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

static const char *TAG = "main";

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
  transmit_quantity(node_id,reading_id,QUANTITY_SOIL,scale_soil(reading.soil_moisture_raw));
  transmit_quantity(node_id,reading_id,QUANTITY_TEMPERATURE,scale_temperature(reading.temperature_centi_c));
  ESP_LOGI(TAG,"sent two measured quantities as six unsigned 8-byte LoRa packets; gateway signing follows reconstruction");
  esp_deep_sleep(SLEEP_CYCLE_US < MIN_SLEEP_US ? MIN_SLEEP_US : SLEEP_CYCLE_US);
}
