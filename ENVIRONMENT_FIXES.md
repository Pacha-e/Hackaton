# Solución de Problemas del Entorno de Desarrollo (Docker & Windows)

Este documento registra los ajustes realizados al entorno del proyecto el 18 de abril de 2026 para que futuros asistentes de código o desarrolladores sepan cómo levantar exitosamente el proyecto, especialmente en Windows.

## 1. Problema de incompatibilidad Python 3.14 Local
- **Síntoma**: Al hacer `pip install -r requirements.txt` fallaba localmente la compilación de `psycopg2-binary` y `Pillow`.
- **Causa**: El entorno local de Windows estaba usando Python 3.14. Muchas bibliotecas con C-extensions aún no tienen wheels pre-construidos para esa versión. La herramienta *pip* de Windows lanzaba un `KeyError: '__version__'`.
- **Decisión**: Se recomienda encarecidamente utilizar `docker-compose.yml` para levantar la aplicación, ya que el contenedor basea la estabilidad en Alpine/Debian y previene estos conflictos del host.

## 2. Archivo `.env` con retornos de carro estilo Windows (CRLF)
- **Síntoma**: El contenedor web reportaba: `django.db.utils.OperationalError: could not translate host name "db" to address: No address associated with hostname`.
- **Causa**: Al editar o clonar en Windows, el archivo `.env` adquirió finales de línea CRLF (`\r\n`). Docker leía el host como `DB_HOST=db\r`. Al buscar la red interna para `db\r`, el DNS local de Docker Compose fallaba catastróficamente provocando que el contenedor web reiniciara permanentemente.
- **Acción Correctiva**: Se ejecutó un script en Python que purgó los caracteres `\r` del archivo `.env`, convirtiendo los cortes de línea a formato Unix (LF). **Atención:** Si se edita de nuevo el archivo `.env` en bloc de notas u otro editor en Windows, es importante revisar que use LF.

## 3. Puertos ocupados 
- **Síntoma**: Error `Bind for 0.0.0.0:5433 failed: port is already allocated` al intentar usar `docker compose up`.
- **Causa**: Había otro contenedor local llamado `postgres_db` (abierto por accidente desde otro contexto / terminal) anclado exactamente al puerto `5433`.
- **Acción Correctiva**: Se apagó y removió el contenedor huérfano para liberar el puerto y arrancar de forma limpia `hackathon-db-1`.

## 4. Inicialización de la Base de Datos
- **Manejo Correcto**: Al tratarse de un entorno en Docker nuevo, se efectuaron los comandos necesarios `makemigrations` y `migrate` _antes_ de tratar de lanzar los seeders.
- **Seeder ejecutado con éxito**: Se corrió `docker compose exec web python manage.py seed_data` cargando con éxito las dependencias, precedentes, PQRSDs de prueba para OmegaHack 2026, y generando usuarios base (`enlace1`, `juridico1`, `admin`).

---
**El sistema se encuentra operando exitosamente vía Docker (`http://localhost:8000`).**
