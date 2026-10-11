# Informe de Discovery — Sistema de gestión de turnos y agenda para consultorios odontológicos en Argentina

**Materia:** Metodología I — Tecnicatura Universitaria en Programación
**Integrante:** Thiago Oviedo
**Tipo de trabajo:** Trabajo Práctico individual
**Fecha del informe:** 2026-10-11
**Fuentes de investigación:** `docs/discovery/raw/{argentina,latam,internacional}.md` y `docs/discovery/verificacion-fuentes.md` (consultas el 2026-10-09)

---

## 1. Resumen ejecutivo

Este informe consolida la **Etapa 2 (Discovery)** del TP: la investigación de mercado de sistemas de gestión de turnos y agenda para consultorios odontológicos, con foco en el mercado argentino. Se relevaron **34 sistemas** en tres rondas (14 de Argentina, 8 de Latinoamérica y 12 internacionales), más 7 referentes LatAm adicionales citados como ampliación, a partir de sitios oficiales, documentación, marketplaces móviles y fuentes de terceros, todos consultados el **2026-10-09** y verificados posteriormente (`verificacion-fuentes.md`).

**Principales hallazgos:**

- **La reserva online 24/7 ya es estándar**, tanto en el mercado argentino (Doctoralia, Docturno, DentalSoft) como en los productos cloud modernos del exterior (Dentally, Curve, Dentrix Ascend, CareStack, tab32, Denticon). No es un diferencial por sí sola.
- **Los competidores más completos como sistema odontológico argentino** son **DentalSoft**, **DentalSaaS** y **Dentiqa**: combinan odontograma/periodontograma, obras sociales y WhatsApp. **Doctoralia** y **Docturno** son los más fuertes en agenda/turnos, pero **no son sistemas odontológicos** (sin odontograma ni fiscalización clínica dental evidenciada).
- **Nadie demostró públicamente prevención de solapamientos** con reglas explícitas (borde a borde `[inicio, fin)` y duración derivada de la prestación). ClinicQ (Ecuador) es el más cercano ("validación en tiempo real doctor y sillón").
- **WhatsApp es el canal rey en LatAm**, pero casi inexistente en la oferta de EE.UU./UK: es un hueco competitivo claro para un producto argentino.
- **La facturación fiscal local (AFIP/ARCA) es la barrera de entrada más fuerte** y un vacío del mercado: ningún competidor relevado la resuelve para Argentina salvo DoctorYa y Reservo (y con evidencia parcial).
- **Seguridad y trazabilidad es el talón de Aquiles regional**: la mayoría solo afirma "seguro" sin aportar evidencia; casi ninguno declara la Ley 25.326 argentina.

**MVP recomendado:** sistema web single-tenant (un consultorio) con **núcleo de turnos**: reserva pública sin login, agenda gestionada por admin, anti-solapamiento por profesional y por sillón/box, duración derivada de la prestación, estados de turno y autenticación JWT para roles admin/odontólogo. **Sin** recordatorios, cobros, ficha clínica ni integraciones externas en v1 (esas capacidades quedan documentadas como backlog v2 con evidencia de mercado). Este MVP es consistente con el alcance v1.0 de la knowledge-base.

---

## 2. Sección A — Tabla comparativa

**Criterio de orden:** primero los **14 sistemas argentinos** (mercado objetivo), luego **8 de Latinoamérica** (idioma y contexto local compartido) y por último **12 internacionales** (referentes de práctica y UX). Dentro de cada región se conserva el orden del raw.

**Convención de evidencia (idéntica a los raw):** `(C)` = **funcionalidad comprobada** (la muestra el producto/sitio/documentación/video oficial) · `(A)` = **afirmación comercial** (lo declara el proveedor sin demostrarlo) · **No evidenciado** = sin respaldo público verificable (no se deduce). Cada fila consigna **URL de origen + fecha de consulta**. Todas las consultas son del **2026-10-09**.

### 2.1 Argentina (14 sistemas)

