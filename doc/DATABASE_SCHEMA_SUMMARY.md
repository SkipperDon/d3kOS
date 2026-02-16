# d3kOS Central Database Schema Summary

**Version:** 1.0
**Date:** 2026-02-16
**Database Engine:** MySQL/MariaDB (InnoDB)

---

## Overview

The central database receives exported data from all d3kOS installations (Tier 1, 2, and 3 only). The schema consists of **17 tables** organized into:

- **2 Master Tables** - Installation registry and export tracking
- **8 Data Category Tables** - One per export category (1-8)
- **5 Telemetry Tables** - Analytics and performance metrics (category 9)
- **3 Analytics Views** - Pre-built queries for reporting

---

## Master Tables

### 1. `installations`
**Purpose:** Master registry of all d3kOS systems

| Column | Type | Description |
|--------|------|-------------|
| installation_id | VARCHAR(16) PK | Unique system ID (16-char hex hash) |
| tier | TINYINT | 0=Free, 1=Free+App, 2=Paid, 3=Enterprise |
| boat_manufacturer | VARCHAR(100) | From onboarding |
| boat_year | INT | From onboarding |
| boat_model | VARCHAR(100) | From onboarding |
| engine_make | VARCHAR(100) | From onboarding |
| engine_model | VARCHAR(100) | From onboarding |
| engine_year | INT | From onboarding |
| created_at | TIMESTAMP | When installation was first created |
| first_export_at | TIMESTAMP | When first data export received |
| last_export_at | TIMESTAMP | When most recent export received |
| total_exports | INT | Count of all exports from this system |
| is_active | BOOLEAN | System still active/reporting |
| last_boot_at | TIMESTAMP | Last system boot time |
| software_version | VARCHAR(20) | d3kOS version |

**Indexes:** tier, is_active, last_export_at

---

### 2. `export_history`
**Purpose:** Track all data imports from d3kOS systems

| Column | Type | Description |
|--------|------|-------------|
| export_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | Which d3kOS system |
| export_timestamp | TIMESTAMP | When export was created on d3kOS |
| import_timestamp | TIMESTAMP | When received by central server |
| tier | TINYINT | System tier at export time |
| format_version | VARCHAR(10) | Export format version (e.g., "1.0") |
| engine_benchmarks_count | INT | Records in category 1 |
| boatlog_entries_count | INT | Records in category 2 |
| marine_vision_captures_count | INT | Records in category 3 |
| marine_vision_snapshots_count | INT | Records in category 4 |
| qr_codes_count | INT | Records in category 5 |
| settings_count | INT | Records in category 6 |
| alerts_count | INT | Records in category 7 |
| onboarding_count | INT | Records in category 8 |
| telemetry_count | INT | Records in category 9 |
| total_records | INT | Sum of all categories |
| file_size_bytes | BIGINT | Size of export JSON file |
| processing_time_ms | INT | Server processing time |

**Indexes:** installation_id, export_timestamp, import_timestamp

---

## Category 1: Engine Benchmarks

### 3. `engine_benchmarks`
**Purpose:** Baseline engine performance metrics

| Column | Type | Description |
|--------|------|-------------|
| benchmark_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| created_at | TIMESTAMP | When benchmark was created |
| baseline_rpm | DECIMAL(7,2) | Baseline RPM value |
| baseline_oil_pressure_psi | DECIMAL(5,2) | Baseline oil pressure |
| baseline_coolant_temp_f | DECIMAL(5,2) | Baseline coolant temp |
| baseline_boost_pressure_psi | DECIMAL(5,2) | Baseline boost pressure |
| baseline_fuel_pressure_psi | DECIMAL(5,2) | Baseline fuel pressure |
| rpm_idle | INT | Idle RPM threshold |
| rpm_max | INT | Max RPM threshold |
| oil_pressure_min_psi | DECIMAL(5,2) | Min oil pressure threshold |
| oil_pressure_max_psi | DECIMAL(5,2) | Max oil pressure threshold |
| coolant_temp_min_f | DECIMAL(5,2) | Min coolant temp threshold |
| coolant_temp_max_f | DECIMAL(5,2) | Max coolant temp threshold |
| engine_hours_at_benchmark | DECIMAL(10,2) | Engine hours when benchmark taken |
| conditions | TEXT | Operating conditions notes |

