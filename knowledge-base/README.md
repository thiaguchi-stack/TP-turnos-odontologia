# Turnos Odontología — Base de Conocimiento

Base de conocimiento generada para el TP de la Tecnicatura Universitaria en Programación (Metodología I). Sistema web de gestión de turnos para una clínica odontológica.

## Índice de Archivos

| Archivo | Contenido |
|---------|-----------|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance v1.0 y fuera de alcance |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack tecnológico, arquitectura general, API REST |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores del sistema, matriz RBAC, rutas públicas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Entidades, ERD, relaciones y seed data |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | Reglas de negocio codificadas (RN-XX-NN) |
| [06_funcionalidades.md](06_funcionalidades.md) | Historias de usuario por épica (US-NNN) |
| [07_flujos_principales.md](07_flujos_principales.md) | Flujos end-to-end: reserva, agenda, confirmación |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura de directorios, seguridad, env vars |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | Decisiones de diseño documentadas + supuestos |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Preguntas abiertas priorizadas y decisiones postergadas |

## Quick Start para Desarrolladores

1. Entender el dominio → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. Entender los datos → [04](04_modelo_de_datos.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender la arquitectura → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. Implementar → [07](07_flujos_principales.md), [06](06_funcionalidades.md)
6. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo

Sistema web full-stack para que los pacientes de una clínica odontológica reserven turnos online sin llamar, y para que el consultorio gestione su agenda de forma centralizada (múltiples profesionales, prestaciones con duración variable, bloqueos). El MVP v1.0 cubre el flujo end-to-end de turnos: **reserva online → agenda → confirmación**, con datos simulados. Stack: React + Vite, FastAPI (Python), SQLite/PostgreSQL, single-tenant.