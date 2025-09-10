-- RazorFlow AI Database Initialization Script
-- This script sets up the initial database schema and data

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database tables
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create bot configurations table
CREATE TABLE IF NOT EXISTS bot_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bot_type VARCHAR(50) NOT NULL, -- 'finance', 'sales', 'scheduler'
    config_name VARCHAR(100) NOT NULL,
    config_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    bot_type VARCHAR(50) NOT NULL,
    session_name VARCHAR(200),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id),
    message_type VARCHAR(20) NOT NULL, -- 'user', 'bot'
    content TEXT NOT NULL,
    metadata JSONB,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create finance data table
CREATE TABLE IF NOT EXISTS finance_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    revenue DECIMAL(15,2),
    expenses DECIMAL(15,2),
    profit DECIMAL(15,2),
    growth_rate DECIMAL(5,2),
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sales data table
CREATE TABLE IF NOT EXISTS sales_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    leads INTEGER,
    conversions INTEGER,
    conversion_rate DECIMAL(5,2),
    pipeline_value DECIMAL(15,2),
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create scheduler data table
CREATE TABLE IF NOT EXISTS scheduler_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    meetings_today INTEGER,
    meetings_week INTEGER,
    utilization_rate DECIMAL(5,2),
    available_slots INTEGER,
    period_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4),
    metric_unit VARCHAR(20),
    bot_type VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_finance_data_user_id ON finance_data(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_data_user_id ON sales_data(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduler_data_user_id ON scheduler_data(user_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_bot_type ON performance_metrics(bot_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_at ON performance_metrics(recorded_at);

-- Insert sample data for demo
INSERT INTO users (email, username, password_hash, first_name, last_name, is_admin) 
VALUES 
    ('admin@razorflow.ai', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewmMdeHKjDO9hSVm', 'Admin', 'User', true),
    ('demo@razorflow.ai', 'demo', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewmMdeHKjDO9hSVm', 'Demo', 'User', false)
ON CONFLICT (email) DO NOTHING;

-- Insert sample finance data
INSERT INTO finance_data (user_id, revenue, expenses, profit, growth_rate, period_start, period_end)
SELECT 
    u.id, 
    125000.00, 
    78000.00, 
    47000.00, 
    12.50,
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE
FROM users u WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;

-- Insert sample sales data
INSERT INTO sales_data (user_id, leads, conversions, conversion_rate, pipeline_value, period_start, period_end)
SELECT 
    u.id, 
    234, 
    56, 
    23.93,
    2100000.00,
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE
FROM users u WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;

-- Insert sample scheduler data
INSERT INTO scheduler_data (user_id, meetings_today, meetings_week, utilization_rate, available_slots, period_date)
SELECT 
    u.id, 
    8, 
    23, 
    89.50,
    4,
    CURRENT_DATE
FROM users u WHERE u.username = 'demo'
ON CONFLICT DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bot_configs_updated_at ON bot_configs;
CREATE TRIGGER update_bot_configs_updated_at BEFORE UPDATE ON bot_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_finance_data_updated_at ON finance_data;
CREATE TRIGGER update_finance_data_updated_at BEFORE UPDATE ON finance_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sales_data_updated_at ON sales_data;
CREATE TRIGGER update_sales_data_updated_at BEFORE UPDATE ON sales_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_scheduler_data_updated_at ON scheduler_data;
CREATE TRIGGER update_scheduler_data_updated_at BEFORE UPDATE ON scheduler_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Log the successful initialization
INSERT INTO performance_metrics (metric_name, metric_value, metric_unit, bot_type)
VALUES ('database_initialized', 1.0, 'boolean', 'system');

COMMIT;
