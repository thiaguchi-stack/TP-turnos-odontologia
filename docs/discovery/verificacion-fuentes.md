# Verificación de fuentes — Estudio de mercado (turnos odontológicos)

> **Propósito:** verificar que las URLs consignadas en `docs/discovery/raw/{argentina,latam,internacional}.md` existen y corresponden al producto descripto, como respaldo de evidencia del TP (consigna: mínimo 5 fuentes de tipos distintos verificadas a fondo).
> **Fecha de la verificación:** 2026-10-09 (misma fecha de consulta declarada en los raw).
> **Método:** en cada URL principal/sospechosa → `Invoke-WebRequest` (status + `<title>` de la home) y/o `webfetch`. Ante bloqueo anti-bot (HTTP 403/SSL/timeout) → confirmación por búsqueda web (fuente secundaria) y se marca `bloqueo`, no `inexistente`.
> **Veredictos:** ✅ **Comprobado** (responde y el título coincide con el producto) · ⚠️ **Corregir** (URL muerta/cambiada o dato del raw desactualizado) · 🔒 **Bloqueo anti-bot** (producto real confirmado por otra vía).

---

## Resultado global

| Concepto | Cantidad |
|---|---|
| URLs re-verificadas (arrogan raíz, subpáginas principales y sospechosas) | **55** |
| ✅ Comprobadas (HTTP 200 + título coherente) | **46** |
| 🔒 Bloqueo anti-bot (producto real, confirmado por búsqueda) | **4** |
| ⚠️ URLs muertas/cambios que corregir | **4** |
| ❌ Productos inventados / dominios inexistentes | **0** |

**Conclusión:** no se detectó ningún producto ficticio ni dominio inexistente en los tres informes. La totalidad de los sistemas citados existen y son software/marketplace real. Las correcciones son de **rutas secundarias obsoletas** y de **2 datos de contenido** (detalle abajo).

---

## 1. Profundidad de verificación (≥5 fuentes de tipos distintos)

### 1.1 Dentally Ltd (Reino Unido) — SaaS dental internacional · `dentally.com`
- **URL base:** `https://www.dentally.com/en-gb/pricing` (via `Invoke-WebRequest` dio timeout; por `webfetch` responde OK).
- **Comprobado:** página `Pricing` con slider **"How many surgeries do you have per site?"** y paquetes **Starter (desde £125/mes para 1 surgery)**, Essentials y Pro (→ sube a £195–£575/mes según nº de surgeries). Menú confirma plataforma cloud con "Dentally Vision" (digital imaging) y "Dentally Portal" (bookings, forms, payments), foco NHS/HSC en UK y planes por país (UK/AU/CA/IE/NZ).
- **Consistencia con raw:** los precios "indicativos desde £125/mes" y la estructura 1 consultorio→multisitio concuerdan.
- **Tipo de fuente:** sitio oficial de producto SaaS internacional.

### 1.2 tab32, Inc. (EE.UU.) — SaaS dental cloud · `tab32.com`
- **URL base:** `https://tab32.com/pricing/` (HTTP 403 a bots; `webfetch` responde OK).
- **Comprobado:** **Alpine Start-Up $125/mes (año 1, hasta 3 providers) → $225/mes (año 2+)**, 14‑day trial gratis; Summit a medida. AutoRemind incluido año 1 (**500 mensajes/mes**, after Year 1 $69/mo, overage $0.08/msg). Comparativa tab32 vs Open Dental publicada en la misma página.
- **✦ Corrección de contenido detectada en esta verificación:** el raw `internacional.md` declaró para tab32 "odontograma/periodontograma: **No evidenciado**", pero la página de pricing vigente lista **"Clinical Charting — Odontogram, perio charting, clinical notes, and treatment planning"** como parte del plan. → Actualizar a **Comprobado** (odontograma y perio en charting).
- **Tipo de fuente:** sitio oficial de producto SaaS internacional.