**Indexes:** installation_id, created_at

---

## Category 2: Boatlog Entries

### 4. `boatlog_entries`
**Purpose:** All boatlog entries (voice, text, auto, weather)

| Column | Type | Description |
|--------|------|-------------|
| entry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| entry_timestamp | TIMESTAMP | When log entry was created |
| entry_type | ENUM | 'voice', 'text', 'auto', 'weather' |
| entry_text | TEXT | Log entry content |
| latitude | DECIMAL(10,7) | GPS latitude |
| longitude | DECIMAL(10,7) | GPS longitude |
| voice_duration_seconds | INT | Voice recording length (if voice) |
| voice_file_size_bytes | BIGINT | Voice file size (if voice) |
| trigger_event | VARCHAR(100) | What triggered auto-log (if auto) |
| weather_temp_f | DECIMAL(5,2) | Temperature (if weather) |
| weather_wind_speed_knots | DECIMAL(5,2) | Wind speed (if weather) |
| weather_wind_direction_deg | INT | Wind direction 0-360 (if weather) |
| weather_wave_height_ft | DECIMAL(4,2) | Wave height (if weather) |
| weather_conditions | VARCHAR(100) | Weather description (if weather) |
| engine_hours | DECIMAL(10,2) | Engine hours at log time |
| rpm | INT | RPM at log time |

**Indexes:** installation_id, entry_timestamp, entry_type, location (lat/lon)

---

## Category 3: Marine Vision Captures (Metadata Only)

### 5. `marine_vision_captures`
**Purpose:** Fish capture photo metadata (files transferred via mobile app)

| Column | Type | Description |
|--------|------|-------------|
| capture_id | VARCHAR(50) PK | UUID from d3kOS |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| capture_timestamp | TIMESTAMP | When photo was taken |
| file_size_bytes | BIGINT | Photo file size |
| file_path_local | VARCHAR(500) | Path on d3kOS system |
| file_transferred | BOOLEAN | Has user downloaded via mobile app? |
| file_transferred_at | TIMESTAMP | When file was transferred |
| species | VARCHAR(100) | Detected fish species |
| confidence | DECIMAL(5,4) | AI confidence (0.0000 to 1.0000) |
| latitude | DECIMAL(10,7) | GPS latitude |
| longitude | DECIMAL(10,7) | GPS longitude |
| location_name | VARCHAR(200) | Lake/ocean name |
| person_detected | BOOLEAN | Person holding fish detected? |
| fish_detected | BOOLEAN | Fish detected? |
| detection_classes | TEXT | JSON array of all detected objects |

**Indexes:** installation_id, capture_timestamp, species, location, file_transferred

**Note:** Actual photo files NOT stored in database. Files remain on d3kOS and are transferred via mobile app.

---

## Category 4: Marine Vision Snapshots (Metadata Only)

### 6. `marine_vision_snapshots`
**Purpose:** Forward watch video/snapshot metadata (files transferred via mobile app)

| Column | Type | Description |
|--------|------|-------------|
| snapshot_id | VARCHAR(50) PK | UUID from d3kOS |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| snapshot_timestamp | TIMESTAMP | When video/snapshot was taken |
| file_size_bytes | BIGINT | Video file size |
| file_path_local | VARCHAR(500) | Path on d3kOS system |
| file_transferred | BOOLEAN | Has user downloaded via mobile app? |
| file_transferred_at | TIMESTAMP | When file was transferred |
| orientation | VARCHAR(20) | 'forward_watch', 'fish_capture', 'manual' |
| camera_angle_degrees | INT | Camera angle 0-360 |
| detections_count | INT | Number of objects detected |
| detection_types | TEXT | JSON array: ["boat", "kayak", "buoy"] |
| latitude | DECIMAL(10,7) | GPS latitude |
| longitude | DECIMAL(10,7) | GPS longitude |
| alert_triggered | BOOLEAN | Did detection trigger alert? |
| alert_type | VARCHAR(50) | 'proximity', 'collision_risk', etc. |
| closest_object_distance_meters | DECIMAL(7,2) | Distance to nearest object |

**Indexes:** installation_id, snapshot_timestamp, orientation, alert_triggered, file_transferred

**Note:** Actual video files NOT stored in database. Files remain on d3kOS and are transferred via mobile app.