| Producto / Proveedor | País · Segmento | Modalidad | Agenda (multi-prof. / sillón / duración / bloqueos / anti-solapamiento) | Reserva online / Turnos digitales | Recordatorios / Automatización | Gestión odontológica clínica | Administración / Cobros | Integraciones | Precio publicado | Fuente y fecha |
|---|---|---|---|---|---|---|---|---|---|---|
| **Doctoralia** / Docplanner | Argentina · Marketplace de salud + agenda (odonto. como especialidad) | SaaS + directorio; app iOS/Android | Agenda en planes PRO; lista de espera (VIP); multi-prof./multi-sede **No evidenciado**; anti-solapamiento **No evidenciado** | Sí (C) · multicanal 24/7 (perfil, web, Google My Business, redes) | Sí (C) · email y push; SMS en Plus+ (1.000/mes) | Registros médicos básicos (C, Plus+); odontograma/imágenes **No evidenciado** | AFIP/ARCA **No evidenciado**; cobros **No evidenciado**; obras sociales solo filtro de directorio | Google My Business (C); WhatsApp / API / Mercado Pago **No evidenciado** | ARS 25.000 / 35.000 / 55.000 por mes (anual) | `doctoraliar.com`; `pro.doctoralia.com/ar/precio` — 2026-10-09 |
| **Docturno** / Docturno | Argentina · Directorio + agenda para profesionales (medicina y odonto.) | SaaS + directorio; app | Agenda online por profesional; multi-sede, duración por prestación, bloqueos y anti-solapamiento **No evidenciado** | Sí (C) · turnos online 24/7; avisos de cambios; bot de WhatsApp | Sí (C) · email/SMS/WhatsApp 24h y 3h antes | Historia clínica (A: referenciada en menú); odontograma/imágenes **No evidenciado** | Mercado Pago (C); AFIP/obras sociales/caja **No evidenciado** | WhatsApp (A: "integración oficial"); Mercado Pago; Google Calendar/API **No evidenciado** | **No publicado** (contacto con ventas) | `docturno.com`; `profesionales.docturno.com` — 2026-10-09 |
| **Dental Total** / SIO S.A. | Argentina · Red de clínicas (no vende software) | Web corporativa + portal de turnos propio (SPA) | Portal 24/7 de autogestión ("en 5 clics"); agenda interna **No evidenciado** (SPA); anti-solapamiento **No evidenciado** | Sí (C) · autogestión 24/7; turnos por WhatsApp | **No evidenciado** | No aplica / **No evidenciado** (no comercializa HC) | **No evidenciado** (portal, no ERP) | WhatsApp (canal); Google (reseñas Trustindex); otros **No evidenciado** | **No publicado** (no comercializa el software) | `dentaltotal.com.ar`; `turnos.dentaltotal.com.ar` — 2026-10-09 |
| **Reservo** / Reservo | LatAm (versión AR) · Software médico multirrubro con odontología | SaaS en la nube | Agenda de pacientes; reserva web/Facebook; control de sesiones; bloqueos/anti-solapamiento **No evidenciado** | Sí (C) · en sitio web y Facebook | Sí · correos de confirmación + WhatsApp (A; cadencia 24h **No evidenciado**) | Fichas/odontogramas/presupuestos (A: listado sin demo); periodontograma/imágenes **No evidenciado** | Boleta/factura electrónica AFIP/ARCA; presupuestos; comisiones; finanzas | MercadoPago, WhatsApp, Google Calendar, WooCommerce, Vambe (listadas); API **No evidenciado** | **No publicado** (cotización) | `reservo.cl`; `agendamiento.reservo.cl` — 2026-10-09 |
| **DentalSoft** / DentalSoft | Argentina · Odontología 100% | SaaS + asistente virtual WhatsApp | Multi-profesional; detección de solapamientos (A: listado); Google Calendar; bloqueos/sobreturnos **No evidenciado** | Sí (C) · turnos online 24/7 (4 pasos); portal del paciente (Pro) | Sí (C) · WhatsApp/email con confirmación que actualiza la agenda; chatbot | HC digital; odontograma FDI (18 estados); ortodoncia por etapas; radiografías **No evidenciado** | Caja/cobros; obras sociales/liquidaciones; Mercado Pago; AFIP **No evidenciado** | WhatsApp oficial (Meta), Google Calendar, Mercado Pago; AFIP/API **No evidenciado** | ARS 30.000/mes (Gestión); 60.000/mes (Pro); prueba $0 (3 meses) | `dentalsoft.com.ar`; `/funcionalidades` — 2026-10-09 |
| **Dentiqa** / Violet Wave | LatAm (versión AR) · Odontología con IA | SaaS + app | Agenda multi-dentista con bloqueos; vista por profesional; lista de espera **No evidenciado** | Sí (C) · chatbot IA WhatsApp 24/7; reserva web **No evidenciada** explícita | Sí (C) · WhatsApp 24h/2h con confirmación; pipeline CRM; campañas | Odontograma versionado; periodontograma BOP/NIC; imágenes; firma electrónica | Presupuestos y facturación por profesional; caja/obras sociales **No evidenciado** | WhatsApp Business API oficial (Meta); Mercado Pago; otros **No evidenciado** | USD 89 / 149 / 249 por mes (y equivalentes ARS); demo | `dentiqa.app/ar` — 2026-10-09 |
| **DoctorYa** / DoctorYa | Argentina · Turnos + historia clínica | SaaS + directorio | Agenda día/semana/mes; bloqueos (A); múltiples sedes; duración por prestación (A); anti-solapamiento **No evidenciado** | Sí (C) · reserva online 24/7; directorio; cancelación por WhatsApp | Sí (C) · WhatsApp con confirmación/cancelación que actualiza la agenda | Ficha clínica con odontograma; estudios/RX (A); presupuestos **No evidenciado** | Obras sociales y copagos; caja/cobros; facturación AFIP/ARCA (Monotributo/RI); Mercado Pago | WhatsApp nativo, Mercado Pago, AFIP/ARCA; API **No evidenciado** | ARS 9.000 y 25.000 por mes (al momento del relevamiento; ruta de planes **ya no pública** — ver C-02) | `doctorya.com.ar` — 2026-10-09 |
| **DentalSaaS** / DelRioTech SAS | Argentina · Odontología 100% | SaaS 100% nube, sin permanencia | Agenda inteligente; detección de solapamientos (A); portal con auto-agendamiento | Sí · portal del paciente con auto-agendamiento y aprobación de presupuestos; cobros online | Sí · WhatsApp/email automáticos (configuración adicional) | Odontograma; periodontograma; fichas por 6 especialidades; consentimientos con firma; imágenes/RX | Caja; +10 reportes (PDF/Excel); liquidación de profesionales; obras sociales/nomenclador; laboratorios; stock | WhatsApp (config. adicional), Mercado Pago, export PDF/Excel; AFIP/API **No evidenciado** | ARS 59.000 / 149.000 / 349.000 por mes | `dental.delriotech.com.ar` — 2026-10-09 |
| **Bilog** / Bilog | Argentina · Odontología 100% (+20 años) | SaaS + app móvil | Agenda diaria; alta por QR; turnos online; vistas por profesional; anti-solapamiento y lista de espera **No evidenciado** | Sí · turnos online; reserva de pacientes nuevos; app móvil | Sí · confirmaciones automáticas; recordatorios (listado); iAngela (IA en RX) | Odontograma; tratamientos; HC digital; recetas; iAngela (IA RX); periodontograma **No evidenciado** | Presupuestos; pagos; liquidaciones de obras sociales; reportes/KPIs | App móvil, recetas, iAngela; WhatsApp/AFIP **No evidenciado** | **No publicado** | `bilog.com.ar` — 2026-10-09 |
| **Dentora** / Dentora | Argentina · Odontología 100% | SaaS en la nube | Agenda por tipo de prestación; bloqueos; vistas diaria/semanal; link por profesional; anti-solapamiento **No evidenciado** | Sí · link personalizado; recordatorio 24h con confirmación/cancelación por clic; cobro anticipado | Sí · recordatorio 24h + confirmación/cancelación automática | Ficha clínica digital (listada); odontograma/periodontograma **No evidenciado** | Cobro anticipado al reservar; caja/facturación **No evidenciado** | WhatsApp nativo; integraciones "a medida"; Mercado Pago **No explicitado** | ARS 13.600 (3 meses); ARS 17.000/mes; USD 500 (5 años) | `dentora.com.ar`; `/precios` — 2026-10-09 |
| **DenPro** / DenPro (UE) | UE · Odontología 100% (comercializado en AR, `.ar`) | SaaS | Gestión de turnos; turnos online; sala de espera inteligente; recordatorios SMS (A); anti-solapamiento **No evidenciado** | Sí · turnos online; confirmación/cancelación **No evidenciado** | Sí · SMS (listado); WhatsApp **No evidenciado** (solo soporte) | Historias clínicas; odontograma FDI; recetas | Facturación; exportación de seguros; inventario (Team); fiscal AR **No evidenciado** | RGPD/data centers UE; AFIP/ARCA **No evidenciado** | ARS 19.900 / 29.900 por mes (moneda no explicitada) | `denpro.ar`; `/precios` — 2026-10-09 |
| **SimpleTurno** / 5Studios | Proveedor **No evidenciado** · Multirrubro (vertical odontología) | SaaS | Multi-profesional (A); reserva 24/7; duración por profesional (A); anti-solapamiento **No evidenciado** | Sí · reserva online 24/7 ("listo en 5 minutos"); link público | Sí · WhatsApp/email ("reduce ausentismo hasta 80%" — A) | **Sin historia clínica por diseño** (declarado); odontograma No aplica | Señas con Mercado Pago; facturación/caja **No evidenciado** | WhatsApp (cupo mensual), Mercado Pago, Google Calendar | Gratis $0/mes; Pro $12.900/mes (moneda no explicitada) | `simpleturno.com`; `/rubros/odontologia` — 2026-10-09 |
| **OdontoApp** / OdontoApp | Argentina (declarado) · Odontología 100% | SaaS (SPA sin render público) | "Agenda digital" (tagline); detalle **No evidenciado** | **No evidenciado** (la home no detalla reserva del paciente) | "Recordatorios automáticos" (tagline); canal **No evidenciado** | Historia clínica y odontograma (tagline); sin demo (parcial) | **No evidenciado** | **No evidenciado** | **No evidenciado** (SPA no renderiza) | `odontoapp.com.ar` — 2026-10-09 |
| **Nimbo** / Ecaresoft Inc. | México/LatAm (landing `/ar`) · Clínica multipropósito, módulo dental | SaaS modular + app | Agenda por médico; agenda colaborativa; portal de solicitud de citas; teleconsulta; anti-solapamiento **No evidenciado** | Sí · portal/sitio de solicitud de citas; portal paciente web/app | Sí · WhatsApp, email y SMS; encuestas; notas IA | Odontograma online (A); periodontograma/imágenes **No evidenciado** | ERP: facturación, inventario, cuentas por cobrar; fiscal AR **No evidenciado** | WhatsApp, Google Calendar, Stripe; API **No evidenciado** | **No publicado**; prueba 14 días | `nimbo-x.com/ar`; `/ar/precios` — 2026-10-09 (nota: `/ar/clinica-dental` 404, ver C-04) |