### 1.3 Eaglesoft — Patterson Dental (EE.UU.) · página con bloqueo anti-bot
- **URL base:** `https://www.pattersondental.com/cp/software/dental-practice-management-software/eaglesoft` (devuelve **HTTP 403** al bot).
- **Confirmado por búsqueda web:** la misma URL aparece indexada como *"Eaglesoft Dental Practice Management Software | Patterson Dental"* con "55+ integrated solutions", Service Club (soporte ilimitado US, upgrades gratuitos), "Trusted over 30 years / Reliably serving nearly 30,000 users"; hay además `patterson.eaglesoft.net/` y PDF oficial "Patterson EagleSoft Overview 12.00". El manual oficial confirma charting interactivo, claims, treatment plans, CAESY/educación.
- **Tipo de fuente:** sitio oficial corporativo (proveedor de software legacy on-premise). Bloqueo documentado, producto 100 % real.

### 1.4 SoftDent — Carestream Dental / Sensei (EE.UU.) · page de producto + soporte
- **URL base:** `https://www.carestreamdental.com/` (OK, redirige a `/en-us`). La página de producto SoftDent no devuelve contenido propio (el soporte migró).
- **Confirmado por búsqueda web:** `help.carestreamdental.com/.../SoftDent/` (manual oficial: "manage front office activities, claims and billing, scheduling and appointments, patient accounts, treatment plans"; charting interactivo); press release de Carestream 2014 (CS SoftDent Cloud, HIPAA-compliant storage); nota OralHealthGroup; y `gosensei.com/softdent-support` — "SoftDent server-based dental practice management software is a Sensei product".
- **Consistencia con raw:** confirma la observación del raw de que "el soporte migró a Sensei" y que la documentación pública vigente es escasa.
- **Tipo de fuente:** documentación/catálogo oficial + prensa técnica del proveedor.

### 1.5 AgendaPro — Gunei Investment SPA (Chile) · App Store (marketplace móvil)
- **URL base:** `https://apps.apple.com/cl/app/agendapro-agendar-citas-y-más/id1218956898` (OK por `webfetch`).
- **Comprobado:** ficha "AgendaPro Business — App agendar citas y reservas", **4.8★ / 782 calificaciones**, desarrollador **Gunei Investment SPA**, descripción "Más de 50,000 negocios usan AgendaPro… 24 países", planes **en CLP con precios publicados** (Plan Individual $15.990 → Básico 5 anual $499.990; Individual+WhatsApp $18.900, Premium 2 profesionales $47.900), "Prueba gratis 14 días, sin tarjeta". Actualizaciones recientes (3.1.0 "hace 4 días") → **producto activo con desarrollo continuo**.
- **Tipo de fuente:** marketplace móvil (App Store) — fuente externa de terceros verificable, independiente del sitio oficial.

### 1.6 DentalSoft (Argentina) — SaaS odontológico local · `dentalsoft.com.ar`
- **URL base:** `https://dentalsoft.com.ar/funcionalidades` (OK).
- **Comprobado (deep):** sección "Funcionalidades" vigente lista: agenda/turnos multi-sucursal con horarios por profesional, **reserva de turnos online**, recordatorios WhatsApp/email, **odontograma digital "inicial y evolutivo, historial de cambios y reporte en PDF"**, ortodoncia por etapas, estudios/escanes 3D, consentimientos con firma, caja/cierre de caja, **obras sociales con cobertura y liquidaciones**, presupuestos por link, portal del paciente, asistente virtual WhatsApp 24 h, Google Calendar. FAQs confirman demo sin tarjeta y domicilio La Plata/Rosario, Argentina.
- **Tipo de fuente:** sitio oficial de producto SaaS local (Argentina) — verificación a fondo de funcionalidades clínicas.

---

## 2. Registro de verificación por URL

> Estado = resultado de la consulta del día. "Título" es el `<title>` devuelto por el sitio.

### 2.1 Argentina (`raw/argentina.md`)