---

## Category 5: QR Codes

### 7. `qr_codes`
**Purpose:** QR code generation and mobile app pairing tracking

| Column | Type | Description |
|--------|------|-------------|
| qr_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| generated_at | TIMESTAMP | When QR code was generated |
| installation_uuid | VARCHAR(36) | UUID format for mobile app |
| pairing_token | VARCHAR(100) | One-time use pairing token |
| current_tier | TINYINT | Tier at QR generation time |
| pairing_completed | BOOLEAN | Has mobile app paired? |
| paired_at | TIMESTAMP | When pairing completed |
| mobile_app_version | VARCHAR(20) | Mobile app version used |

**Indexes:** installation_id, installation_uuid, pairing_token

---

## Category 6: Settings Configurations

### 8. `settings_configurations`
**Purpose:** System settings and user preferences

| Column | Type | Description |
|--------|------|-------------|
| config_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| saved_at | TIMESTAMP | When settings were saved |
| language | VARCHAR(10) | UI language (default: 'en') |
| units_system | ENUM | 'metric' or 'imperial' |
| timezone | VARCHAR(50) | System timezone |
| screen_brightness | TINYINT | 0-100 |
| auto_dimming | BOOLEAN | Auto-dim enabled? |
| night_mode | BOOLEAN | Night mode enabled? |
| alerts_enabled | BOOLEAN | System alerts enabled? |
| voice_alerts | BOOLEAN | Voice alerts enabled? |
| email_notifications | BOOLEAN | Email notifications enabled? |
| email_address | VARCHAR(255) | Notification email address |
| threshold_rpm_low | INT | Low RPM alert threshold |
| threshold_rpm_high | INT | High RPM alert threshold |
| threshold_oil_pressure_low | DECIMAL(5,2) | Low oil pressure threshold |
| threshold_coolant_temp_high | DECIMAL(5,2) | High coolant temp threshold |
| wifi_ssid | VARCHAR(100) | WiFi network name |
| wifi_enabled | BOOLEAN | WiFi enabled? |
| hotspot_enabled | BOOLEAN | Hotspot mode enabled? |
| telemetry_enabled | BOOLEAN | Telemetry collection enabled? (Tier 1+) |
| data_sharing_consent | BOOLEAN | User consent for data sharing |
| full_config_json | JSON | Complete settings backup |

**Indexes:** installation_id, saved_at

---

## Category 7: System Alerts

### 9. `system_alerts`
**Purpose:** Health monitoring alerts and anomaly detection

| Column | Type | Description |
|--------|------|-------------|
| alert_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| alert_timestamp | TIMESTAMP | When alert was triggered |
| alert_type | ENUM | 'health', 'anomaly', 'system', 'critical' |
| alert_category | VARCHAR(50) | 'engine', 'network', 'storage', etc. |
| severity | ENUM | 'low', 'medium', 'high', 'critical' |
| alert_title | VARCHAR(200) | Alert title/summary |
| alert_message | TEXT | Detailed alert message |
| resolved | BOOLEAN | Has alert been resolved? |
| resolved_at | TIMESTAMP | When alert was resolved |
| resolution_notes | TEXT | Resolution details |
| auto_resolved | BOOLEAN | Auto-resolved by system? |
| sensor_value | DECIMAL(10,2) | Actual sensor reading |
| threshold_value | DECIMAL(10,2) | Threshold that was exceeded |
| engine_hours | DECIMAL(10,2) | Engine hours at alert time |
| latitude | DECIMAL(10,7) | GPS latitude (if applicable) |
| longitude | DECIMAL(10,7) | GPS longitude (if applicable) |

**Indexes:** installation_id, alert_timestamp, alert_type, severity, resolved

---

## Category 8: Onboarding/Initial Setup Configurations

### 10. `onboarding_configurations`
**Purpose:** Wizard answers for Tier 1 config restore after image update