### 2.2 Latinoamérica (8 sistemas)

| Producto / Proveedor | País · Segmento | Modalidad | Agenda (multi-prof. / sillón / duración / bloqueos / anti-solapamiento) | Reserva online / Turnos digitales | Recordatorios / Automatización | Gestión odontológica clínica | Administración / Cobros | Integraciones | Precio publicado | Fuente y fecha |
|---|---|---|---|---|---|---|---|---|---|---|
| **Dentalink** / OpenMind (atrib. tercero) | Chile (CO/MX/ES) · Odontología 100% | SaaS web en la nube | Diaria/semanal/global de **sillones**; multi-profesional; duración variable; sobreagendamiento paralelo; bloqueos y anti-solapamiento **No evidenciado** | Sí · agendamiento 24/7 incluido en todos los planes; widget poco documentado (parcial) | Sí · WhatsApp y email; tareas automáticas (Titanium); citas recurrentes | HC dental; odontograma y periodontograma; ortodoncia; videos 3D; RX parcial (web ES) | Caja; pagos online; cuotas/créditos; convenios; inventario/comisiones (Pro); multicentro | WhatsApp (parcial); Google Calendar/API **No evidenciado**; factura fiscal CL **No evidenciado** | **No publicado**; tercero cita "desde ~USD 29/mes" (afirmación de tercero) | `softwaredentalink.com/cl/planes` — 2026-10-09 |
| **Clinicorp** / Clinicorp | Brasil · Odontología y estética | SaaS + implementación obligatoria | Diaria; multi-profesional; multi-sillón/box ("evite el conflicto de agendas"); duración variable (parcial); bloqueos/sobreturnos **No evidenciado** | Sí (parcial) · WhatsApp, link o SMS; app Clini.me | Sí · SMS/email/app; régua de cobranza; alerta de retorno; IA | Prontuario digital; anamnesis; odontograma; radiología (Image2Doc/iDoc); presupuestos; alineadores/implantes | NFS-e; boletos/PIX/cartão; SPC; comisiones; estoque; dashboard | WhatsApp (R$ 0,12/envío); SMS; API (R$ 99,90/mes); NFS-e; radiología | R$ 159,90/mes (Standard); R$ 369,90/mes (Premium) — discrepancia interna | `clinicorp.com/planos` — 2026-10-09 |
| **Feegow Clinic** / Feegow | Brasil · Clínicas médicas/odontológicas multiprofesional | SaaS web (AWS) | Diaria/semanal/múltiple; multi-profesional; multiclínica; duración configurable; fila de espera; repescaje; anti-solapamiento parcial | Parcial · agendamiento online 24h **limitado** (vía Doctoralia) | Sí · lembretes automáticos (canal no detallado); repescagem; teleconsulta; IA | Prontuario personalizable; odontograma/periodontograma **No evidenciado**; banco de imágenes (parcial) | Control financiero; faturamento TISS/ANS; NFS-e (parcial); relatórios | API abierta (sí); Doctoralia; TISS/ANS; firma digital (Plus) | R$ 129 (Starter) / 199 (Plus) / 249 (VIP) por profesional/mes | `feegowclinic.com.br/precos-e-planos` — 2026-10-09 |
| **Ninsaúde Clinic** / Ninsaúde | Brasil · Clínicas/franquias (incluye odontología) | SaaS en la nube | Multi-profesional (por profesional y sala); multi-sucursal; sesiones/tratamientos; bloqueos parcial; anti-solapamiento **No evidenciado** | Sí · widget en sitios y redes sociales (muy configurable) | **No evidenciado** (solo email marketing y check-in citados) | Odontograma **parcial** (insinuado); anamnesis/radiología **No evidenciado**; presupuestos parcial | Ninsaúde Pay; NFS-e/relatórios parcial; PIX/boleto/cartão; liquidación a profesionales | Ninsaúde Sign; Google Workspace (A de tercero); WhatsApp/API **No evidenciado** | **No publicado**; tercero cita "desde R$ 139/mes" | `ninsaude.com/pt-br/software-odontologia` — 2026-10-09 |
| **Doctocliq** / Zolupro S.A.C. | Perú/México · LatAm (20+ países) · Odontología y estética | SaaS + apps iOS/Android | Multi-profesional; multi-sucursal; agrupación de agendas; duración parcial; bloqueos parcial (Google Calendar); anti-solapamiento **No evidenciado** | Sí · link 24/7 (web/Instagram/WhatsApp); bot Soyla IA agenda | Sí · WhatsApp/email/SMS (SMS MX); anti-no-show; controles semestrales; CRM | Expediente clínico; odontograma y periodontograma; ortodoncia; estética; presupuestos; imágenes parcial | Caja; reportes; facturación SUNAT/SAT/SRI/DIAN; pagos online (solo Perú) | WhatsApp Business; Google Calendar; facturación multi-país; API **No evidenciado** | Gratuito permanente (30 citas/mes); Básico desde USD 29/mes | `doctocliq.com/planes-y-precios` — 2026-10-09 |
| **AgendaPro** / Gunei Investment SPA | Chile/LatAm · Belleza, salud, bienestar (vertical dental) | SaaS + app iOS | Diaria/semanal/mensual; multi-profesional; multi-sucursal; multi-sala/recurso; duración variable; bloqueos; sobre-reservas controladas; anti-solapamiento parcial | Sí (C) · 24/7; link/QR/redes; IA "Sofia" | Sí · WhatsApp/SMS/email; anticipos anti-no-show; códigos promocionales | Ficha clínica personalizable; odontograma/periodontograma/radiología **No evidenciado** | Cobros; POS propia; documentos tributarios electrónicos CL; comisiones | WhatsApp/SMS; FONASA/CENS (CL); calendario/API **No evidenciado** | CLP (App Store): individual $18.900; Básico $34.900; Premium $47.900 | `agendapro.com/cl` — 2026-10-09 |
| **Medilink** / Medilink LatAm | Chile/LatAm · Centros de salud (incluye odontología) | SaaS 100% nube | Diaria/semanal/global; multi-profesional; multi-sucursal; duración variable; sobreagendamiento paralelo; anti-solapamiento **No evidenciado** | Sí · agendamiento online; asistente virtual WhatsApp 24/7 | Sí · email ilimitado; WhatsApp "gestionado"; Suite IA; encuestas | Ficha clínica por especialidad; presupuestos; odontograma/periodontograma **No evidenciado** | Recaudación/cajas; pagos online; telemedicina; facturación fiscal **No evidenciado** | WhatsApp (parcial); Google Calendar (sí); API **No evidenciado** | **No publicado** (contactar a ventas) | `softwaremedilink.com` — 2026-10-09 |
| **Clinicloud** / Genesys | Chile · Centros médicos pequeños/medianos (no dental) | SaaS + app (PideHora) | Agendas con filtros; jornada con cupos; multi-profesional parcial; multi-sillón **No evidenciado**; anti-solapamiento **No evidenciado** | Sí · app/web PideHora | **No evidenciado** | Ficha médica (no odontológica); odontograma **No evidenciado** | Recaudación; reportes; exportación a Excel | PideHora; WhatsApp/API/fiscal **No evidenciado** | **No evidenciado** | `clinicloud.cl` — 2026-10-09 |

### 2.3 Internacional (12 sistemas)

