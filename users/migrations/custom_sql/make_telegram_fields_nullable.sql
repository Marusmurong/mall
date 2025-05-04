-- 修改telegram_chat_id字段允许为空（PostgreSQL语法）
ALTER TABLE users_userprofile ALTER COLUMN telegram_chat_id DROP NOT NULL;
-- 修改telegram_connected字段允许为空或设置默认值
ALTER TABLE users_userprofile ALTER COLUMN telegram_connected DROP NOT NULL;
ALTER TABLE users_userprofile ALTER COLUMN telegram_connected SET DEFAULT false;
-- 修改telegram_token字段允许为空
ALTER TABLE users_userprofile ALTER COLUMN telegram_token DROP NOT NULL;
-- 修改telegram_username字段允许为空
ALTER TABLE users_userprofile ALTER COLUMN telegram_username DROP NOT NULL;
-- 设置现有记录的默认值
UPDATE users_userprofile SET telegram_chat_id = '' WHERE telegram_chat_id IS NULL;
UPDATE users_userprofile SET telegram_connected = false WHERE telegram_connected IS NULL;
UPDATE users_userprofile SET telegram_token = '' WHERE telegram_token IS NULL;
UPDATE users_userprofile SET telegram_username = '' WHERE telegram_username IS NULL; 