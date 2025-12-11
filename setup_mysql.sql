-- Crear base de datos y usuario para bar_galileo
-- Ejecutar: mysql -u root -p < setup_mysql.sql

CREATE DATABASE IF NOT EXISTS bar_galileo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'bar_galileo_user'@'localhost' IDENTIFIED BY 'Galileo2025';
GRANT ALL PRIVILEGES ON bar_galileo.* TO 'bar_galileo_user'@'localhost';
FLUSH PRIVILEGES;