| Column | Type | Description |
|--------|------|-------------|
| config_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| completed | BOOLEAN | Wizard completed? |
| completion_timestamp | TIMESTAMP | When wizard was completed |
| reset_count | INT | Number of resets used |
| max_resets | INT | Max resets allowed (10 for Tier 0/1) |
| resets_remaining | INT | Calculated: max_resets - reset_count |
| last_reset_timestamp | TIMESTAMP | When last reset occurred |
| boat_manufacturer | VARCHAR(100) | Step 1 answer |
| boat_year | INT | Step 2 answer |
| boat_model | VARCHAR(100) | Step 3 answer |
| chartplotter | VARCHAR(100) | Step 4 answer |
| engine_make | VARCHAR(100) | Step 5 answer |
| engine_model | VARCHAR(100) | Step 6 answer |
| engine_year | INT | Step 7 answer |
| engine_cylinders | TINYINT | Step 8 answer |
| engine_displacement_liters | DECIMAL(4,1) | Step 9 answer |
| engine_power_hp | INT | Step 10 answer |
| engine_compression_ratio | VARCHAR(10) | Step 11 answer |
| engine_idle_rpm | INT | Step 12 answer |
| engine_max_rpm | INT | Step 13 answer |
| engine_fuel_type | VARCHAR(50) | Step 14 answer |
| regional_origin | VARCHAR(100) | Step 15 answer |
| engine_position | VARCHAR(50) | Step 16 answer (port/starboard/center) |
| wizard_answers_json | JSON | Complete wizard backup |

**Indexes:** installation_id, completed, boat_manufacturer, engine_make

**Use Case:** Tier 1 mobile app retrieves this data to restore configuration after d3kOS image update

---

## Category 9: Telemetry & Analytics (5 Sub-tables)

### 11. `telemetry_system_performance`
**Purpose:** System performance metrics (boot time, RAM, CPU, network, storage)

| Column | Type | Description |
|--------|------|-------------|
| telemetry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| collection_start | TIMESTAMP | Metrics period start |
| collection_end | TIMESTAMP | Metrics period end |
| collection_duration_hours | DECIMAL(6,2) | Period duration |
| boot_time_seconds | DECIMAL(6,2) | System boot time |
| uptime_hours | DECIMAL(10,2) | Total uptime |
| reboot_count | INT | Number of reboots |
| average_ram_usage_mb | INT | Average RAM usage |
| peak_ram_usage_mb | INT | Peak RAM usage |
| average_cpu_load | DECIMAL(4,2) | Average CPU load |
| peak_cpu_load | DECIMAL(4,2) | Peak CPU load |
| average_network_latency_ms | INT | Network latency |
| network_errors_count | INT | Network errors |
| storage_used_gb | DECIMAL(7,2) | Storage used |
| storage_total_gb | DECIMAL(7,2) | Total storage |
| storage_percent_used | TINYINT | Storage % used |
| battery_health_percent | TINYINT | Battery health (Tier 3) |
| average_battery_voltage | DECIMAL(4,2) | Battery voltage (Tier 3) |
| service_restarts_json | JSON | {"d3kos-voice": 0, ...} |
| error_counts_json | JSON | {"camera": 5, "gps": 12} |

**Indexes:** installation_id, collection_start/end

---

### 12. `telemetry_user_interaction`
**Purpose:** User behavior and feature usage metrics

| Column | Type | Description |
|--------|------|-------------|
| telemetry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| collection_start | TIMESTAMP | Metrics period start |
| collection_end | TIMESTAMP | Metrics period end |
| collection_duration_hours | DECIMAL(6,2) | Period duration |
| menu_clicks_json | JSON | {"dashboard": 45, "ai_assistant": 18} |
| voice_commands_count | INT | Total voice commands |
| ai_queries_count | INT | Total AI queries |
| camera_captures_count | INT | Total camera captures |
| boatlog_entries_count | INT | Total boatlog entries |
| common_flows_json | JSON | [["dashboard", "engine", "settings"]] |
| abandoned_actions_count | INT | Incomplete actions |
| abandoned_actions_json | JSON | {"onboarding_step_5": 2} |
| settings_changes_count | INT | Settings modifications |
| voice_command_success_rate | DECIMAL(5,2) | % successful voice commands |
| touchscreen_inputs_count | INT | Touchscreen interactions |
| keyboard_inputs_count | INT | Keyboard interactions |

**Indexes:** installation_id, collection_start/end

---

### 13. `telemetry_ai_assistance`
**Purpose:** AI assistant performance and usage metrics

