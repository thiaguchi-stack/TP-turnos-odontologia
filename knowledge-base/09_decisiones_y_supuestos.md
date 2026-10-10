# Decisiones y Supuestos

## Decisiones de diseño (DD)

| ID | Decisión | Fundamento | Contraalternativa descartada |
|----|----------|------------|------------------------------|
| DD-01 | Stack: React + Vite + FastAPI + SQLite (dev) / Postgres (opcional) | Stack libre; velocidad de entrega + mantenibilidad para un TP full-stack; Python y JS ampliamente documentados | Next.js full-stack (menos separación de capas para evaluar), Java/Spring (mayor boilerplate) |
| DD-02 | Single-tenant (un consultorio) | Escala acordada (equipo < 50 personas); evita complejidad multi-tenant que no aporta al TP | Multi-tenant (requiere aislamiento y auth por tenant; backlog) |
| DD-03 | MVP = flujo end-to-end de turnos: reserva → agenda → confirmación, con datos simulados | Alcance P2a acordado; foco en el núcleo del dominio | Incluir recordatorios/cobros (ampliaba demasiado el TP) |
| DD-04 | Reserva online **sin login del paciente** (datos de contacto + token de cancelación) | Menos fricción de adopción; consistente con el research (Doctoralia/Dental Total permiten reserva directa); no hace falta cuenta en v1 | Login de paciente obligatorio (backlog) |
| DD-05 | Duración del turno derivada de la prestación (duración variable) | Refleja la realidad odontológica (30-60 min según práctica) y simplifica la agenda | Turnos de duración fija (ej. 30 min siempre) → inflexible |
| DD-06 | Ninguna integración externa en v1 | Alcance acotado; los servicios externos (pagos, WhatsApp, calendarios) se relegan a backlog con evidencia del mercado | Conectar Mercado Pago/WhatsApp en v1 |
| DD-07 | Capa de servicios + routers delgados en FastAPI | Testeabilidad y cumplimiento de reglas de negocio en un solo lugar (RN-TU) | Lógica en routers (menos testeable) |
| DD-08 | Tratamiento de datos conforme a Ley 25.326 (consentimiento, acceso autorizado) | El sistema maneja datos personales de salud; responsabilidad desde el diseño, aunque sea un TP | Ignorar privacidad (inaceptable para datos de salud) |
| DD-09 | Modelo con sillón/box como recurso del consultorio: el solapamiento se valida por profesional y por sillón (RN-TU-01) | Consigna del TP + regla estándar del dominio odontológico (múltiples profesionales comparten sillones) | Ignorar el sillón en la validación (no cubre la consigna) o modelar multi-sucursal (fuera de alcance, DD-02) |

## Supuestos (SU)

| ID | Supuesto | Riesgo si no se cumple |
|----|----------|------------------------|
| SU-01 | Los pacientes prefieren reservar sin crear cuenta (roto si el research local/encuesta muestra lo contrario) | Bajo: el flujo con token de cancelación cubre la gestión post-reserva |
| SU-02 | Un profesional atiende un paciente a la vez (regla de no solapamiento válida) | Bajo: es el estándar del sector; si hubiera atención simultánea (asistente/sillón doble) habría que relajar RN-TU-01 |
| SU-03 | El consultorio opera con horarios semanales fijos por profesional | Medio: si los horarios cambian a diario, hace falta un calendario de disponibilidad por fecha (backlog) |
| SU-04 | Los datos simulados alcanzan para la demostración del TP | Bajo: los seeds cubren los flujos de la demo |
| SU-05 | La cátedra no impone stack ni deploy específico (confirmado: stack libre) | Bajo: si llegara un requisito de infra, se ajusta deploy, no modelo |
| SU-06 | "TM Dental" no es competidor directo del sistema (es distribuidor B2B, no software de agenda) | Bajo: no afecta la construcción; se revisa en el informe |
| SU-07 | El consultorio tiene un inventario pequeño de sillones/boxes (2-5) y los turnos se asignan a uno | Bajo: si hubiera más sillones o asignación automática, se ajusta la UI/seed; el modelo escala igual (DD-09) |

## Cómo se usan estas decisiones

- Para **implementar**: la arquitectura (08) y el modelo (04) reflejan DD-01..09; las RN en 05 reflejan DD-04/05/06/08/09.
- Para **criticar/entregar**: el informe del TP puede citar DD-01..09 como decisiones con fundamento y revocarlas explícitamente si la cátedra pide otra cosa.