-- ============================================
-- Manual Database Setup for Statistical Analysis App
-- Run this on your RDS PostgreSQL database
-- ============================================

-- Create Django system tables first
-- ============================================

-- Django migrations tracking table
CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Django content types
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Django permissions
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    UNIQUE(content_type_id, codename)
);

-- Django user groups
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- Django group permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGSERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    UNIQUE(group_id, permission_id)
);

-- Django users
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Django user groups
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    UNIQUE(user_id, group_id)
);

-- Django user permissions
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    UNIQUE(user_id, permission_id)
);

-- Django sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Django admin log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INTEGER,
    user_id INTEGER NOT NULL
);

-- Create Application Tables
-- ============================================

-- 1. UploadedFile table
CREATE TABLE IF NOT EXISTS analysis_uploadedfile (
    id BIGSERIAL PRIMARY KEY,
    file VARCHAR(100) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    file_size INTEGER NOT NULL
);

-- 2. AnalysisSession table (with all fields from both migrations)
CREATE TABLE IF NOT EXISTS analysis_analysissession (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    data_source VARCHAR(20) NOT NULL,
    sample_size INTEGER,
    selected_column VARCHAR(100),
    color VARCHAR(20) NOT NULL DEFAULT 'blue',
    bins INTEGER NOT NULL DEFAULT 30,
    show_plot BOOLEAN NOT NULL DEFAULT true,
    show_stats BOOLEAN NOT NULL DEFAULT true,
    show_correlation BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    uploaded_file_id BIGINT,
    -- SVM fields from second migration
    svm_kernel VARCHAR(20) NOT NULL DEFAULT 'rbf',
    svm_target_column VARCHAR(100),
    svm_test_size FLOAT NOT NULL DEFAULT 0.2,
    -- Foreign key constraints
    CONSTRAINT fk_uploaded_file 
        FOREIGN KEY (uploaded_file_id) 
        REFERENCES analysis_uploadedfile(id) 
        ON DELETE CASCADE
);

-- 3. SVMResults table
CREATE TABLE IF NOT EXISTS analysis_svmresults (
    id BIGSERIAL PRIMARY KEY,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    kernel_type VARCHAR(20) NOT NULL,
    test_size FLOAT NOT NULL,
    target_column VARCHAR(100) NOT NULL,
    feature_columns JSONB NOT NULL,
    class_labels JSONB NOT NULL,
    confusion_matrix JSONB NOT NULL,
    n_samples INTEGER NOT NULL,
    n_features INTEGER NOT NULL,
    n_train INTEGER NOT NULL,
    n_test INTEGER NOT NULL,
    training_date TIMESTAMP WITH TIME ZONE NOT NULL,
    analysis_session_id BIGINT NOT NULL,
    -- Foreign key constraint
    CONSTRAINT fk_analysis_session 
        FOREIGN KEY (analysis_session_id) 
        REFERENCES analysis_analysissession(id) 
        ON DELETE CASCADE
);

-- Create Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_analysissession_session_id ON analysis_analysissession(session_id);
CREATE INDEX IF NOT EXISTS idx_analysissession_updated_at ON analysis_analysissession(updated_at);
CREATE INDEX IF NOT EXISTS idx_uploadedfile_uploaded_at ON analysis_uploadedfile(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_svmresults_training_date ON analysis_svmresults(training_date);
CREATE INDEX IF NOT EXISTS idx_svmresults_analysis_session ON analysis_svmresults(analysis_session_id);
CREATE INDEX IF NOT EXISTS idx_django_session_expire_date ON django_session(expire_date);

-- Mark Migrations as Applied
-- ============================================

-- Mark our custom migrations as applied so Django doesn't try to run them again
INSERT INTO django_migrations (app, name, applied) VALUES
    ('analysis', '0001_initial', NOW()),
    ('analysis', '0002_analysissession_svm_kernel_and_more', NOW())
ON CONFLICT DO NOTHING;

-- Mark Django system migrations as applied (simplified)
INSERT INTO django_migrations (app, name, applied) VALUES
    ('contenttypes', '0001_initial', NOW()),
    ('auth', '0001_initial', NOW()),
    ('admin', '0001_initial', NOW()),
    ('sessions', '0001_initial', NOW())
ON CONFLICT DO NOTHING;

-- Insert Content Types (required for Django admin)
-- ============================================

INSERT INTO django_content_type (app_label, model) VALUES
    ('analysis', 'analysissession'),
    ('analysis', 'uploadedfile'),
    ('analysis', 'svmresults'),
    ('auth', 'permission'),
    ('auth', 'group'),
    ('auth', 'user'),
    ('contenttypes', 'contenttype'),
    ('admin', 'logentry'),
    ('sessions', 'session')
ON CONFLICT DO NOTHING;

-- ============================================
-- Script Complete!
-- ============================================

-- Verify tables were created
SELECT 
    schemaname,
    tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename; 
