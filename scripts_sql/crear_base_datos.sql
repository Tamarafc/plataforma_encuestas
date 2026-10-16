-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS plataforma_encuestas_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear el usuario (la contraseña debe coincidir con DB_PASSWORD del .env)
-- Si el servidor fuera remoto, usar '%' en vez de 'localhost'
CREATE USER IF NOT EXISTS 'encuestas_user'@'localhost' IDENTIFIED BY 'tu_contraseña';

-- Asignar permisos sobre esa base de datos
GRANT ALL PRIVILEGES ON plataforma_encuestas_db.* TO 'encuestas_user'@'localhost';
FLUSH PRIVILEGES;