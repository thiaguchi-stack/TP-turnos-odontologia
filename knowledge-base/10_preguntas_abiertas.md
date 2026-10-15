# Preguntas Abiertas

## Inconsistencias detectadas

| ID | Inconsistencia | Estado |
|----|----------------|--------|
| IN-01 | En el research, "TM Dental" fue descripto como "centro odontológico de alta demanda" pero el sitio es una **distribuidora de insumos dentales B2B** — no es competidor de software. | Confirmar identidad real antes del informe final |
| IN-02 | El pricing público de Doctoralia (ARS 25.000/35.000/55.000/mes) no muestra plan "First Class". | Descartar para v1 (sin integración) |
| IN-03 | Doctoralia Argentina no evidencia odontograma, imágenes RX, facturación AFIP/ARCA ni Mercado Pago en su oferta pública. | Oportunidad de diferenciación documentada (backlog v2) |

## Preguntas abiertas priorizadas

| # | Pregunta | Impacto | ¿Bloquea v1? | Acción sugerida |
|---|----------|---------|--------------|-----------------|
| 1 | ¿El enlace de cancelación por email es suficiente, o hace falta recordatorio automático al paciente (US-101)? | UX del paciente | No | Confirmar con la cátedra si los recordatorios son necesarios para la nota |
| 2 | ¿Se integra WhatsApp Business API para recordatorios (v2)? | Adopción real en el consultorio | No | Evaluar en backlog; el research muestra que es estándar de mercado |
| 3 | ¿Entran cobros/señas con Mercado Pago en el TP (US-102)? | Diferenciador documentado | No | Solo si el TP lo pide; hoy es backlog |
| 4 | ¿Se integra ficha clínica/odontograma (US-103)? | Diferenciador vs. Doctoralia | No | Backlog v2; el modelo de datos ya lo permite (Paciente + historial) |
| 5 | ¿El deploy es local (demo) o en la nube (Railway/Render)? | Entrega del TP | No | Preguntar a la cátedra; v1 soporta ambos |
| 6 | ¿La cancelación del paciente requiere aviso al consultorio (US-104)? | Operación diaria | No | Backlog v2 |
| 7 | ¿Obra social queda solo informativa o se integra validación de cobertura? | Exactitud de datos | No | Informativa en v1 (ya decidido), validación en backlog |
| 8 | ¿Los horarios del profesional son semanales fijos (SU-03) o cambian por fecha? | Regla de agenda | No* | *Si cambian por fecha, ajustar agenda_service antes de implementar US-001 |

## Vacíos del research de mercado (oportunidades pendientes)

Fuente: `discovery/raw/argentina.md`, `discovery/raw/latam.md` e `discovery/raw/internacional.md` (investigación del 2026-10-09; campos marcados **"No evidenciado"** = sin respaldo público verificable).

| ID | Oportunidad / vacío detectado | Origen | Destino |
|----|-------------------------------|--------|---------|
| OP-01 | Facturación fiscal (AFIP/ARCA) y cobros/señas con Mercado Pago: **no evidenciado** en Doctoralia AR, Docturno AR y otros relevados → vacío del mercado argentino. | `raw/argentina.md` (Doctoralia AR, Docturno) | Backlog v2 (US-102, DD-06) |
| OP-02 | Odontograma / ficha clínica integrada a la agenda: ningún competidor relevante en Argentina lo combina con la gestión de turnos en su oferta pública. | `raw/argentina.md` (Doctoralia AR: odontograma/RX no evidenciado; Docturno: odontograma no evidenciado) | Backlog v2 (US-103) |
| OP-03 | WhatsApp Business API para confirmación y recordatorios: estándar de mercado (evidenciado solo en 2-3 proveedores locales), no generalizado → fuera del MVP v1. | `raw/argentina.md` (SimpleTurno, Docturno, Reservo) y `raw/latam.md` | Backlog v2 (US-101, US-104) |
| OP-04 | Integración con calendarios externos (Google Calendar): **no evidenciado** en Docturno AR ni Doctoralia AR → oportunidad de sincronización para v2. | `raw/argentina.md` (Docturno) | Backlog v2 (DD-06) |

## Cómo cerrar estas preguntas

- Las etiquetadas **"No bloquea v1"** no impiden implementar el MVP; se resuelven antes del informe final (respuesta de la cátedra o decisión del equipo).
- Las decisiones que se tomen deben actualizar `09_decisiones_y_supuestos.md` (nuevo DD/SU) o mover la US del backlog a alcance.