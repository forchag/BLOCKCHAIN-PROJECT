#include "unity.h"
#include "crt_encode.h"

TEST_CASE("paper worked example reproduces", "[crt]") {
  crt_residue_t r[3]; TEST_ASSERT_EQUAL(ESP_OK, crt_encode(2530, r));
  TEST_ASSERT_EQUAL_UINT8(8, r[0].value); TEST_ASSERT_EQUAL_UINT8(5, r[1].value); TEST_ASSERT_EQUAL_UINT8(58, r[2].value);
}
TEST_CASE("two residue decode needs an admissible bound", "[crt]") {
  crt_residue_t r[3]; uint32_t value=0; TEST_ASSERT_EQUAL(ESP_OK, crt_encode(2530,r));
  TEST_ASSERT_EQUAL(ESP_OK, crt_decode_pair(r, CRT_SAFE_MAX_VALUE, &value)); TEST_ASSERT_EQUAL_UINT32(2530,value);
  TEST_ASSERT_EQUAL(ESP_ERR_INVALID_SIZE, crt_decode_pair(r, CRT_SAFE_MAX_VALUE+1,&value));
}
TEST_CASE("encoder enforces smallest pair product", "[crt]") {
  crt_residue_t r[3]; TEST_ASSERT_EQUAL(ESP_OK,crt_encode(CRT_SAFE_MAX_VALUE-1,r));
  TEST_ASSERT_EQUAL(ESP_ERR_INVALID_SIZE,crt_encode(CRT_SAFE_MAX_VALUE,r));
}
