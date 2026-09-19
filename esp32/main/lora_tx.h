#pragma once

#include <stdint.h>
#include "esp_err.h"

#define LORA_PACKET_LEN 8u
#define LORA_CHANNEL_COUNT 3u
#define LORA_RSSI_BOOST_THRESHOLD_DBM (-120)

typedef struct __attribute__((packed)) {
  uint16_t node_id;
  uint32_t reading_id;
  uint8_t quantity_residue; /* high nibble quantity, low two bits residue */
  uint8_t residue_value;
} lora_packet_t;

esp_err_t lora_init(void);
esp_err_t lora_set_link_rssi(int16_t rssi_dbm);
esp_err_t lora_transmit_quantity_residues(uint16_t node_id, uint32_t reading_id,
    uint8_t quantity_id, const uint8_t residue_values[LORA_CHANNEL_COUNT]);
