# ESP32 sensor calibration

The reference firmware transmits five scaled quantities as 15 CRT residue packets. Soil moisture and temperature have built-in scaling. Humidity, pH, and light require actual instrument-specific calibration.

## Required ESP-IDF build definitions

Provide these six unsigned integer ADC endpoints at build time using compiler definitions (for example, add `target_compile_definitions(${COMPONENT_LIB} PRIVATE ...)` in `esp32/main/CMakeLists.txt` with measured endpoint values):

| Definition | Physical calibration endpoint |
| --- | --- |
| `HUMIDITY_ADC_DRY` | ADC count at 0% relative humidity |
| `HUMIDITY_ADC_WET` | ADC count at 100% relative humidity |
| `PH_ADC_ZERO` | ADC count at pH 0 |
| `PH_ADC_FOURTEEN` | ADC count at pH 14 |
| `LIGHT_ADC_DARK` | ADC count at 0 lux |
| `LIGHT_ADC_65000_LUX` | ADC count at 65,000 lux |

The current implementation linearly maps each calibrated pair onto 0–1000 (humidity), 0–1400 (pH), or 0–6500 (light) CRT units. These endpoints represent the mathematical mapping; **do not assume the connected sensor is linear or can actually be calibrated at those extremes**. Validate the real sensor transfer function against its datasheet and calibration measurements, and replace this method if the sensor requires a different model.

Each endpoint must be in the ADC range 0–4095, and both endpoints in a pair must differ. Default endpoints are intentionally equal, so the firmware refuses to send records when calibration is absent. No model, coefficient or field measurement is inferred here.

## Hardware and validation requirements

Record the sensor manufacturer, model, electrical interface, wiring, ADC attenuation, reference instrument, calibration date, input/output pairs, and uncertainty before preparing the production build. GPIO39, GPIO32 and GPIO33 are currently read as analog inputs. Digital humidity sensors or specialist pH/light circuits require appropriate drivers, not an assumed raw ADC conversion.

After programming, verify each scaled value against a reference measurement; check both range limits, all 15 packets, gateway reconstruction and failure behavior. The firmware has not yet been proven on the historical deployment hardware.