| Column | Type | Description |
|--------|------|-------------|
| telemetry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| collection_start | TIMESTAMP | Metrics period start |
| collection_end | TIMESTAMP | Metrics period end |
| collection_duration_hours | DECIMAL(6,2) | Period duration |
| total_queries_count | INT | Total AI queries |
| simple_queries_count | INT | Simple rule-based queries |
| complex_queries_count | INT | Complex online queries |
| average_response_time_ms | INT | Average response time |
| median_response_time_ms | INT | Median response time |
| p95_response_time_ms | INT | 95th percentile response time |
| query_types_json | JSON | {"rpm": 15, "fuel": 8, "help": 3} |
| provider_usage_json | JSON | {"auto": 20, "online": 5, "onboard": 10} |
| cache_hit_rate | DECIMAL(5,2) | % cache hits |
| cache_hits_count | INT | Cache hits |
| cache_misses_count | INT | Cache misses |
| abandoned_queries_count | INT | User didn't wait for response |

**Indexes:** installation_id, collection_start/end

---

### 14. `telemetry_device_environment`
**Purpose:** Connected devices and environmental usage patterns

| Column | Type | Description |
|--------|------|-------------|
| telemetry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| collection_start | TIMESTAMP | Metrics period start |
| collection_end | TIMESTAMP | Metrics period end |
| collection_duration_hours | DECIMAL(6,2) | Period duration |
| camera_connected | BOOLEAN | Camera status |
| camera_uptime_percent | DECIMAL(5,2) | Camera availability % |
| gps_connected | BOOLEAN | GPS status |
| ais_connected | BOOLEAN | AIS status |
| chartplotter_connected | BOOLEAN | Chartplotter status |
| hardware_model | VARCHAR(50) | "Raspberry Pi 4B" |
| ram_total_mb | INT | Total RAM |
| cpu_cores | TINYINT | CPU core count |
| network_mode | VARCHAR(20) | "wifi", "cellular", "offline" |
| network_uptime_percent | DECIMAL(5,2) | Network availability % |
| time_of_day_usage_json | JSON | {"morning": 20, "afternoon": 45} |
| day_of_week_usage_json | JSON | {"monday": 5, "saturday": 25} |

**Indexes:** installation_id, collection_start/end

---

### 15. `telemetry_business_intelligence`
**Purpose:** Retention, engagement, and tier tracking metrics

| Column | Type | Description |
|--------|------|-------------|
| telemetry_id | BIGINT PK | Auto-increment ID |
| installation_id | VARCHAR(16) FK | System ID |
| export_id | BIGINT FK | Which export batch |
| collection_start | TIMESTAMP | Metrics period start |
| collection_end | TIMESTAMP | Metrics period end |
| collection_duration_hours | DECIMAL(6,2) | Period duration |
| days_since_installation | INT | Installation age |
| daily_active_usage | BOOLEAN | User opened UI today? |
| sessions_this_week | INT | Number of sessions |
| average_session_duration_minutes | DECIMAL(6,2) | Avg session length |
| current_tier | TINYINT | Current tier level |
| tier_upgrades_count | INT | Number of upgrades |
| last_tier_upgrade_at | TIMESTAMP | When last upgraded |
| features_used_json | JSON | {"voice": true, "ai": true, "camera": false} |
| weekly_active_user | BOOLEAN | Active last 7 days? |
| monthly_active_user | BOOLEAN | Active last 30 days? |

**Indexes:** installation_id, collection_start/end, tier, weekly/monthly active flags

---

## Analytics Views

### 16. `v_active_installations` (VIEW)
**Purpose:** Summary of active installations by tier

```sql
SELECT tier, total_installations, active_installations, active_last_7_days
FROM v_active_installations;
```

| Column | Description |
|--------|-------------|
| tier | 0, 1, 2, or 3 |
| total_installations | All installations at this tier |
| active_installations | Currently active systems |
| active_last_7_days | Exported data in last 7 days |

---

### 17. `v_export_activity` (VIEW)
**Purpose:** Daily export activity summary (last 30 days)

```sql
SELECT export_date, total_exports, total_records, avg_processing_time_ms
FROM v_export_activity;
```

| Column | Description |
|--------|-------------|
| export_date | Date of exports |
| total_exports | Number of exports received |
| total_records | Total records imported |
| avg_processing_time_ms | Average server processing time |
| total_bytes | Total data volume |

---