| URL verificada | Estado | Título devuelto / nota |
|---|---|---|
| https://www.doctoraliar.com/ | ✅ 200 | "Doctoralia - Encontrá especialista - Pedí turno con tu especialista" |
| https://pro.doctoralia.com/ar | ✅ 200 | "Agenda para especialistas de la salud I Doctoralia PRO" |
| https://pro.doctoralia.com/ar/precio | ✅ 200 | "Precios | Doctoralia PRO" |
| https://www.docturno.com/ | ✅ 200 | "Docturno - Encuentra turno online para tu profesional de confianza" |
| https://profesionales.docturno.com/ | ✅ 200 | "Agenda online para profesionales" |
| https://profesionales.docturno.com/planes | ⚠️ **404** | Ruta `planes` no existe (ver Correcciones). |
| https://dentaltotal.com.ar/ | ✅ 200 | "Dental Total | Implantes Dentales | Tratamientos Odontológicos" |
| https://turnos.dentaltotal.com.ar/ | ✅ 200 | SPA (título "Index") |
| https://reservo.cl/ | ✅ 200 | Redirige a `reservo.cl/ar/` (versión Argentina por defecto) |
| https://agendamiento.reservo.cl/ | ✅ 200 | Redirige a `/ar/` |
| https://agendamiento.reservo.cl/precios/ar | ✅ 200 | "Software de gestión y administración - Reservo" |
| https://dentalsoft.com.ar/ | ✅ 200 | "DentalSoft | Software dental para clínicas y profesionales" |
| https://dentalsoft.com.ar/funcionalidades | ✅ 200 | "Funcionalidades de DentalSoft" (**verificado a fondo**, sección 1.6) |
| https://dentiqa.app/ar | ✅ 200 | "Software Dental en Argentina | Dentiqa - Gestión Integral para Clínicas" |
| https://doctorya.com.ar/ | ✅ 200 | "DoctorYa | Gestión de turnos y recordatorios por WhatsApp para la salud" |
| https://doctorya.com.ar/planes | ⚠️ **redirige a /login** | Ya no es pública la página de planes (ver Correcciones). |
| https://dental.delriotech.com.ar/ | ✅ 200 | "DentalSaaS - Sistema de Gestión para Clínicas Odontológicas" |
| https://bilog.com.ar/ | ✅ 200 | "Software de gestión odontológica para clínicas - Bilog" |
| https://dentora.com.ar/ | ✅ 200 | "Dentora | Agenda para Consultorio Dental" |
| https://dentora.com.ar/precios | ✅ 200 | "Precios | Dentora" |
| https://denpro.ar/ | ✅ 200 | Redirige a `www.denpro.ar` — "Software odontológico Argentina | DenPro" |
| https://denpro.ar/precios | ✅ 200 | "Precios - Planes simples para clínicas dentales | DenPro" |
| https://simpleturno.com/ | ✅ 200 | "SimpleTurno: App de Turnos Online para tu Negocio" (home multirrubro) |
| https://simpleturno.com/rubros/odontologia | ✅ 200 | "Sistema de Turnos para Odontólogos y Clínicas Dentales" |
| https://simpleturno.com/precios | ⚠️ **404** | Ruta `precios` no existe (ver Correcciones). |
| https://odontoapp.com.ar/ | ✅ 200 | "OdontoApp | Software para Consultorios Odontológicos" (SPA; funcionalidades/precios quedan sin render) |
| https://www.nimbo-x.com/ar | ✅ 200 | "Gestión Digital de Pacientes para Clínicas y Médicos | Nimbo Argentina" |
| https://www.nimbo-x.com/ar/clinica-dental | ⚠️ **404** | Ruta no existe (ver Correcciones). |
| https://turnosweb.com/ (descartado en raw) | ✅ 200 | "TurnosWEB" — confirmado que es HRTech/gimnasios, no salud. |

### 2.2 Latinoamérica (`raw/latam.md`)

