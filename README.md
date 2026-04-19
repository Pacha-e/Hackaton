# PQRSD Medellín Inteligente

> MVP desarrollado para **OmegaHack 2026** por el equipo **Incapaces FC**.  
> Plataforma para la gestión inteligente de **PQRSD** de la Alcaldía de Medellín, con enfoque en automatización, clasificación asistida por IA y trazabilidad del proceso.

---

## Descripción general

Este proyecto busca modernizar la recepción, clasificación y seguimiento de **peticiones, quejas, reclamos, sugerencias y denuncias (PQRSD)** mediante una solución web compuesta por:

- **Backend en Django + Django REST Framework**
- **Frontend en React + TypeScript + Vite**
- **Base de datos PostgreSQL**
- **Orquestación con Docker Compose**
- **Módulos de IA** para clasificación, síntesis, enrutamiento y apoyo a la respuesta

La solución está diseñada para atender tanto el flujo ciudadano como el flujo interno de funcionarios, centralizando la información y mejorando los tiempos de respuesta.

---

## Objetivo del proyecto

Construir un sistema mínimo viable (MVP) que permita:

- Radicar PQRSD desde un portal ciudadano.
- Consultar el estado de una solicitud.
- Gestionar casos desde un panel interno para funcionarios.
- Clasificar solicitudes con apoyo de inteligencia artificial.
- Sugerir rutas de atención y dependencias responsables.
- Brindar una experiencia más clara, rápida y trazable.

---

## Características principales

### Portal ciudadano
- Radicación de solicitudes.
- Consulta por número de radicado.
- Confirmación de envío.
- Interfaz simple y accesible.

### Panel de funcionarios
- Autenticación para personal autorizado.
- Dashboard con métricas generales.
- Bandeja de entrada de solicitudes.
- Vista detallada de casos.
- Visualización operativa (mapa de calor).
- Clasificación y priorización de PQRSD.

### Módulos inteligentes
- Normalización de solicitudes.
- Filtrado inicial.
- Cálculo de SLA.
- Enrutamiento por dependencia.
- Validaciones de privacidad.
- Recuperación de conocimiento de casos previos.
- Generación de síntesis y apoyo a respuestas.

---

## Arquitectura del sistema

pqrds-medellin/
├── apps/
│   ├── agentes/
│   ├── api/
│   ├── clasificacion/
│   ├── conocimiento/
│   ├── funcionarios/
│   ├── pqrsd/
│   └── sintesis/
├── config/
├── templates/
├── frontend/
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md

---

## Stack tecnológico

- React 19, TypeScript, Vite, Tailwind CSS  
- Django 4.2, Django REST Framework  
- PostgreSQL 15  
- Docker Compose  
- IA para clasificación y asistencia  

---

## Requisitos

- Docker Desktop  
- Docker Compose  
- Make  
- Node.js (opcional)  
- Python 3.11+ (opcional)  

---

## Ejecución rápida

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_PROYECTO>
cp .env.example .env
make setup
```

O:

```bash
docker compose up --build
```

---

## Servicios

- http://localhost:5175/
- http://localhost:5175/pqrsd/
- http://localhost:5175/funcionarios/
- http://localhost:5175/api/v1/

---

## Usuarios de prueba

- admin / admin1234  
- enlace1 / pqrsd2026  
- juridico1 / pqrsd2026  

---

## Comandos

```bash
make help
make setup
make run
make stop
make restart
make logs
make test
make migrate
make seed
make clean
```

---

## Flujo

1. Ciudadano radica PQRSD  
2. Sistema procesa  
3. Clasificación IA  
4. Asignación  
5. Gestión interna  
6. Consulta ciudadana  

---

## Próximas mejoras

- Omnicanal  
- Analítica  
- CI/CD  
- Roles avanzados  

---

## Licencia

Uso académico / hackathon.