### 18. `v_fleet_overview` (VIEW)
**Purpose:** Fleet breakdown by boat/engine manufacturer

```sql
SELECT boat_manufacturer, engine_make, installation_count, avg_engine_year
FROM v_fleet_overview;
```

| Column | Description |
|--------|-------------|
| boat_manufacturer | Boat manufacturer |
| engine_make | Engine manufacturer |
| installation_count | Number of installations |
| avg_engine_year | Average engine year |
| active_count | Currently active systems |

---

## Key Relationships

```
installations (1) ───→ (N) export_history
                 ├───→ (N) engine_benchmarks
                 ├───→ (N) boatlog_entries
                 ├───→ (N) marine_vision_captures
                 ├───→ (N) marine_vision_snapshots
                 ├───→ (N) qr_codes
                 ├───→ (N) settings_configurations
                 ├───→ (N) system_alerts
                 ├───→ (N) onboarding_configurations
                 ├───→ (N) telemetry_system_performance
                 ├───→ (N) telemetry_user_interaction
                 ├───→ (N) telemetry_ai_assistance
                 ├───→ (N) telemetry_device_environment
                 └───→ (N) telemetry_business_intelligence

export_history (1) ───→ (N) all data tables
```

---

## Storage Estimates

Based on typical d3kOS usage:

| Table | Records/Day | Record Size | Daily Growth |
|-------|-------------|-------------|--------------|
| boatlog_entries | 10-50 | ~500 bytes | 5-25 KB |
| system_alerts | 0-5 | ~300 bytes | 0-1.5 KB |
| marine_vision_captures | 5-20 | ~200 bytes | 1-4 KB |
| telemetry_* (5 tables) | 1 each | ~500 bytes | 2.5 KB |
| **Total per installation** | | | **~10-35 KB/day** |

**For 1,000 installations:**
- Daily: ~10-35 MB
- Monthly: ~300 MB - 1 GB
- Yearly: ~3.6-12.8 GB

*Note: Marine vision media files NOT included (stored on d3kOS, transferred via mobile app)*

---

## Privacy & Data Retention

- **Telemetry:** Tier 1+ only, user consent required, anonymized (no PII)
- **GPS Coordinates:** Stored for boatlog, captures, snapshots, alerts (user data)
- **Media Files:** NOT stored in database (metadata only)
- **Retention:** Recommend 2-year retention for analytics, longer for fleet/warranty data
- **Anonymization:** installation_id is pseudonymous (no personal names/addresses)

---

## Implementation Notes

1. **JSON Columns:** Used for flexible/complex data (query_types, menu_clicks, etc.)
2. **DECIMAL Types:** Used for precise values (money, coordinates, percentages)
3. **ENUM Types:** Used for fixed value sets (better performance than VARCHAR)
4. **Foreign Keys:** Enforce referential integrity (all data tied to valid installation)
5. **Indexes:** Optimized for common queries (by installation, by date, by type)
6. **InnoDB Engine:** ACID compliance, transaction support, foreign key support
7. **UTF8MB4:** Full Unicode support including emojis

---

## Sample Queries

### How many Tier 2 installations exported data in the last 7 days?
```sql
SELECT COUNT(DISTINCT installation_id)
FROM export_history
WHERE tier = 2
  AND import_timestamp > DATE_SUB(NOW(), INTERVAL 7 DAY);
```

### What are the most common engine makes?
```sql
SELECT engine_make, COUNT(*) as count
FROM installations
GROUP BY engine_make
ORDER BY count DESC
LIMIT 10;
```

### Average AI response time across all installations?
```sql
SELECT AVG(average_response_time_ms) as avg_response_ms
FROM telemetry_ai_assistance
WHERE collection_end > DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Which installations have unresolved critical alerts?
```sql
SELECT i.installation_id, i.boat_manufacturer, a.alert_title, a.alert_timestamp
FROM system_alerts a
JOIN installations i ON a.installation_id = i.installation_id
WHERE a.resolved = FALSE
  AND a.severity = 'critical'
ORDER BY a.alert_timestamp DESC;
```

---

## Files Created

1. **`CENTRAL_DATABASE_SCHEMA.sql`** - Full SQL CREATE TABLE statements
2. **`DATABASE_SCHEMA_SUMMARY.md`** - This document (human-readable reference)

**Ready for review!**