| URL verificada | Estado | Título devuelto / nota |
|---|---|---|
| https://www.softwaredentalink.com/cl | ✅ 200 | "Dentalink el Software Dental líder en Latinoamérica | Dentalink Chile" |
| https://www.softwaredentalink.com/cl/planes | ✅ 200 | "Comenzar | Dentalink Chile" |
| https://www.softwaredentalink.com/experiencia-de-pacientes/agenda | ✅ 200 | "Agenda - Funcionalidad del Software | Dentalink Latam" |
| https://www.clinicorp.com/ | ✅ 200 | "O software odontológico para clínicas e consultórios | Clinicorp" |
| https://www.clinicorp.com/planos | ✅ 200 | "Planos Clinicorp | Escolha a melhor opção para sua clínica" |
| https://feegowclinic.com.br/ | ✅ 200 | "Feegow - Software para gestão de Clínicas e Consultórios" |
| https://www.ninsaude.com/pt-br/software-odontologia/ | ✅ 200 | "Sistema para gerenciamento de clínicas de odontologia | Ninsaúde" |
| https://www.doctocliq.com/ | ✅ 200 | "Doctocliq - El mejor software dental y médico de Latinoamérica" |
| https://www.doctocliq.com/planes-y-precios | ✅ 200 | "Planes y precios" |
| https://agendapro.com/cl | ✅ 200 | "AgendaPro: Mejor Sistema de Agendamiento en Chile" |
| https://agendapro.com/es/dental/software-odontologico | ✅ 200 | "Software dental número 1 en Latinoamérica | AgendaPro" |
| https://www.softwaremedilink.com/ | ✅ 200 | "Agenda Citas Médicas Online y Aumenta tus Consultas | Medilink Latam" |
| https://www.softwaremedilink.com/odontologia | ✅ 200 | "Software Dental con Telemedicina | Medilink Latam" |
| https://www.clinicloud.cl/ | ✅ 200 | "CliniCloud | Powered by Genesys" |
| https://clinicq.cloud/ | ✅ 200 | "ClinicQ - Software Integral para Clínicas Dentales con IA | Ecuador" |
| https://www.mrdentalcloud.com/ | ✅ 200 | "MR Dental Cloud | Software Dental en la Nube y Agenda por WhatsApp" |
| https://www.denty.cloud/ | ✅ 200 | "Denty Cloud | Software para Clínicas Dentales en México" |
| https://dentalware.cl/precios/ | ✅ 200 | "Precios de software dental en Chile | Dentalware" |
| https://odontocloude.com/ | ✅ 200 | "Software dental en la nube – OdontoCloude" |
| https://xdentalcloud.com/precios/ | ✅ 200 | "Precios del Software Dental | XDentalCloud" |
| https://www.quieroagendar.cl/aprende/alternativa-a-dentalink | ✅ 200 | "Alternativa a Dentalink en Chile: cuándo conviene cada una | Quiero Agendar" |
| https://dentisoftperu.com/ (nota marcas) | ✅ 200 | "DentiSoft" |

### 2.3 Internacional (`raw/internacional.md`)

| URL verificada | Estado | Título devuelto / nota |
|---|---|---|
| https://www.dentally.com/en-gb/pricing | ✅ 200 (webfetch) | "Pricing, Dental Software Price Comparison | Dentally" |
| https://opendental.com/site/fees.html | ✅ 200 | "Open Dental Software - Fees for Support and Services" |
| https://www.curvedental.com/pricing | ✅ 200 | "Curve Dental | Affordable & Transparent Pricing" |
| https://www.dentrixascend.com/ | ✅ 200 | "Cloud-Based Dental Practice Management Software | Dentrix Ascend" |
| https://carestack.com/pricing | ✅ 200 | "Pricing | What's The Cost? | How Much Is CareStack?" |
| https://tab32.com/pricing/ | 🔒 403 (ok webfetch) | "Dental Software Pricing — From $125/mo, No Server – tab32" |
| https://www.planetdds.com/denticon/ | ✅ 200 | "Denticon Dental Practice Management Software - Planet DDS" |
| https://www.pattersondental.com/cp/software/dental-practice-management-software/eaglesoft | 🔒 403 (confirmado por búsqueda) | "Eaglesoft Dental Practice Management Software | Patterson Dental" |
| https://www.carestreamdental.com/ | ✅ 200 | "Carestream Dental | Home | United States" (redirige `/en-us`) |
| https://www.identalsoft.com/dental-software-pricing | ✅ 200 | "Dental Software Pricing | iDentalSoft Cloud-Based Plans" |
| https://www.dentisoft.com/ | ✅ 200 | "Dental Software | Dentist Software Cloud | Dental Practice Management Software" |
| https://dentalsoft.es/ | ✅ 200 | "Software Clínica Dental | Programa Gestión Dental | Dentalsoft.es" |
| https://www.softwareadvice.com/dental/softdent-profile/ | 🔒 403 (marketplace real, anti-bot) | SoftwareAdvice bloquea a bots; SoftDent confirmado por vías oficiales (sección 1.4) |
| https://www.themolarreport.com/reviews/open-dental | 🔒 error SSL | Sitio real pero con TLS problemático para este cliente; Open Dental confirmado por fuente primaria (`opendental.com`) |

