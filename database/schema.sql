-- Sistem Manajemen Risiko KPPN - Database Schema
-- PostgreSQL 15+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(150),
  role VARCHAR(50) DEFAULT 'user',
  section VARCHAR(50),
  is_active BOOLEAN DEFAULT true,
  last_login TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_section ON users(section);

-- Risk Indicators Table (26 indikator)
CREATE TABLE risk_indicators (
  id SERIAL PRIMARY KEY,
  indicator_code VARCHAR(20) UNIQUE NOT NULL,
  indicator_name VARCHAR(255) NOT NULL,
  indicator_description TEXT,
  indicator_type VARCHAR(50),
  pic_section VARCHAR(100),
  secondary_pics VARCHAR(500),
  p26_initial INT,
  r26_target INT,
  is_active BOOLEAN DEFAULT true,
  effective_quarter VARCHAR(5),
  effective_year INT DEFAULT 2024,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_indicators_code ON risk_indicators(indicator_code);
CREATE INDEX idx_indicators_section ON risk_indicators(pic_section);

-- Risk Assessments Table
CREATE TABLE risk_assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  indicator_id INT REFERENCES risk_indicators(id),
  quarter VARCHAR(5) NOT NULL,
  year INT DEFAULT 2024,
  section VARCHAR(100) NOT NULL,
  frequency INT DEFAULT 1,
  impact INT DEFAULT 1,
  risk_value INT NOT NULL,
  risk_category VARCHAR(20),
  previous_quarter VARCHAR(5),
  previous_risk_value INT,
  risk_change INT,
  change_reason TEXT,
  mitigation_action TEXT,
  status VARCHAR(50) DEFAULT 'draft',
  submitted_by UUID REFERENCES users(id),
  submitted_at TIMESTAMP,
  verified_by UUID REFERENCES users(id),
  verified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_indicator ON risk_assessments(indicator_id);
CREATE INDEX idx_assessments_quarter ON risk_assessments(quarter, year);
CREATE INDEX idx_assessments_section ON risk_assessments(section);

-- Risk Change Logs (Audit Trail)
CREATE TABLE risk_change_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assessment_id UUID REFERENCES risk_assessments(id) ON DELETE CASCADE,
  from_risk_value INT,
  to_risk_value INT,
  change_reason TEXT,
  changed_by UUID REFERENCES users(id),
  changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ip_address VARCHAR(50)
);

CREATE INDEX idx_change_logs_assessment ON risk_change_logs(assessment_id);

-- Supporting Documents
CREATE TABLE supporting_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assessment_id UUID REFERENCES risk_assessments(id) ON DELETE CASCADE,
  original_filename VARCHAR(255),
  stored_filename VARCHAR(255),
  file_path VARCHAR(500),
  file_size INT,
  mime_type VARCHAR(100),
  description TEXT,
  uploaded_by UUID REFERENCES users(id),
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_assessment ON supporting_documents(assessment_id);

-- Risk Matrix Mapping
CREATE TABLE risk_matrix_mapping (
  id SERIAL PRIMARY KEY,
  risk_value INT UNIQUE NOT NULL,
  frequency INT NOT NULL,
  impact INT NOT NULL,
  category VARCHAR(20) NOT NULL,
  color_code VARCHAR(10),
  description VARCHAR(255),
  mitigation_level VARCHAR(50)
);

-- Quarterly Summaries
CREATE TABLE quarterly_summaries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quarter VARCHAR(5) NOT NULL,
  year INT DEFAULT 2024,
  section VARCHAR(100) NOT NULL,
  total_indicators INT,
  completed_indicators INT,
  blue_count INT DEFAULT 0,
  green_count INT DEFAULT 0,
  yellow_count INT DEFAULT 0,
  orange_count INT DEFAULT 0,
  red_count INT DEFAULT 0,
  overall_risk_score INT,
  is_submitted BOOLEAN DEFAULT false,
  submitted_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_summaries_quarter ON quarterly_summaries(quarter, year);

-- Audit Logs
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(100),
  resource_type VARCHAR(100),
  resource_id VARCHAR(100),
  status VARCHAR(50) DEFAULT 'success',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_date ON audit_logs(created_at);
