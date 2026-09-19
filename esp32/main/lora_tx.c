#include "lora_tx.h"

#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LORA_SPI_HOST SPI2_HOST
#define LORA_PIN_MISO GPIO_NUM_19
#define LORA_PIN_MOSI GPIO_NUM_23
#define LORA_PIN_SCK GPIO_NUM_18
#define LORA_PIN_CS GPIO_NUM_5
#define LORA_PIN_RST GPIO_NUM_14
#define LORA_PIN_DIO0 GPIO_NUM_26
#define REG_FIFO 0x00
#define REG_OP_MODE 0x01
#define REG_FRF_MSB 0x06
#define REG_FRF_MID 0x07
#define REG_FRF_LSB 0x08
#define REG_PA_CONFIG 0x09
#define REG_FIFO_ADDR_PTR 0x0D
#define REG_FIFO_TX_BASE_ADDR 0x0E
#define REG_IRQ_FLAGS 0x12
#define REG_MODEM_CONFIG_1 0x1D
#define REG_MODEM_CONFIG_2 0x1E
#define REG_PREAMBLE_MSB 0x20
#define REG_PREAMBLE_LSB 0x21
#define REG_PAYLOAD_LENGTH 0x22
#define REG_MODEM_CONFIG_3 0x26
#define REG_SYNC_WORD 0x39
#define REG_DIO_MAPPING_1 0x40
#define REG_VERSION 0x42
#define REG_PA_DAC 0x4D
#define MODE_LONG_RANGE_MODE 0x80
#define MODE_SLEEP 0x00
#define MODE_STDBY 0x01
#define MODE_TX 0x03
#define IRQ_TX_DONE_MASK 0x08

static const char *TAG = "lora_tx";
static spi_device_handle_t s_spi;
static int16_t s_link_rssi_dbm = 0;
static const uint32_t s_channels_hz[3] = {868100000u, 868300000u, 868500000u};

_Static_assert(sizeof(lora_packet_t) == LORA_PACKET_LEN, "LoRa payload must be eight bytes");

static esp_err_t write_reg(uint8_t reg, uint8_t value) {
  uint8_t tx[2] = {(uint8_t)(reg | 0x80), value};
  spi_transaction_t t = {.length = 16, .tx_buffer = tx};
  return spi_device_transmit(s_spi, &t);
}
static esp_err_t read_reg(uint8_t reg, uint8_t *value) {
  uint8_t tx[2] = {(uint8_t)(reg & 0x7F), 0}, rx[2] = {0};
  spi_transaction_t t = {.length = 16, .tx_buffer = tx, .rx_buffer = rx};
  esp_err_t err = spi_device_transmit(s_spi, &t); if (err == ESP_OK) *value = rx[1]; return err;
}
static esp_err_t set_frequency(uint32_t hz) {
  const uint64_t frf = ((uint64_t)hz << 19) / 32000000ULL;
  ESP_RETURN_ON_ERROR(write_reg(REG_FRF_MSB, (uint8_t)(frf >> 16)), TAG, "frf msb");
  ESP_RETURN_ON_ERROR(write_reg(REG_FRF_MID, (uint8_t)(frf >> 8)), TAG, "frf mid");
  return write_reg(REG_FRF_LSB, (uint8_t)frf);
}
static esp_err_t apply_tx_power(void) {
  if (s_link_rssi_dbm != 0 && s_link_rssi_dbm < LORA_RSSI_BOOST_THRESHOLD_DBM) {
    ESP_RETURN_ON_ERROR(write_reg(REG_PA_DAC, 0x87), TAG, "20 dBm PA DAC");
    return write_reg(REG_PA_CONFIG, 0x8F);
  }
  ESP_RETURN_ON_ERROR(write_reg(REG_PA_DAC, 0x84), TAG, "normal PA DAC");
  return write_reg(REG_PA_CONFIG, 0x8C); /* PA_BOOST, +14 dBm */
}
esp_err_t lora_set_link_rssi(int16_t rssi_dbm) { s_link_rssi_dbm = rssi_dbm; return apply_tx_power(); }

