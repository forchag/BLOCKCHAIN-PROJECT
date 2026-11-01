#include <inttypes.h>
#include <string.h>
#include <time.h>

#include "cert_store.h"
#include "crt_encode.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_random.h"
#include "esp_sleep.h"
#include "esp_sntp.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "lora_tx.h"
#include "nvs_flash.h"
#include "sensor.h"

#define SNTP_TIMEOUT_MS 10000u
#define SLEEP_CYCLE_US (30ULL * 60ULL * 1000000ULL)
#define MIN_SLEEP_US (5ULL * 1000000ULL)
#define QUANTITY_SOIL 0u
#define QUANTITY_TEMPERATURE 1u
#define QUANTITY_COUNT 5u
#define PACKETS_PER_READING (QUANTITY_COUNT * CRT_RESIDUE_COUNT)

#ifndef HUMIDITY_ADC_DRY
#define HUMIDITY_ADC_DRY 0u
#endif
#ifndef HUMIDITY_ADC_WET
#define HUMIDITY_ADC_WET 0u
#endif
#ifndef PH_ADC_ZERO
#define PH_ADC_ZERO 0u
#endif
#ifndef PH_ADC_FOURTEEN
#define PH_ADC_FOURTEEN 0u
#endif
#ifndef LIGHT_ADC_DARK
#define LIGHT_ADC_DARK 0u
#endif
#ifndef LIGHT_ADC_65000_LUX
#define LIGHT_ADC_65000_LUX 0u
#endif

static const char *TAG = "main";

/* Two-point sensor calibration maps physical endpoints into documented CRT units. */
static esp_err_t scale_adc(uint16_t raw, uint32_t at_zero, uint32_t at_max,
                           uint32_t encoded_max, uint32_t *out) {
  if (out == NULL || at_zero == at_max || at_zero > 4095u || at_max > 4095u)
    return ESP_ERR_INVALID_STATE;
  const int32_t numerator = ((int32_t)raw - (int32_t)at_zero) * (int32_t)encoded_max;
  const int32_t denominator = (int32_t)at_max - (int32_t)at_zero;
  const int32_t value = numerator / denominator;
  if (value < 0 || value > (int32_t)encoded_max) return ESP_ERR_INVALID_SIZE;
  *out = (uint32_t)value;
  return ESP_OK;
}

static uint16_t node_id_from_mac(void) {
  uint8_t mac[6]; ESP_ERROR_CHECK(esp_read_mac(mac, ESP_MAC_WIFI_STA));
  uint16_t id = 0; memcpy(&id, &mac[4], sizeof(id)); return id;
}
static bool sync_time(void) {
  esp_sntp_setoperatingmode(SNTP_OPMODE_POLL); esp_sntp_setservername(0,"pool.ntp.org"); esp_sntp_init();
  const int64_t deadline=esp_timer_get_time()+SNTP_TIMEOUT_MS*1000LL;
  while(esp_timer_get_time()<deadline){if(esp_sntp_get_sync_status()==SNTP_SYNC_STATUS_COMPLETED)return true;vTaskDelay(pdMS_TO_TICKS(250));}
  return false;
}
static uint32_t scale_soil(uint16_t raw) {
  if (raw > 4095) raw = 4095;
  return ((uint32_t)raw * 1000u + 2047u) / 4095u; /* 0.1 percent VWC */
}
static uint32_t scale_temperature(int16_t centi_c) {
  int32_t deci_offset = ((int32_t)centi_c + 4000 + 5) / 10; /* -40 C maps to zero */
  if (deci_offset < 0) deci_offset = 0;
  if (deci_offset > 1250) deci_offset = 1250;
  return (uint32_t)deci_offset;
}
static void transmit_quantity(uint16_t node_id,uint32_t reading_id,uint8_t quantity,uint32_t value){
  crt_residue_t residues[3]; ESP_ERROR_CHECK(crt_encode(value,residues));
  uint8_t values[3]={residues[0].value,residues[1].value,residues[2].value};
  ESP_ERROR_CHECK(lora_transmit_quantity_residues(node_id,reading_id,quantity,values));
}
void app_main(void) {
  esp_err_t err=nvs_flash_init(); if(err==ESP_ERR_NVS_NO_FREE_PAGES||err==ESP_ERR_NVS_NEW_VERSION_FOUND){ESP_ERROR_CHECK(nvs_flash_erase());err=nvs_flash_init();} ESP_ERROR_CHECK(err);
  ESP_ERROR_CHECK(esp_netif_init()); ESP_ERROR_CHECK(esp_event_loop_create_default());
  const bool time_synced=sync_time(); time_t now=0; if(time_synced){time(&now);if(cert_store_is_expired(now)){ESP_LOGW(TAG,"certificate expired; enrollment required");esp_deep_sleep(MIN_SLEEP_US);}}
  ESP_ERROR_CHECK(sensor_init()); ESP_ERROR_CHECK(lora_init());
  sensor_reading_t reading={0}; ESP_ERROR_CHECK(sensor_read(&reading));
  const uint16_t node_id=node_id_from_mac(); const uint32_t reading_id=esp_random();
  uint32_t quantities[QUANTITY_COUNT] = {
      scale_soil(reading.soil_moisture_raw),
      scale_temperature(reading.temperature_centi_c), 0, 0, 0,
  };
  /* Do not label raw ADC counts as humidity, pH or illuminance. */
  err = scale_adc(reading.aux_adc_raw[0], HUMIDITY_ADC_DRY,
                  HUMIDITY_ADC_WET, 1000u, &quantities[2]);
  if (err == ESP_OK) err = scale_adc(reading.aux_adc_raw[1], PH_ADC_ZERO,
                  PH_ADC_FOURTEEN, 1400u, &quantities[3]);
  if (err == ESP_OK) err = scale_adc(reading.aux_adc_raw[2], LIGHT_ADC_DARK,
                  LIGHT_ADC_65000_LUX, 6500u, &quantities[4]);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "Humidity, pH and light calibration required; no invalid CRT records sent");
    esp_deep_sleep(MIN_SLEEP_US);
  }
  for (uint8_t quantity = 0; quantity < QUANTITY_COUNT; ++quantity) {
    transmit_quantity(node_id, reading_id, quantity, quantities[quantity]);
  }
  ESP_LOGI(TAG, "sent %u measured quantities as %u unsigned 8-byte LoRa packets",
           (unsigned)QUANTITY_COUNT, (unsigned)PACKETS_PER_READING);
  esp_deep_sleep(SLEEP_CYCLE_US < MIN_SLEEP_US ? MIN_SLEEP_US : SLEEP_CYCLE_US);
}
