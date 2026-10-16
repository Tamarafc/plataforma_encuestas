# Plataforma de Encuestas

Proyecto backend inicial desarrollado con Python y Django para construir una plataforma de gestion de encuestas.

## Requisitos

- Python 3.12 o superior
- PowerShell en Windows, o una terminal equivalente

## Instalacion

Desde la carpeta que contiene `manage.py`, crea y activa el ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Ejecucion

Ejecuta las comprobaciones y levanta el servidor de desarrollo:

```powershell
python manage.py check
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` para ver la página de bienvenida.

Para comprobar la página personalizada de error, visita `http://127.0.0.1:8000/ruta-inexistente/`.

## Estructura principal

- `encuestas/`: configuracion y URLs principales del proyecto Django.
- `core/`: aplicacion Django con la vista de bienvenida, las URLs propias y las plantillas HTML.
- `requirements.txt`: dependencias del proyecto.
- `.gitignore`: archivos locales que no deben subirse al repositorio.

## Cómo ejecutar el proyecto

1. Crear y activar un entorno virtual, y luego instalar las dependencias:
   pip install -r requirements.txt
2. Ejecutar el script `scripts_sql/crear_base_datos.sql` en MySQL (por ejemplo, en la       pestaña SQL de phpMyAdmin). Crea la base de datos, el usuario y sus permisos. 
3. Copiar .env.example como .env y completar sus valores:
   Copy-Item .env.example .env
4. Aplicar las migraciones:
   python manage.py migrate
5. Crear un superusuario:
   python manage.py createsuperuser
6. Levantar el servidor y entrar a http://127.0.0.1:8000/admin/:
   python manage.py runserver