| Producto / Proveedor | País · Segmento | Modalidad | Agenda (multi-prof. / sillón / duración / bloqueos / anti-solapamiento) | Reserva online / Turnos digitales | Recordatorios / Automatización | Gestión odontológica clínica | Administración / Cobros | Integraciones | Precio publicado | Fuente y fecha |
|---|---|---|---|---|---|---|---|---|---|---|
| **Dentally** / Dentally Ltd | Reino Unido · Clínicas privadas y NHS, multi-sitio | SaaS cloud (navegador) | Multiprofesional y multisitio; agenda por provider; waitlist; **slot reservado 30 min anti-doble-reserva** | Sí · Dentally Portal booking 24/7 | Sí · SMS/email automáticos; recalls (según plan) | Registro clínico completo; Dentally Vision (RX digital); charting; odontograma por nombre **No evidenciado** | Invoices/cobros; pagos online (Stripe/Worldpay/Dojo); Xero; claiming NHS | API pública abierta; pagos; radiología; WhatsApp/Google Calendar **No evidenciado** | desde £125/mes (indicativo, Starter) a £510/mes (Pro) | `dentally.com/en-gb/pricing` — 2026-10-09 |
| **Open Dental** / Open Dental Software Inc. | EE.UU. · Self-hosted, consultorios 1–3+ | Licencia + soporte mensual (self-hosted) | Gráfica con block scheduling; por provider; multi-localización; control de operatory; anti-solapamiento **No evidenciado** explícito | Sí · Web Sched (4 variantes, add-on con fee) | Sí · eReminders (email gratis; SMS con Integrated Texting); eConfirmations | Charting/perio; odontograma por nombre **No evidenciado**; imágenes vía terceros | Billing; claims; pagos online (Payment Portal); fiscal AR **No evidenciado** | API/BD abierta (MySQL); gran ecosistema; WhatsApp/Google Calendar **No evidenciado** | USD 199/mes localización año 1 → 149/mes; eServices Bundle USD 165/mes | `opendental.com/site/fees.html` — 2026-10-09 |
| **Curve Dental** / Curve Dental, Inc. | EE.UU./Canadá · Cloud all-in-one | SaaS navegador | Scheduling; multi-provider/operatory; **anti-doble-booking en tiempo real**; duración variable **No evidenciado** | Sí · self-scheduling 24/7 (Curve GRO incluido) | Sí · text/email automatizados; campañas; Smart Fill (A) | Charting restaurativo y perio; imaging nativo; planes chairside; odontograma por nombre **No evidenciado** | Billing; eClaims ilimitado; ERA/EFT auto-posting; Curve Pay; analytics | Google Calendar/Outlook/iCal (A); WhatsApp/API **No evidenciado** | **No publicado** (cotización); tercero ~USD 4.794/año | `curvedental.com/pricing` — 2026-10-09 |
| **Dentrix Ascend** / Henry Schein One | EE.UU. · Cloud-native, multi-localización/DSO | SaaS, usuarios ilimitados | Control por tipo de cita, bloques, disponibilidad por provider/ubicación; **sincronización en tiempo real**; sobreturnos **No evidenciado** | Sí · booking nativo + Reserve with Google | Sí · text/email/phone; +66M enviados; Campaign Studio | Charting consolidado; imaging 2D/3D/CBCT; Voice Perio; odontograma por nombre **No evidenciado** | Claims; elegibilidad; ERA auto-posting; pagos integrados | Reserve with Google; athenahealth; 270+ integraciones (desktop) | **No publicado** (terceros estiman USD 500–1.200/mes) | `dentrixascend.com` — 2026-10-09 |
| **CareStack** / CareStack Inc. | EE.UU. · Cloud all-in-one, solos a DSO | SaaS sin add-ons | Multi-specialty; scheduler personalizable; búsqueda de huecos multi-sitio/provider/operatory; bloqueos/sobreturnos **No evidenciado** | Sí · Patient Portal (direct booking / request / mensaje) | Sí · SMS/email/voz; dashboard; AI teammates | Charting/perio; imaging "FDA-Cleared"; planes; AI notes/X-ray | Claims; elegibilidad; MMS/bulk texting; billing; KPIs | Reserve with Google; Google Analytics; WhatsApp/API **No evidenciado** | Essentials desde USD 829/mes; Intelligence desde USD 1.299/mes | `carestack.com/pricing` — 2026-10-09 |
| **tab32** / tab32, Inc. | EE.UU. · Cloud (GCP); Alpine y Summit | SaaS | Multi-provider/multi-localización; ASAP list/waitlist; gestión de operatory/chair; **prevención de doble reserva (tiempo real)** | Sí · HelloPatient online booking; portal sin login | Sí · AutoRemind (gratis año 1 en Alpine; 500 msg/mes); reactivación | Clinical charting y planes; imaging; AI radiology (PiAI); **odontograma/perio comprobado** (corrección C-05) | Billing/payments (Stripe); claims usage-based; ERAs; A/R; analytics | Stripe; GCP; data warehouse/SSO; WhatsApp/Google Calendar **No evidenciado** | Alpine USD 125/mes año 1 → 225/mes; Summit a medida; trial 14 días | `tab32.com/pricing/` — 2026-10-09 |
| **Denticon** / Planet DDS | EE.UU. · Cloud, multi-localización/DSO | SaaS por suscripción | Scheduling avanzado; Find a Slot; programación multi-localización; bloques/sobreturnos **No evidenciado** | Sí · online scheduling incluido; portal paciente; 2-way texting | Sí · recordatorios nativos; campañas; DentalOS AI Agents | Tratamiento planning; imaging nativa; voice perio; módulos de especialidad; odontograma por nombre **No evidenciado** | eClaims ilimitados; 835 auto-posting; elegibilidad; payments; RCM | 50+ APIs; WhatsApp/Google Calendar **No evidenciado** | desde USD 795/mes; export de datos USD 995 | `planetdds.com/denticon` — 2026-10-09 |
| **Eaglesoft** / Patterson Dental | EE.UU. · On-premise Windows | On-premise (servidor) | Color-coded; por provider/familias; QuickFill; bloqueos; **doble-book documentado**; anti-solapamiento **No evidenciado** | Sí · online scheduling (planes Professional/Growth) | Sí · eReminders (fee USD 80–380/mes); recalls; eConfirmations | Tooth charting interactivo; Smart clinical notes; Advanced Imaging; perio por nombre **No evidenciado** | Billing; walkout; Smart Claim/Invoice; eClaims/eRA/RTE; pagos online | 55+ eServices; marketplace de terceros; WhatsApp/Google Calendar **No evidenciado** | **No publicado** (Service Club; eReminders USD 80–380/mes) | `pattersondental.com/.../eaglesoft` — 2026-10-09 |
| **SoftDent** / Carestream Dental (Sensei) | EE.UU. · On-premise y hosted | On-premise/hosted | Scheduler completo (Daily/Book At A Glance/Month/History/Tickler); color/goal scheduling; slots bloqueados; multi-operatory; sobreturnos **No evidenciado** | **No evidenciado** (booking online no documentado públicamente) | Sí · eReminders (opcional); eConfirmations; Missed Appointments report | Patient charts; charting/planes; integración nativa imagen Carestream; odontograma por nombre **No evidenciado** | Billing; insurance tracking; reportes; eClaims/eRA (eSuite) | Imagen Carestream; eServices/Patient Manager; WhatsApp/API **No evidenciado** | **No publicado** (terceros estiman USD 199–399/mes) | `carestreamdental.com` — 2026-10-09 |
| **iDentalSoft** / iDentalSoft, Inc. | EE.UU. (corrección del briefing: **no España**) · Cloud, un consultorio a multi-sitio | SaaS cloud | Smart Scheduler drag-and-drop; cada provider hasta 8 operatories con **citas solapadas**; multi-oficina; bloqueos **No evidenciado** | Sí · portal paciente self-scheduling 24/7; kiosk/BYOD check-in | Sí · email/SMS incluidos; recall; campañas; AI Front-Desk (opcional) | EHR/EMR completo; **odontograma 3D (comprobado)**; perio con voz; imaging nativa (TWAIN); e-Rx | eClaims ilimitado; ERA/e-EOB; elegibilidad; payment plans; payroll; KPIs | **WhatsApp integrado** (opción paga — único intl del relevamiento); VoIP; Zoom; HL7; API **No evidenciado** | desde USD 395/mes (Starter); fee por práctica | `identalsoft.com/dental-software-pricing` — 2026-10-09 |
| **Dentisoft** / Dentisoft Technologies | EE.UU. · Cloud básico, consultorios chicos | SaaS cloud | PMS con scheduling; sin detalle público; conflictos **No evidenciado** | **No evidenciado** | **No evidenciado** | Gestión clínica y radiografía online; odontograma/perio **No evidenciado** | Billing genérico; reportes **No evidenciado** | Facebook, DentistDirectory; radiografía online; WhatsApp/API **No evidenciado** | Cloud Starter "Get started FREE"; Cloud Pro USD 50 → 249/mes | `dentisoft.com` — 2026-10-09 |
| **DentalSoft.es** / DentalSoft (España) | España · On-premise, pago único | On-premise | Día/semana; avisos SMS día anterior con confirmación; odontograma evolutivo; ficha de ortodoncia | **No evidenciado** (sin motor de reserva online evidenciado) | Sí · SMS día anterior con confirmación/cambio/anulación | Odontograma evolutivo; ficha de ortodoncia; radiografías/TAC; firma digital | Módulo de caja; enlace contable (recibos SEPA); CRM de recuperación | Web de pacientes; sin cloud; WhatsApp/API **No evidenciado** | Pago único (sin cuotas por usuario); importe **No evidenciado** | `dentalsoft.es` — 2026-10-09 |

