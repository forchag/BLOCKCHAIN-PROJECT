#pragma once

#include <stdint.h>
#include "esp_err.h"

#define CRT_MODULUS_0 97u
#define CRT_MODULUS_1 101u
#define CRT_MODULUS_2 103u
#define CRT_RESIDUE_COUNT 3u
#define CRT_MAX_VALUE 1009091u
#define CRT_SAFE_MAX_VALUE 9797u

typedef struct { uint8_t index; uint8_t value; } crt_residue_t;

esp_err_t crt_encode(uint32_t reading, crt_residue_t residues[CRT_RESIDUE_COUNT]);
esp_err_t crt_decode_pair(const crt_residue_t residues[2], uint32_t admissible_upper_bound, uint32_t *reading);
uint16_t crt_modulus_for_index(uint8_t index);