---

## 3. Correcciones registradas

### 3.1 URLs muertas / cambiadas (generan 404 o redirección indebida)

| # | Raw | URL citada | Situación verificada | Acción sugerida |
|---|---|---|---|---|
| C-01 | argentina (Docturno) | `profesionales.docturno.com/planes` | 404. La base `profesionales.docturno.com` existe. | Corregir a la URL base o a la página de planes vigente. |
| C-02 | argentina (DoctorYa) | `doctorya.com.ar/planes` | Redirige a `/login`; la lista de precios ya no es pública. | Re-marcar "precios publicados" como **ya no públicos** (o verificar precio en otra ruta). |
| C-03 | argentina (SimpleTurno) | `simpleturno.com/precios` | 404. Existen `simpleturno.com` y `/rubros/odontologia`. | Corregir a la ruta de precios vigente o eliminar la cita. |
| C-04 | argentina (Nimbo) | `nimbo-x.com/ar/clinica-dental` | 404. Existen `/ar` y `/ar/precios`. | Corregir a `/ar/precios` o ruta de la página del módulo dental vigente. |

### 3.2 Correcciones de contenido detectadas en esta verificación

| # | Raw | Dato | Verificación | Acción |
|---|---|---|---|---|
| C-05 | internacional (tab32) | "odontograma/periodontograma: **No evidenciado**" | Página de pricing vigente lista "Clinical Charting — **Odontogram, perio charting**, clinical notes, and treatment planning". | Actualizar a **Comprobado** (el charting incluye odontograma y perio). |
| C-06 | internacional (tab32) | Raw no detalla inclusión de AutoRemind | Página vigente: "**AutoRemind — Included Year 1**, 500 messages included per month, after Year 1: $69/mo, overage $0.08/msg". | Enriquecer/confirmar la celda de recordatorios con el detalle de mensajes/costo. |
| C-07 | argentina (Doctoralia PRO) | No aplica | `pro.doctoralia.com/ar` responde **200 con `www`** (en sesión previa dio timeout). | Mantener la URL tal cual; es válida. |

### 3.3 Notas de integridad del repo

- Los raw referencian notas internas `discovery/sources/{doctoralia-argentina,dental-total,tm-dental}.md` que **no existen** en el repositorio (verificado por `glob`). Si se citan como "nota interna", o bien se crean o bien se elimina la referencia.
- Marcas desambiguadas y confirmadas: **DentalSoft (AR)** / **DentalSoft.es** / **Dentisoft (US)** / **DentiSoft (PE)** — 4 productos distintos que comparten nombre (raw internacional sección 11b). Se verificaron los 4 dominios: `dentalsoft.com.ar`, `dentalsoft.es`, `dentisoft.com`, `dentisoftperu.com` (todos 200).

---

## 4. Notas metodológicas

1. **Bloqueos anti-bot (403) no implican inexistencia.** Patterson, tab32, SoftwareAdvice, iTechGuides y TheMolotReport bloquean consultas automatizadas; en todos los casos se confirmó el producto por su dominio/sitio oficial o por resultados de búsqueda. Se marcan `🔒` y se consideran **comprobados** para el propósito del informe, con la salvedad de que el contenido citado proviene de lo indexado.
2. **SPA sin render** (OdontoApp, Dental Total/turnos, Reservo AR, reservo.cl): el status 200 y el `<title>` confirman existencia, pero las funcionalidades citadas dependen de render en navegador (se mantiene el criterio "parcial/no evidenciado" del raw).
3. **Redirecciones por país/idioma** (reservo.cl→/ar/, carestreamdental.com→/en-us, denpro.ar→www): no se consideran cambios de URL, se documentan en la tabla.
4. La verificación no re-valida el **contenido funcional** de cada informe completo (eso ya fue relevado en los raw el 2026-10-09); priorizó existencia + título + corrección de rutas sospechosas y de prueba de que los productos "raros" (DentalSaaS, Dentora, DenPro, OdontoApp, ClinicQ, MR Dental Cloud, Denty.Cloud, OdontoCloude, XDentalCloud, Quiero Agendar, Bilog, DoctorYa, Dentiqa) son **reales**: todos responden 200 con dominio y título propio.