### 2.4 Otros referentes LatAm (ampliación, sin plantilla completa)

Estos sistemas aparecieron en las búsquedas con evidencia pública suficiente, pero no se relevaron con la plantilla completa. Se incluyen como pista para un profundizado posterior.

| Producto | País | Segmento | Hallazgo clave (fuente, consultada 2026-10-09) |
|---|---|---|---|
| ClinicQ | Ecuador | Odontología con IA | Agenda por doctor/sillón con **"validación en tiempo real doctor y sillón"**; recordatorios WhatsApp con botones; bot Zuri IA; facturación SRI; precios USD 15/30/40. `clinicq.cloud` |
| MR Dental Cloud | México | Odontología | Bot WhatsApp que agenda 24/7; recordatorios 24/12/4/1h; NOM-004/COFEPRIS declarado; precios MXN publicados. `mrdentalcloud.com` |
| Denty.Cloud | México | Odontología | Recordatorios WhatsApp/email; odontograma y periodontograma; precios MXN publicados; API de agenda online. `denty.cloud` |
| Dentalware | Chile | Odontología | Precios con IVA publicados; portal de agendamiento; WhatsApp en plan Impulso; migración desde Dentalink. `dentalware.cl/precios` |
| OdontoCloude | LatAm (multi-país) | Odontología | Precios en USD; odontograma/periodontograma en todos los planes; **declara NO emitir CFDI/DIAN ni comprobantes de obras sociales**. `odontocloude.com` |
| XDentalCloud | LatAm (factura USD, empresa USA) | Odontología | Precios EUR/USD; odontograma/periodontograma; portal del paciente y teleodontología opcionales. `xdentalcloud.com/precios` |
| Quiero Agendar | Chile | Belleza/salud (agenda liviana) | Alternativa liviana a Dentalink: plan gratis (1 dentista, 5 reservas/sem), link público, recordatorios email; se posiciona contra los EHR dentales caros. `quieroagendar.cl` |

**Pie de tabla:** todas las celdas marcadas **No evidenciado** corresponden a funcionalidades que no pudieron respaldarse con fuente pública verificable al 2026-10-09; **no** se dedujeron por analogía con otros productos del mismo proveedor o segmento. Las celdas marcadas `(A)` son **afirmaciones comerciales** del proveedor sin demostración pública y no equivalen a funcionalidad comprobada. Los precios se expresan en la moneda del sitio de origen y corresponden al valor publicado al momento de la consulta.

---

## 3. Sección B — Matriz de puntuación

Se puntúan los **20 sistemas más relevantes para Argentina** (ver criterio en la nota metodológica). Las notas **0–5** por celda provienen de la evidencia registrada en los raw (`docs/discovery/raw/`); el **total ponderado** es la suma de `nota × peso`.

### Pesos de los criterios (exactos)

| Criterio | Peso |
|---|---|
| Gestión de turnos y automatización | 25% |
| Funcionalidad odontológica clínica | 20% |
| Integraciones locales y WhatsApp | 15% |
| Administración, cobros y facturación | 15% |
| Experiencia del paciente | 10% |
| Seguridad, exportación y trazabilidad | 10% |
| Precio y facilidad de adopción | 5% |
| **Total** | **100%** |

### Matriz (nota 0–5 por criterio · total ponderado)

| # | Sistema (país) | Turnos / automat. (25%) | Clínica odonto. (20%) | Integr. locales / WhatsApp (15%) | Admin. / cobros (15%) | Experiencia paciente (10%) | Seguridad / export. / trazab. (10%) | Precio / adopción (5%) | **Total ponderado** |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Dentiqa (LatAm AR) | 5.0 | 5.0 | 4.5 | 3.5 | 4.5 | 4.5 | 3.0 | **4.50** |
| 2 | DentalSaaS (AR) | 4.0 | 5.0 | 3.5 | 5.0 | 4.0 | 5.0 | 3.0 | **4.33** |
| 3 | DentalSoft (AR) | 4.5 | 5.0 | 4.0 | 4.5 | 4.0 | 3.0 | 4.0 | **4.30** |
| 4 | Clinicorp (BR) | 4.0 | 4.5 | 5.0 | 5.0 | 3.5 | 2.0 | 4.0 | **4.15** |
| 5 | DoctorYa (AR) | 4.5 | 3.5 | 4.5 | 4.5 | 4.0 | 3.0 | 4.0 | **4.08** |
| 6 | Doctocliq (PE/MX) | 4.5 | 4.0 | 4.0 | 3.5 | 4.5 | 2.5 | 4.0 | **3.95** |
| 7 | iDentalSoft (EE.UU.) | 4.0 | 4.5 | 3.5 | 3.5 | 4.0 | 3.5 | 3.5 | **3.88** |
| 8 | Dentally (UK) | 4.5 | 4.0 | 2.0 | 3.5 | 4.0 | 4.0 | 3.5 | **3.73** |
| 9 | Bilog (AR) | 4.0 | 4.0 | 2.5 | 4.0 | 4.0 | 2.5 | 4.5 | **3.65** |
| 10 | Dentalink (CL) | 3.5 | 5.0 | 2.5 | 4.0 | 3.0 | 2.0 | 3.5 | **3.53** |
| 11 | AgendaPro (CL) | 4.0 | 2.0 | 3.5 | 4.0 | 4.5 | 3.0 | 3.5 | **3.45** |
| 12 | Reservo (LatAm AR) | 3.5 | 3.0 | 4.0 | 4.0 | 3.5 | 2.5 | 3.0 | **3.43** |
| 13 | Nimbo (MX) | 4.0 | 2.5 | 3.5 | 3.5 | 4.0 | 2.5 | 3.0 | **3.35** |
| 14 | Docturno (AR) | 4.0 | 2.0 | 4.0 | 2.0 | 4.5 | 2.0 | 3.0 | **3.10** |
| 15 | DenPro (UE/AR) | 3.0 | 4.0 | 1.5 | 3.0 | 3.0 | 4.0 | 3.0 | **3.08** |
| 16 | Dentora (AR) | 4.0 | 2.0 | 3.0 | 3.0 | 4.0 | 1.5 | 3.0 | **3.00** |
| 17 | Doctoralia (AR) | 4.0 | 1.5 | 3.0 | 1.5 | 5.0 | 2.0 | 5.0 | **2.93** |
| 18 | SimpleTurno (?) | 4.0 | 1.0 | 3.0 | 3.0 | 4.0 | 2.0 | 4.0 | **2.90** |
| 19 | Dental Total (AR) | 3.5 | 0.0 | 1.5 | 0.0 | 4.5 | 0.0 | 3.5 | **1.73** |
| 20 | OdontoApp (AR) | 1.5 | 1.5 | 0.5 | 0.0 | 1.0 | 0.0 | 1.5 | **0.93** |

