-- init-scripts/init.sql
-- Script khởi tạo database khi container Postgres khởi động lần đầu

-- Tạo App User (tách biệt với root)
CREATE USER social_hub_user WITH PASSWORD 'social_hub_pass@123';

-- Cấp quyền connect database
GRANT CONNECT ON DATABASE social_hub_db TO social_hub_user;

-- Kết nối vào database để cấp quyền schema
\c social_hub_db;

-- Cấp quyền trên schema public (bắt buộc từ PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO social_hub_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO social_hub_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO social_hub_user;

-- Đảm bảo quyền cho các bảng tạo sau (migrate)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO social_hub_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO social_hub_user;