esp_err_t lora_init(void) {
  spi_bus_config_t bus = {.miso_io_num=LORA_PIN_MISO,.mosi_io_num=LORA_PIN_MOSI,.sclk_io_num=LORA_PIN_SCK,.quadwp_io_num=-1,.quadhd_io_num=-1};
  esp_err_t err=spi_bus_initialize(LORA_SPI_HOST,&bus,SPI_DMA_CH_AUTO); if(err!=ESP_OK&&err!=ESP_ERR_INVALID_STATE)return err;
  spi_device_interface_config_t dev={.clock_speed_hz=8000000,.mode=0,.spics_io_num=LORA_PIN_CS,.queue_size=1};
  err=spi_bus_add_device(LORA_SPI_HOST,&dev,&s_spi); if(err!=ESP_OK&&err!=ESP_ERR_INVALID_STATE)return err;
  gpio_set_direction(LORA_PIN_RST,GPIO_MODE_OUTPUT); gpio_set_level(LORA_PIN_RST,0); vTaskDelay(pdMS_TO_TICKS(10)); gpio_set_level(LORA_PIN_RST,1); vTaskDelay(pdMS_TO_TICKS(10));
  gpio_set_direction(LORA_PIN_DIO0,GPIO_MODE_INPUT);
  uint8_t version=0; ESP_RETURN_ON_ERROR(read_reg(REG_VERSION,&version),TAG,"version");
  ESP_RETURN_ON_ERROR(write_reg(REG_OP_MODE,MODE_LONG_RANGE_MODE|MODE_SLEEP),TAG,"sleep");
  ESP_RETURN_ON_ERROR(set_frequency(s_channels_hz[0]),TAG,"frequency");
  ESP_RETURN_ON_ERROR(write_reg(REG_FIFO_TX_BASE_ADDR,0),TAG,"tx base");
  ESP_RETURN_ON_ERROR(write_reg(REG_MODEM_CONFIG_1,0x72),TAG,"BW125 CR4/5 explicit");
  ESP_RETURN_ON_ERROR(write_reg(REG_MODEM_CONFIG_2,0x94),TAG,"SF9 CRC on");
  ESP_RETURN_ON_ERROR(write_reg(REG_MODEM_CONFIG_3,0x04),TAG,"AGC");
  ESP_RETURN_ON_ERROR(write_reg(REG_PREAMBLE_MSB,0),TAG,"preamble");
  ESP_RETURN_ON_ERROR(write_reg(REG_PREAMBLE_LSB,8),TAG,"preamble");
  ESP_RETURN_ON_ERROR(write_reg(REG_PAYLOAD_LENGTH,LORA_PACKET_LEN),TAG,"payload");
  ESP_RETURN_ON_ERROR(write_reg(REG_SYNC_WORD,0x34),TAG,"sync");
  ESP_RETURN_ON_ERROR(apply_tx_power(),TAG,"default +14 dBm");
  return write_reg(REG_OP_MODE,MODE_LONG_RANGE_MODE|MODE_STDBY);
}
static esp_err_t transmit_packet(const lora_packet_t *packet, uint32_t channel) {
  ESP_RETURN_ON_ERROR(write_reg(REG_OP_MODE,MODE_LONG_RANGE_MODE|MODE_STDBY),TAG,"standby");
  ESP_RETURN_ON_ERROR(set_frequency(channel),TAG,"frequency");
  ESP_RETURN_ON_ERROR(apply_tx_power(),TAG,"tx power");
  ESP_RETURN_ON_ERROR(write_reg(REG_IRQ_FLAGS,0xFF),TAG,"irq");
  ESP_RETURN_ON_ERROR(write_reg(REG_DIO_MAPPING_1,0x40),TAG,"dio");
  ESP_RETURN_ON_ERROR(write_reg(REG_FIFO_ADDR_PTR,0),TAG,"fifo");
  const uint8_t *bytes=(const uint8_t *)packet;
  for(size_t i=0;i<sizeof(*packet);++i) ESP_RETURN_ON_ERROR(write_reg(REG_FIFO,bytes[i]),TAG,"fifo write");
  ESP_RETURN_ON_ERROR(write_reg(REG_PAYLOAD_LENGTH,sizeof(*packet)),TAG,"length");
  ESP_RETURN_ON_ERROR(write_reg(REG_OP_MODE,MODE_LONG_RANGE_MODE|MODE_TX),TAG,"tx");
  const int64_t deadline=esp_timer_get_time()+2000000LL;
  while(esp_timer_get_time()<deadline){uint8_t flags=0;ESP_RETURN_ON_ERROR(read_reg(REG_IRQ_FLAGS,&flags),TAG,"irq");if(flags&IRQ_TX_DONE_MASK){write_reg(REG_IRQ_FLAGS,IRQ_TX_DONE_MASK);return write_reg(REG_OP_MODE,MODE_LONG_RANGE_MODE|MODE_STDBY);}vTaskDelay(pdMS_TO_TICKS(10));}
  return ESP_ERR_TIMEOUT;
}
esp_err_t lora_transmit_quantity_residues(uint16_t node_id,uint32_t reading_id,uint8_t quantity_id,const uint8_t values[3]) {
  if(values==NULL||quantity_id>15)return ESP_ERR_INVALID_ARG;
  for(uint8_t i=0;i<3;++i){lora_packet_t packet={.node_id=node_id,.reading_id=reading_id,.quantity_residue=(uint8_t)((quantity_id<<4)|i),.residue_value=values[i]};ESP_RETURN_ON_ERROR(transmit_packet(&packet,s_channels_hz[i]),TAG,"transmit residue");}
  return ESP_OK;
}