### Nota metodológica

- **Criterio de selección de los 20 sistemas.** Se priorizó la relevancia para el **mercado argentino**: (a) los **14 sistemas argentinos** del raw (relevancia directa); (b) **4 sistemas LatAm** de referencia cercana por idioma/localización (**Dentalink**, **Clinicorp**, **Doctocliq**, **AgendaPro**); y (c) **2 internacionales** de referencia obligada: **iDentalSoft** (único del relevamiento internacional con WhatsApp integrado publicado) y **Dentally** (mejor referencia de UX de reserva y anti-doble-reserva). El resto de los internacionales (Open Dental, Curve, Ascend, CareStack, tab32, Denticon, Eaglesoft, SoftDent, Dentisoft, DentalSoft.es) se documenta en la Sección A pero no se pondera por su baja aplicabilidad local (modelo de práctica, fiscalidad y canales distintos).
- **Significado de la escala 0–5** (idéntica a la usada en los raw):
  - **0** = sin evidencia (incluye "No evidenciado" y "No aplica").
  - **1–2** = evidencia mínima o **afirmación comercial sin demostración** (p. ej. tagline o listado sin demo).
  - **3** = funcionalidad documentada de forma parcial o con evidencia incompleta.
  - **4** = funcionalidad evidenciada con claridad en sitio/documentación oficial.
  - **5** = funcionalidad **comprobada en fuente pública** (producto, documentación o video oficial) con el mayor nivel de respaldo del relevamiento.
- **Tratamiento de los "No evidenciado".** Se computan como **0** y **afectan la nota negativamente**, de forma consistente en toda la matriz. No se aplica un criterio "neutral" a celdas sin evidencia: la ausencia de respaldo público se penaliza, porque el objetivo del ejercicio es discriminar lo **demostrado** de lo **declarado**.
- **Origen de las notas.** Todas las notas provienen de los puntajes ya asignados por criterio en `docs/discovery/raw/{argentina,latam,internacional}.md`; este informe solo los ordena, los pondera y los agrega. El total ponderado se calcula como `Σ (nota × peso)` con los pesos exactos de la tabla anterior.

---

## 4. Sección C — Análisis competitivo

### 4.1 Funcionalidades estándar del mercado

- **Reserva online 24/7** desde un enlace público o portal del paciente, con confirmación automática. Presente en prácticamente todos los jugadores (Doctoralia, Docturno, DentalSoft, Dentiqa, DentalSaaS, AgendaPro, Doctocliq, y en los internacionales Dentally, Curve, Ascend, CareStack, tab32, Denticon, iDentalSoft).
- **Recordatorios automatizados** por email/SMS/WhatsApp para reducir ausentismo. Es el estándar de facto en LatAm (WhatsApp) y en EE.UU. (text/SMS + email). El "no-show" es el problema transversal que todos atacan.
- **Agenda multi-profesional** con vistas diaria/semanal y, en productos dentales maduros, **gestión por sillón/sala** (Dentalink, Clinicorp, Feegow, AgendaPro).
- **Duración variable por prestación** (agenda que se adapta al tipo de práctica).
- **Ficha clínica y odontograma** como ancla de retención clínica en los productos 100% odontológicos (DentalSoft, DentalSaaS, Dentiqa, Dentalink, Clinicorp, Doctocliq, iDentalSoft).
- **Portal del paciente** con auto-agendamiento, formularios y (en algunos) pagos online.

### 4.2 Diferenciadores reales

- **Odontograma + planes de tratamiento + presupuesto por pieza**: es el verdadero diferencial dental (lo tienen Dentalink, Dentiqa, Clinicorp, Doctocliq, Denty.Cloud), no la agenda. Un sistema puramente de turnos compite en la capa agenda/reserva/recordatorio, pero **el odontograma es el ancla de retención clínica**.
- **Anti-doble-reserva demostrado**: Dentally (reserva el slot 30 min), Dentrix Ascend (sincronización en tiempo real), Curve/tab32 (prevención de doble booking). ClinicQ es el más cercano en LatAm con "validación en tiempo real doctor y sillón".
- **Integraciones locales profundas**: Clinicorp (PIX + NFS-e + API con precio), DoctorYa y Reservo (AFIP/ARCA + obras sociales + WhatsApp + Mercado Pago), AgendaPro y Feegow (certificaciones de salud locales CENS/FONASA y SBIS/ANS).
- **Seguridad con evidencia**: Feegow (SBIS NGS2 + LGPD + backups diarios) y AgendaPro (CENS/FONASA) son los únicos que aportan cumplimiento verificable.
- **Modelo de precios transparente**: los nacidos después de 2020 publican precio (Doctocliq, ClinicQ, Denty.Cloud, Dentalware, DentalSaaS); los instalados cotizan (Dentalink, Ninsaúde, Medilink, Doctoralia solo en planes PRO).

### 4.3 Vacíos frecuentes del mercado argentino

- **Prevención de solapamientos explícita**: **ningún** competidor relevado demuestra públicamente las reglas (borde a borde `[inicio, fin)`, duración derivada de la prestación, colisión por profesional **y** por sillón). Es un hueco de producto aprovechable y es, justamente, la regla que el MVP del TP ataca.
- **Facturación fiscal AFIP/ARCA + Mercado Pago + obras sociales en una sola pieza**: vacío documentado (OP-01). Solo DoctorYa y Reservo lo cubren parcialmente; Doctoralia y Docturno **no** evidencian AFIP/obras sociales.
- **Odontograma integrado a la agenda**: opciones locales existen (DentalSoft/DentalSaaS/Dentiqa), pero Doctoralia/Docturno (los más adoptados) **no** lo tienen evidenciado (OP-02).
- **WhatsApp Business API generalizado**: estándar del mercado, pero evidenciado solo en 2–3 proveedores locales (OP-03).
- **Sincronización con calendarios externos (Google Calendar)**: no evidenciada en Doctoralia ni Docturno (OP-04).
- **Cumplimiento explícito de la Ley 25.326**: raramente declarado; la mayoría solo afirma "seguridad" de forma genérica.

### 4.4 Oportunidades de innovación para un sistema nuevo

