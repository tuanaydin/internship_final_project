# STATION_01 Pipeline Extension

## Hedef hiyerarşi

```text
PLANT_01
└── STATION_01
    ├── MOTOR_A
    ├── PUMP_B
    └── VALVE_C
```

## Proses ilişkisi

```text
MOTOR_A --mechanical drive--> PUMP_B --fluid flow--> VALVE_C --> PROCESS_OUT
```

MOTOR_A mevcut elektrik motorudur. PUMP_B motor tarafından tahrik edilen santrifüj pompa,
VALVE_C ise pompa sonrasında yer alan kontrol vanası olarak kurgulanmıştır.

## Veri tasarımı

Her iki yeni veri seti de Motor-A ile aynı zaman eksenini kullanır:

- Dönem: 2026-07-01 00:00 - 2026-07-30 23:55
- Örnekleme: 5 dakika
- Kayıt: 8.640 / varlık
- `operating_state`: Motor-A ile aynı istasyon çalışma/duruş penceresi
- Ortak alanlar: `timestamp`, `device_id`, `operating_state`, `load_pct`,
  `temperature_c`, `vibration_mm_s`, `current_a`, `power_kw`, `energy_kwh_5min`
- Asset-specific alanlar CSV/XLSX içinde ayrıca korunur.

Pump-B:
- `suction_pressure_bar`
- `discharge_pressure_bar`
- `flow_m3_h`
- `differential_pressure_bar`

Valve-C:
- `valve_command_pct`
- `valve_position_pct`
- `position_error_pct`
- `upstream_pressure_bar`
- `downstream_pressure_bar`
- `flow_m3_h`
- `differential_pressure_bar`

## Station-level bağlam için özellikle tasarlanan durumlar

1. Motor-A'nın 12 Temmuz overload penceresinde PUMP_B ve VALVE_C verileri de yüksek proses
   talebini takip eder. Bu, Motor-A olayındaki "proses yükünün yükselmesi" yorumunu destekleyen bağlamdır.
2. Motor-A'nın 27 Temmuz kritik rulman olayında PUMP_B/VALVE_C proses değişkenleri kendi sentetik
   arızaları dışında normal davranır. Bu, motor tarafında lokal mekanik sorun ayrımını göstermeye yarar.
3. Pump-B ve Valve-C kendi bağımsız fiziksel ve data-quality olaylarına sahiptir; aynı istasyonda olmak
   otomatik olarak aynı kök nedeni paylaşmaları anlamına gelmez.

## Mevcut backend ile önemli uyumluluk notu

Mevcut `data_service` yalnızca ortak ham alanları normalize ediyor ve mevcut `SensorMeasurementSchema`
da aynı motor-odaklı alanları expose ediyor. Bu nedenle yeni CSV'ler ortak alanları korur; fakat pompa
basınç/debi ve vana konum/ΔP alanlarını deterministik analiz/API çıktısında tam kullanmak için sonraki
adımda sensör listesini config-driven hale getirmek gerekir.

Önerilen yön:
- `RAW_SENSOR_FIELDS` sabit listesini asset sensor config'inden üretmek.
- `anomaly_service` içindeki sabit `temperature/vibration/current/load` döngüsünü generic evaluator'a çevirmek.
- `diagnostic_service` kurallarını `asset_type` veya diagnostic profile üzerinden seçmek.
- Station-level context için `STATION_01` altındaki varlıkların aynı timestamp penceresini birleştiren
  ayrı bir context service eklemek.
