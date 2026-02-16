-- ============================================================================
-- d3kOS Central Database Schema
-- ============================================================================
-- Purpose: Import and store exported data from all d3kOS installations
-- Version: 1.0
-- Date: 2026-02-16
--
-- Export Categories:
--   1. Engine Benchmarks
--   2. Boatlog Entries
--   3. Marine Vision Captures (metadata only)
--   4. Marine Vision Snapshots (metadata only)
--   5. QR Codes
--   6. Settings Configurations
--   7. System Alerts
--   8. Onboarding/Initial Setup Configurations
--   9. Telemetry & Analytics (5 sub-tables)
-- ============================================================================

-- ============================================================================
-- MASTER TABLES
-- ============================================================================

-- Master registry of all d3kOS installations
CREATE TABLE installations (
    installation_id VARCHAR(16) PRIMARY KEY,  -- 16-char hex hash (SHA-256)
    tier TINYINT NOT NULL,                    -- 0=Free, 1=Free+App, 2=Paid Monthly, 3=Enterprise
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    first_export_at TIMESTAMP NULL,
    last_export_at TIMESTAMP NULL,
    total_exports INT DEFAULT 0,

    -- Installation details (from onboarding)
    boat_manufacturer VARCHAR(100),
    boat_year INT,
    boat_model VARCHAR(100),
    engine_make VARCHAR(100),
    engine_model VARCHAR(100),
    engine_year INT,

    -- System status
    is_active BOOLEAN DEFAULT TRUE,
    last_boot_at TIMESTAMP NULL,
    software_version VARCHAR(20),

    INDEX idx_tier (tier),
    INDEX idx_active (is_active),
    INDEX idx_last_export (last_export_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Track all data imports from d3kOS systems
CREATE TABLE export_history (
    export_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_timestamp TIMESTAMP NOT NULL,      -- When export was created on d3kOS
    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When received by server
    tier TINYINT NOT NULL,
    format_version VARCHAR(10) NOT NULL,

    -- Record counts per category
    engine_benchmarks_count INT DEFAULT 0,
    boatlog_entries_count INT DEFAULT 0,
    marine_vision_captures_count INT DEFAULT 0,
    marine_vision_snapshots_count INT DEFAULT 0,
    qr_codes_count INT DEFAULT 0,
    settings_count INT DEFAULT 0,
    alerts_count INT DEFAULT 0,
    onboarding_count INT DEFAULT 0,
    telemetry_count INT DEFAULT 0,

    total_records INT DEFAULT 0,
    file_size_bytes BIGINT,
    processing_time_ms INT,

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    INDEX idx_installation (installation_id),
    INDEX idx_export_time (export_timestamp),
    INDEX idx_import_time (import_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 1: ENGINE BENCHMARKS
-- ============================================================================

CREATE TABLE engine_benchmarks (
    benchmark_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,            -- When benchmark was created
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Baseline values
    baseline_rpm DECIMAL(7,2),
    baseline_oil_pressure_psi DECIMAL(5,2),
    baseline_coolant_temp_f DECIMAL(5,2),
    baseline_boost_pressure_psi DECIMAL(5,2),
    baseline_fuel_pressure_psi DECIMAL(5,2),

    -- Thresholds
    rpm_idle INT,
    rpm_max INT,
    oil_pressure_min_psi DECIMAL(5,2),
    oil_pressure_max_psi DECIMAL(5,2),
    coolant_temp_min_f DECIMAL(5,2),
    coolant_temp_max_f DECIMAL(5,2),

    -- Metadata
    engine_hours_at_benchmark DECIMAL(10,2),
    conditions TEXT,                          -- Operating conditions during benchmark

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 2: BOATLOG ENTRIES
-- ============================================================================

CREATE TABLE boatlog_entries (
    entry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    entry_timestamp TIMESTAMP NOT NULL,       -- When log entry was created
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Entry details
    entry_type ENUM('voice', 'text', 'auto', 'weather') NOT NULL,
    entry_text TEXT NOT NULL,

    -- Location data
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),

    -- Voice-specific
    voice_duration_seconds INT,
    voice_file_size_bytes BIGINT,

    -- Auto-log data
    trigger_event VARCHAR(100),               -- What triggered the auto-log

    -- Weather data
    weather_temp_f DECIMAL(5,2),
    weather_wind_speed_knots DECIMAL(5,2),
    weather_wind_direction_deg INT,
    weather_wave_height_ft DECIMAL(4,2),
    weather_conditions VARCHAR(100),

    -- Engine data at time of log
    engine_hours DECIMAL(10,2),
    rpm INT,

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_timestamp (entry_timestamp),
    INDEX idx_type (entry_type),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 3: MARINE VISION CAPTURES (Metadata Only)
-- ============================================================================

CREATE TABLE marine_vision_captures (
    capture_id VARCHAR(50) PRIMARY KEY,       -- UUID from d3kOS
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,     -- When photo was taken
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- File metadata (file NOT stored in database)
    file_size_bytes BIGINT NOT NULL,
    file_path_local VARCHAR(500),             -- Path on d3kOS system
    file_transferred BOOLEAN DEFAULT FALSE,   -- Via mobile app
    file_transferred_at TIMESTAMP NULL,

    -- Detection results
    species VARCHAR(100),
    confidence DECIMAL(5,4),                  -- 0.0000 to 1.0000

    -- Location
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    location_name VARCHAR(200),               -- Lake/ocean name

    -- Additional metadata
    person_detected BOOLEAN DEFAULT FALSE,
    fish_detected BOOLEAN DEFAULT FALSE,
    detection_classes TEXT,                   -- JSON array of all detected objects

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_timestamp (capture_timestamp),
    INDEX idx_species (species),
    INDEX idx_location (latitude, longitude),
    INDEX idx_transferred (file_transferred)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 4: MARINE VISION SNAPSHOTS (Metadata Only)
-- ============================================================================

CREATE TABLE marine_vision_snapshots (
    snapshot_id VARCHAR(50) PRIMARY KEY,      -- UUID from d3kOS
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    snapshot_timestamp TIMESTAMP NOT NULL,    -- When video/snapshot was taken
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- File metadata (file NOT stored in database)
    file_size_bytes BIGINT NOT NULL,
    file_path_local VARCHAR(500),             -- Path on d3kOS system
    file_transferred BOOLEAN DEFAULT FALSE,   -- Via mobile app
    file_transferred_at TIMESTAMP NULL,

    -- Camera orientation
    orientation VARCHAR(20),                  -- 'forward_watch', 'fish_capture', 'manual'
    camera_angle_degrees INT,                 -- 0-360

    -- Detection results
    detections_count INT DEFAULT 0,
    detection_types TEXT,                     -- JSON array: ["boat", "kayak", "buoy"]

    -- Location
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),

    -- Forward Watch specific
    alert_triggered BOOLEAN DEFAULT FALSE,
    alert_type VARCHAR(50),                   -- 'proximity', 'collision_risk', etc.
    closest_object_distance_meters DECIMAL(7,2),

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_timestamp (snapshot_timestamp),
    INDEX idx_orientation (orientation),
    INDEX idx_alert (alert_triggered),
    INDEX idx_transferred (file_transferred)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 5: QR CODES
-- ============================================================================

CREATE TABLE qr_codes (
    qr_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    generated_at TIMESTAMP NOT NULL,          -- When QR code was generated
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- QR code data
    installation_uuid VARCHAR(36),            -- UUID format for mobile app pairing
    pairing_token VARCHAR(100),               -- One-time use token
    current_tier TINYINT NOT NULL,

    -- Usage tracking
    pairing_completed BOOLEAN DEFAULT FALSE,
    paired_at TIMESTAMP NULL,
    mobile_app_version VARCHAR(20),

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_uuid (installation_uuid),
    INDEX idx_token (pairing_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 6: SETTINGS CONFIGURATIONS
-- ============================================================================

CREATE TABLE settings_configurations (
    config_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    saved_at TIMESTAMP NOT NULL,              -- When settings were saved
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- User preferences
    language VARCHAR(10) DEFAULT 'en',
    units_system ENUM('metric', 'imperial') DEFAULT 'imperial',
    timezone VARCHAR(50),

    -- Display settings
    screen_brightness TINYINT,                -- 0-100
    auto_dimming BOOLEAN DEFAULT TRUE,
    night_mode BOOLEAN DEFAULT FALSE,

    -- Notification preferences
    alerts_enabled BOOLEAN DEFAULT TRUE,
    voice_alerts BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT FALSE,
    email_address VARCHAR(255),

    -- Thresholds (from engine benchmarks)
    threshold_rpm_low INT,
    threshold_rpm_high INT,
    threshold_oil_pressure_low DECIMAL(5,2),
    threshold_coolant_temp_high DECIMAL(5,2),

    -- Network settings
    wifi_ssid VARCHAR(100),
    wifi_enabled BOOLEAN DEFAULT TRUE,
    hotspot_enabled BOOLEAN DEFAULT FALSE,

    -- Privacy settings
    telemetry_enabled BOOLEAN DEFAULT FALSE,  -- Tier 1+ only
    data_sharing_consent BOOLEAN DEFAULT FALSE,

    -- Full JSON backup
    full_config_json JSON,                    -- Complete settings backup

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_saved (saved_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 7: SYSTEM ALERTS
-- ============================================================================

CREATE TABLE system_alerts (
    alert_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    alert_timestamp TIMESTAMP NOT NULL,       -- When alert was triggered
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Alert details
    alert_type ENUM('health', 'anomaly', 'system', 'critical') NOT NULL,
    alert_category VARCHAR(50),               -- 'engine', 'network', 'storage', etc.
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL,

    -- Message
    alert_title VARCHAR(200) NOT NULL,
    alert_message TEXT NOT NULL,

    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP NULL,
    resolution_notes TEXT,
    auto_resolved BOOLEAN DEFAULT FALSE,

    -- Context data
    sensor_value DECIMAL(10,2),
    threshold_value DECIMAL(10,2),
    engine_hours DECIMAL(10,2),

    -- Location (if applicable)
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_timestamp (alert_timestamp),
    INDEX idx_type (alert_type),
    INDEX idx_severity (severity),
    INDEX idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 8: ONBOARDING/INITIAL SETUP CONFIGURATIONS
-- ============================================================================

CREATE TABLE onboarding_configurations (
    config_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    completed BOOLEAN NOT NULL,
    completion_timestamp TIMESTAMP NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Reset tracking
    reset_count INT DEFAULT 0,
    max_resets INT DEFAULT 10,                -- 10 for Tier 0/1, unlimited for Tier 3
    resets_remaining INT,
    last_reset_timestamp TIMESTAMP NULL,

    -- Wizard answers (Step 1-16)
    boat_manufacturer VARCHAR(100),           -- Step 1
    boat_year INT,                            -- Step 2
    boat_model VARCHAR(100),                  -- Step 3
    chartplotter VARCHAR(100),                -- Step 4
    engine_make VARCHAR(100),                 -- Step 5
    engine_model VARCHAR(100),                -- Step 6
    engine_year INT,                          -- Step 7
    engine_cylinders TINYINT,                 -- Step 8
    engine_displacement_liters DECIMAL(4,1),  -- Step 9
    engine_power_hp INT,                      -- Step 10
    engine_compression_ratio VARCHAR(10),     -- Step 11
    engine_idle_rpm INT,                      -- Step 12
    engine_max_rpm INT,                       -- Step 13
    engine_fuel_type VARCHAR(50),             -- Step 14
    regional_origin VARCHAR(100),             -- Step 15
    engine_position VARCHAR(50),              -- Step 16 (port, starboard, center)

    -- Full wizard data JSON
    wizard_answers_json JSON,                 -- Complete answers backup

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_completed (completed),
    INDEX idx_boat_make (boat_manufacturer),
    INDEX idx_engine_make (engine_make)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CATEGORY 9: TELEMETRY & ANALYTICS
-- ============================================================================

-- 9a. System Performance Telemetry
CREATE TABLE telemetry_system_performance (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    collection_start TIMESTAMP NOT NULL,
    collection_end TIMESTAMP NOT NULL,
    collection_duration_hours DECIMAL(6,2),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Boot & Uptime
    boot_time_seconds DECIMAL(6,2),
    uptime_hours DECIMAL(10,2),
    reboot_count INT DEFAULT 0,

    -- Memory & CPU
    average_ram_usage_mb INT,
    peak_ram_usage_mb INT,
    average_cpu_load DECIMAL(4,2),
    peak_cpu_load DECIMAL(4,2),

    -- Network
    average_network_latency_ms INT,
    network_errors_count INT,

    -- Storage
    storage_used_gb DECIMAL(7,2),
    storage_total_gb DECIMAL(7,2),
    storage_percent_used TINYINT,

    -- Battery (Tier 3)
    battery_health_percent TINYINT,
    average_battery_voltage DECIMAL(4,2),

    -- Service reliability
    service_restarts_json JSON,              -- {"d3kos-voice": 0, "d3kos-ai-api": 1}
    error_counts_json JSON,                   -- {"camera": 5, "gps": 12}

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_period (collection_start, collection_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9b. User Interaction Telemetry
CREATE TABLE telemetry_user_interaction (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    collection_start TIMESTAMP NOT NULL,
    collection_end TIMESTAMP NOT NULL,
    collection_duration_hours DECIMAL(6,2),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Menu navigation
    menu_clicks_json JSON,                    -- {"dashboard": 45, "ai_assistant": 18}

    -- Feature usage
    voice_commands_count INT DEFAULT 0,
    ai_queries_count INT DEFAULT 0,
    camera_captures_count INT DEFAULT 0,
    boatlog_entries_count INT DEFAULT 0,

    -- User flows (page sequences)
    common_flows_json JSON,                   -- [["dashboard", "engine", "settings"]]

    -- Abandoned actions
    abandoned_actions_count INT DEFAULT 0,
    abandoned_actions_json JSON,              -- {"onboarding_step_5": 2}

    -- Settings changes
    settings_changes_count INT DEFAULT 0,

    -- Voice success
    voice_command_success_rate DECIMAL(5,2),  -- 0.00 to 100.00

    -- Input methods
    touchscreen_inputs_count INT DEFAULT 0,
    keyboard_inputs_count INT DEFAULT 0,

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_period (collection_start, collection_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9c. AI Assistance Telemetry
CREATE TABLE telemetry_ai_assistance (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    collection_start TIMESTAMP NOT NULL,
    collection_end TIMESTAMP NOT NULL,
    collection_duration_hours DECIMAL(6,2),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Query counts
    total_queries_count INT DEFAULT 0,
    simple_queries_count INT DEFAULT 0,
    complex_queries_count INT DEFAULT 0,

    -- Response times
    average_response_time_ms INT,
    median_response_time_ms INT,
    p95_response_time_ms INT,               -- 95th percentile

    -- Query distribution
    query_types_json JSON,                   -- {"rpm": 15, "fuel": 8, "help": 3}

    -- Provider usage
    provider_usage_json JSON,                -- {"auto": 20, "online": 5, "onboard": 10}

    -- Cache performance
    cache_hit_rate DECIMAL(5,2),             -- 0.00 to 100.00
    cache_hits_count INT DEFAULT 0,
    cache_misses_count INT DEFAULT 0,

    -- Query abandonment
    abandoned_queries_count INT DEFAULT 0,   -- User didn't wait for response

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_period (collection_start, collection_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9d. Device & Environment Telemetry
CREATE TABLE telemetry_device_environment (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    collection_start TIMESTAMP NOT NULL,
    collection_end TIMESTAMP NOT NULL,
    collection_duration_hours DECIMAL(6,2),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Connected devices
    camera_connected BOOLEAN DEFAULT FALSE,
    camera_uptime_percent DECIMAL(5,2),
    gps_connected BOOLEAN DEFAULT FALSE,
    ais_connected BOOLEAN DEFAULT FALSE,
    chartplotter_connected BOOLEAN DEFAULT FALSE,

    -- Hardware specs
    hardware_model VARCHAR(50),               -- "Raspberry Pi 4B"
    ram_total_mb INT,
    cpu_cores TINYINT,

    -- Network mode
    network_mode VARCHAR(20),                 -- "wifi", "cellular", "offline"
    network_uptime_percent DECIMAL(5,2),

    -- Usage patterns
    time_of_day_usage_json JSON,             -- {"morning": 20, "afternoon": 45, "evening": 15}
    day_of_week_usage_json JSON,             -- {"monday": 5, "saturday": 25}

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_period (collection_start, collection_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9e. Business Intelligence Telemetry
CREATE TABLE telemetry_business_intelligence (
    telemetry_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    installation_id VARCHAR(16) NOT NULL,
    export_id BIGINT NOT NULL,
    collection_start TIMESTAMP NOT NULL,
    collection_end TIMESTAMP NOT NULL,
    collection_duration_hours DECIMAL(6,2),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Installation age
    days_since_installation INT,

    -- Engagement
    daily_active_usage BOOLEAN DEFAULT FALSE, -- User opened UI today
    sessions_this_week INT DEFAULT 0,
    average_session_duration_minutes DECIMAL(6,2),

    -- Tier tracking
    current_tier TINYINT NOT NULL,
    tier_upgrades_count INT DEFAULT 0,
    last_tier_upgrade_at TIMESTAMP NULL,

    -- Feature adoption
    features_used_json JSON,                  -- {"voice": true, "ai": true, "camera": false}

    -- Retention indicators
    weekly_active_user BOOLEAN DEFAULT FALSE,
    monthly_active_user BOOLEAN DEFAULT FALSE,

    FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
    FOREIGN KEY (export_id) REFERENCES export_history(export_id),
    INDEX idx_installation (installation_id),
    INDEX idx_period (collection_start, collection_end),
    INDEX idx_tier (current_tier),
    INDEX idx_retention (weekly_active_user, monthly_active_user)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Active installations summary
CREATE VIEW v_active_installations AS
SELECT
    tier,
    COUNT(*) as total_installations,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_installations,
    COUNT(CASE WHEN last_export_at > DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as active_last_7_days
FROM installations
GROUP BY tier;

-- Recent export activity
CREATE VIEW v_export_activity AS
SELECT
    DATE(import_timestamp) as export_date,
    COUNT(*) as total_exports,
    SUM(total_records) as total_records,
    AVG(processing_time_ms) as avg_processing_time_ms,
    SUM(file_size_bytes) as total_bytes
FROM export_history
WHERE import_timestamp > DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(import_timestamp)
ORDER BY export_date DESC;

-- Fleet overview by boat/engine manufacturer
CREATE VIEW v_fleet_overview AS
SELECT
    boat_manufacturer,
    engine_make,
    COUNT(*) as installation_count,
    AVG(engine_year) as avg_engine_year,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_count
FROM installations
GROUP BY boat_manufacturer, engine_make
ORDER BY installation_count DESC;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_installation_tier ON installations(installation_id, tier);
CREATE INDEX idx_export_installation_time ON export_history(installation_id, export_timestamp);
CREATE INDEX idx_boatlog_installation_time ON boatlog_entries(installation_id, entry_timestamp);
CREATE INDEX idx_alerts_installation_unresolved ON system_alerts(installation_id, resolved, severity);
CREATE INDEX idx_telemetry_installation_period ON telemetry_system_performance(installation_id, collection_start);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- No initial data needed (populated by d3kOS exports)

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- 1. All timestamps use server timezone (recommend UTC)
-- 2. Marine vision media files NOT stored in database (metadata only)
-- 3. JSON columns used for flexible/complex data structures
-- 4. Foreign keys enforce referential integrity
-- 5. Indexes optimized for common query patterns
-- 6. Views provide quick analytics access
-- 7. DECIMAL types for precise numeric values (money, coordinates, percentages)
-- 8. ENUM types for fixed value sets (better performance than VARCHAR)
-- 9. All tables use InnoDB engine (ACID compliance, foreign keys)
-- 10. UTF8MB4 charset (full Unicode support including emojis)
--
-- ============================================================================