1. **Hacer de la correctitud de la agenda el diferencial técnico**: validar solapamiento por profesional **y** por sillón/box, con intervalos semiabiertos y duración derivada de la prestación, demostrable por tests. Es lo que nadie demuestra públicamente en Argentina.
2. **Reserva pública sin fricción**: sin login del paciente, con token de cancelación; es lo que el research respalda (Doctoralia, Dental Total) y reduce la barrera de adopción.
3. **Capa de privacidad visible**: consentimiento explícito en la reserva y no exposición de datos clínicos en rutas públicas (Ley 25.326), como ventaja defendible frente al "seguro" genérico de la competencia.
4. **Roadmap de expansión con evidencia**: recordatorios (WhatsApp), cobros (Mercado Pago) y ficha clínica (odontograma) quedan documentados como backlog v2 — todas con evidencia de mercado que justifica priorizarlas después del núcleo de turnos.

---

## 5. Sección D — Recomendación final

### 5.1 Cinco competidores prioritarios para analizar mediante demo

1. **DentalSoft (AR)** — el competidor odontológico local más completo: reserva 24/7, odontograma FDI, obras sociales/liquidaciones, WhatsApp oficial y Google Calendar.
2. **DentalSaaS (AR)** — mejor cobertura administrativa y de trazabilidad del relevamiento AR (auditoría exportable, liquidación de profesionales, obras sociales/nomenclador).
3. **Dentiqa (AR/LatAm)** — mejor experiencia de paciente con IA (chatbot WhatsApp 24/7), odontograma versionado, periodontograma y WhatsApp Business API oficial.
4. **DoctorYa (AR)** — la mejor combinación de "localización argentina" (WhatsApp + Mercado Pago + AFIP/ARCA + obras sociales/copagos) para estudiarla como referencia funcional.
5. **Clinicorp (BR)** — referencia regional de administración/cobros e integraciones con precio publicado (PIX, NFS-e, API), útil para benchmark de completitud.

### 5.2 Tres productos de referencia para experiencia de usuario

1. **Doctoralia (AR)** — referencia de descubrimiento y reserva (directorio, reseñas verificadas, reserva multicanal incluido Google).
2. **Dentally (UK)** — referencia de portada de reserva 24/7 con **slot reservado 30 min** anti-doble-reserva y portal de autogestión del paciente.
3. **Doctocliq (PE/MX)** — referencia de journey digital de reserva (link en redes, confirmación desde el mismo mensaje, app móvil).

### 5.3 MVP sugerido

> Consistente con `knowledge-base/01_vision_y_objetivos.md` (Alcance v1.0) y `CHANGES.md` (camino crítico del núcleo de turnos).

**Imprescindible (núcleo del MVP):**

- Reserva online **pública, sin login del paciente** (profesional → fecha → franja disponible → datos de contacto), con consentimiento (Ley 25.326).
- **Anti-solapamiento por profesional y por sillón/box**, con intervalos semiabiertos `[inicio, fin)` y validación en la capa de servicios.
- **Duración derivada de la prestación** (`fin = inicio + duracion_minutos`); estados de turno `reservado → confirmado → completado` (y `cancelado`).
- **Agenda diaria/semanal** por profesional (turnos + bloqueos) y gestión de profesionales, prestaciones, sillones y bloqueos.
- **Autenticación JWT con RBAC** para admin/odontólogo (el odontólogo solo ve/modifica turnos de su `profesional_id`).
- Cancelación del paciente por **token** (sin login).

**Diferenciador (lo que nos separa del mercado local):**

- Correctitud demostrable de la agenda (anti-solapamiento por profesional **y** sillón, cubierto con tests unitarios y de integración) — nadie lo demuestra públicamente.
- Privacidad explícita desde el diseño: consentimiento registrado, sin datos clínicos ni de terceros en rutas públicas.

**Etapas posteriores (backlog v2/v3, **fuera** de v1):**

- Recordatorios automáticos por WhatsApp/email (US-101).
- Cobros/señas con Mercado Pago y facturación fiscal AFIP/ARCA (US-102).
- Ficha clínica/odontograma/anamnesis (US-103).
- Notificaciones al profesional ante cancelaciones (US-104) e integraciones externas (Google Calendar, WhatsApp Business API).

> **Excluido de v1 de forma explícita:** recordatorios, cobros, ficha clínica y cualquier integración externa (coincidente con DD-06 y el alcance v1.0 de la KB).

---

## 6. Verificación de fuentes

**Método (resumen de `docs/discovery/verificacion-fuentes.md`):** se re-verificaron **55 URLs** mediante `Invoke-WebRequest` (status HTTP + `<title>`) y/o `webfetch`, con confirmación por búsqueda secundaria cuando hubo bloqueo anti-bot. Veredictos: ✅ Comprobado (HTTP 200 + título coherente), ⚠️ Corregir (URL muerta/cambiada o dato desactualizado) y 🔒 Bloqueo anti-bot (producto real confirmado por otra vía). Resultado global: **46 comprobadas**, **4 bloqueos anti-bot**, **4 URLs a corregir** y **0 productos inventados**.

**Verificación a fondo de 6 fuentes (una por tipo):**

| # | Fuente (tipo) | Qué afirmaba el informe | Qué se encontró | Corrección / resultado |
|---|---|---|---|---|
| 1 | **Dentally Ltd** (SaaS dental internacional, `dentally.com`) | Precios "indicativos desde £125/mes"; estructura 1 consultorio→multisitio | Página de pricing con slider por nº de surgeries; Starter £125/mes; Dentally Vision; Dentally Portal | Consistente con el raw (sin cambios) |
| 2 | **tab32** (SaaS cloud EE.UU., `tab32.com`) | "Odontograma/periodontograma: **No evidenciado**" | La página vigente lista "Clinical Charting — **Odontogram, perio charting**…" y AutoRemind incluido año 1 | **Corregido** (C-05, C-06): pasa a **Comprobado** |
| 3 | **Eaglesoft — Patterson Dental** (legacy on-premise) | 55+ integraciones, Service Club, manual de charting | URL devuelve **HTTP 403** al bot; producto confirmado por URL indexada y PDF oficial | 🔒 Bloqueo documentado, producto real (sin cambios de datos) |
| 4 | **SoftDent — Carestream/Sensei** (documentación/ catálogo + prensa) | Documentación pública escasa; soporte migró a Sensei | Confirmado: manual oficial, nota 2014 (Cloud HIPAA), `gosensei.com` | Consistente con el raw |
| 5 | **AgendaPro** (marketplace móvil, App Store CL) | Adopción "50.000 negocios"; precios publicados | Ficha 4.8★/782 calificaciones, Gunei Investment SPA, planes en CLP, prueba 14 días | Consistente (producto activo) |
| 6 | **DentalSoft AR** (SaaS local, `dentalsoft.com.ar`) | Odontograma, obras sociales, WhatsApp, reserva online | Sección de funcionalidades vigente confirma todo eso (deep check) | Consistente y verificada a fondo |

**Correcciones reales registradas (sección 3 de `verificacion-fuentes.md`):**

- **URLs muertas / cambiadas (generan 404 o redirección indebida):**
  - **C-01** — `profesionales.docturno.com/planes` → **404** (la base `profesionales.docturno.com` existe). Corregir la cita.
  - **C-02** — `doctorya.com.ar/planes` → **redirige a `/login`**; la lista de precios ya no es pública → re-marcar "precios publicados" como **ya no públicos**.
  - **C-03** — `simpleturno.com/precios` → **404** (existen `simpleturno.com` y `/rubros/odontologia`). Corregir la cita.
  - **C-04** — `nimbo-x.com/ar/clinica-dental` → **404** (existen `/ar` y `/ar/precios`). Corregir la ruta.
- **Correcciones de contenido detectadas:**
  - **C-05** — tab32: "odontograma/periodontograma No evidenciado" → **Comprobado** (el charting incluye odontograma y perio).
  - **C-06** — tab32: el raw no detallaba AutoRemind → la página vigente indica **"AutoRemind — Included Year 1, 500 mensajes/mes, luego USD 69/mes, overage USD 0,08/msg"**.
  - **C-07** — `pro.doctoralia.com/ar` responde **200 con `www`**; la URL original es válida (sin cambio de contenido).
- **Notas de integridad del repo:** los raw citan notas internas `discovery/sources/{doctoralia-argentina,dental-total,tm-dental}.md` que **no existen** en el repositorio (referencias a limpiar o crear). Se desambiguaron y verificaron 4 marcas "DentalSoft/Dentisoft" distintas (AR, España, EE.UU., Perú), todas con dominio propio.

---

## 7. Referencias completas

Todas las URLs listadas fueron consultadas el **2026-10-09** (salvo aclaración). Agrupadas por región de origen del relevamiento.

### 7.1 Argentina (`docs/discovery/raw/argentina.md`)

- Doctoralia (pacientes): https://www.doctoraliar.com/ — 2026-10-09
- Doctoralia PRO (precios): https://pro.doctoralia.com/ar/precio — 2026-10-09
- Docturno (directorio): https://www.docturno.com/ — 2026-10-09
- Docturno (profesionales): https://profesionales.docturno.com/ — 2026-10-09
- Dental Total: https://dentaltotal.com.ar/ — 2026-10-09
- Dental Total (portal de turnos): https://turnos.dentaltotal.com.ar/ — 2026-10-09
- Reservo: https://reservo.cl/ · https://agendamiento.reservo.cl/ — 2026-10-09
- Reservo (precios AR): https://agendamiento.reservo.cl/precios/ar — 2026-10-09
- DentalSoft: https://dentalsoft.com.ar/ · https://dentalsoft.com.ar/funcionalidades — 2026-10-09
- Dentiqa (AR): https://dentiqa.app/ar — 2026-10-09
- DoctorYa: https://doctorya.com.ar/ — 2026-10-09
- DentalSaaS: https://dental.delriotech.com.ar/ — 2026-10-09
- Bilog: https://bilog.com.ar/ — 2026-10-09
- Dentora: https://dentora.com.ar/ · https://dentora.com.ar/precios — 2026-10-09
- DenPro: https://denpro.ar/ · https://denpro.ar/precios — 2026-10-09
- SimpleTurno: https://simpleturno.com/ · https://simpleturno.com/rubros/odontologia — 2026-10-09
- OdontoApp: https://odontoapp.com.ar/ — 2026-10-09
- Nimbo (AR): https://www.nimbo-x.com/ar · https://www.nimbo-x.com/ar/precios — 2026-10-09
- TurnosWeb (descartado): https://turnosweb.com/ — 2026-10-09

### 7.2 Latinoamérica (`docs/discovery/raw/latam.md`)

- Dentalink (planes): https://www.softwaredentalink.com/cl/planes · https://www.softwaredentalink.com/experiencia-de-pacientes/agenda — 2026-10-09
- Clinicorp: https://www.clinicorp.com/ · https://www.clinicorp.com/planos — 2026-10-09
- Feegow Clinic: https://feegowclinic.com.br/ · https://feegowclinic.com.br/precos-e-planos · https://feegowclinic.com.br/funcionalidades/agenda — 2026-10-09
- Ninsaúde: https://www.ninsaude.com/pt-br/software-odontologia/ — 2026-10-09
- Doctocliq: https://www.doctocliq.com/ · https://www.doctocliq.com/planes-y-precios · https://www.doctocliq.com/agenda-medica-y-recordatorios — 2026-10-09
- AgendaPro: https://agendapro.com/cl · https://agendapro.com/es/dental/software-odontologico — 2026-10-09
- Medilink: https://www.softwaremedilink.com/ · https://www.softwaremedilink.com/odontologia · https://www.softwaremedilink.com/agenda-medica — 2026-10-09
- Clinicloud: https://www.clinicloud.cl/ — 2026-10-09
- Otros referentes (ampliación): https://clinicq.cloud/ · https://www.mrdentalcloud.com/ · https://www.denty.cloud/ · https://dentalware.cl/precios/ · https://odontocloude.com/ · https://xdentalcloud.com/precios/ · https://www.quieroagendar.cl/aprende/alternativa-a-dentalink — 2026-10-09

### 7.3 Internacional (`docs/discovery/raw/internacional.md`)

- Dentally: https://www.dentally.com/en-gb/pricing · https://www.dentally.com/en-gb/resources/faqs — 2026-10-09
- Open Dental: https://opendental.com/site/fees.html · https://www.opendental.com/site/websched.html · https://opendental.com/site/ereminders.html — 2026-10-09
- Curve Dental: https://www.curvedental.com/pricing · https://www.curvedental.com/ — 2026-10-09
- Dentrix Ascend: https://www.dentrixascend.com/ — 2026-10-09
- CareStack: https://carestack.com/pricing · https://carestack.com/dental-software/features/online-scheduling — 2026-10-09
- tab32: https://tab32.com/pricing/ · https://tab32.com/platform/ — 2026-10-09
- Denticon (Planet DDS): https://www.planetdds.com/denticon/ — 2026-10-09
- Eaglesoft (Patterson): https://www.pattersondental.com/cp/software/dental-practice-management-software/eaglesoft — 2026-10-09
- SoftDent (Carestream): https://www.carestreamdental.com/ — 2026-10-09
- iDentalSoft: https://www.identalsoft.com/dental-software-pricing · https://www.identalsoft.com/faq — 2026-10-09
- Dentisoft: https://www.dentisoft.com/ — 2026-10-09
- DentalSoft.es: https://dentalsoft.es/ — 2026-10-09
- Agregadores/terceros consultados: https://apps.apple.com/cl/app/agendapro-agendar-citas-y-m%C3%A1s/id1218956898 · https://www.getapp.com/healthcare-pharmaceuticals-software/a/curve-dental-hero/ · https://costbench.com/software/dental-software/curve-dental/ · https://pickmypms.com/software/denticon/ · https://www.softwareadvice.com/dental/softdent-profile/ · https://www.themolarreport.com/reviews/open-dental — 2026-10-09

### 7.4 Documentos internos citados

- `docs/discovery/raw/argentina.md` · `docs/discovery/raw/latam.md` · `docs/discovery/raw/internacional.md` — research de mercado (2026-10-09)
- `docs/discovery/verificacion-fuentes.md` — verificación de 55 URLs y registro de correcciones (2026-10-09)
- `docs/explore/relevamiento-crear-turno-sin-solapamientos.md` — relevamiento previo del change núcleo (2026-10-10)
- `knowledge-base/01_vision_y_objetivos.md`, `knowledge-base/04_modelo_de_datos.md`, `knowledge-base/05_reglas_de_negocio.md`, `knowledge-base/06_funcionalidades.md`, `knowledge-base/09_decisiones_y_supuestos.md`, `knowledge-base/10_preguntas_abiertas.md` y `CHANGES.md`

> **Aviso de privacidad:** este informe se elaboró exclusivamente con información pública de proveedores de software. No contiene datos reales de pacientes (RN-DATOS-03).
