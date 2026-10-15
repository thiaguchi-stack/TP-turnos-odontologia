# Matriz ponderada consolidada — Discovery turnos/agenda odontológica

> **Insumo:** `discovery/raw/argentina.md`, `discovery/raw/latam.md`, `discovery/raw/internacional.md` (todos consultados 2026-10-09).
> **Consolidado:** 33 productos con ficha completa y puntuación por criterio. Orden: descendente por puntaje ponderado (global, con columna Región).
> **Verificación automática:** `discovery/verificar_matriz.py` (solo stdlib). Reproduce las notas de los raw, recalcula el ponderado y compara contra esta tabla.

---

## Metodología

- **Pesos (idénticos a los usados en los 3 raw, suman 100%):** Turnos/automatización **25%** · Clínica odontológica **20%** · Integraciones locales/WhatsApp **15%** · Admin/cobros/facturación **15%** · Experiencia paciente **10%** · Seguridad/exportación/trazabilidad **10%** · Precio/adopción **5%**.
- **Qué mide cada nota (0–5):** *Turnos/automatización* = reserva, agenda, anti-solapamiento, recordatorios; *Clínica odontológica* = historia clínica/odontograma/periodontograma/imágenes; *Integraciones locales/WhatsApp* = WhatsApp, MercadoPago, Google Calendar, AFIP/ARCA; *Admin/cobros/facturación* = caja, cobros, obras sociales/facturación fiscal; *Experiencia paciente* = descubrimiento, reserva y autogestión; *Seguridad/exportación/trazabilidad* = cumplimiento (Ley 25.326), auditoría, respaldo, exportación; *Precio/adopción* = transparencia de precios y escala declarada.
- **Cálculo del ponderado:** suma de las 7 notas por su peso (escala 0–5), redondeada a 2 decimales (ROUND_HALF_UP). Ej.: Dentiqa = 5.0·0.25 + 5.0·0.20 + 4.5·0.15 + 3.5·0.15 + 4.5·0.10 + 4.5·0.10 + 3.0·0.05 = **4.50**.
- **Convención de evidencia (la de los raw):** *Comprobado (C)* = lo muestra el producto/documentación/video oficial; *Afirmación comercial (A)* = lo declara el proveedor sin demostración pública (incluye métricas de clientes); *No evidenciado* = sin respaldo público verificable (no se deduce).
- **Límites:** la nota refleja **solo evidencia pública** (sesgo de visibilidad: un producto bueno con web opaca puntúa bajo; ej. OdontoApp queda en 0.93 por SPA sin render). No mide calidad técnica ni precio real; para Argentina, varias celdas de "Integraciones locales/WhatsApp", "Admin/cobros/facturación" y "Seguridad" están en "No evidenciado" en casi todos.
- **Filas incompletas:** ninguna. Las 33 fichas de los 3 raw traen las 7 notas completas (rango 0–5, paso 0.5). No se imputó ningún valor.
- **Discrepancias raw vs `informe-discovery.md`:** se priorizó **raw** (fuente primaria del scoring). El informe menciona 34 sistemas; aquí se consolidan los 33 con ficha + puntuación (el restante es un anexo de "otros referentes" del informe, sin ficha puntuada).

---

## Tabla global (orden descendente por ponderado)

| # | Producto | País/Región | Segmento | Turnos 25% | Clínica 20% | Integr. 15% | Admin 15% | Experiencia 10% | Seguridad 10% | Precio 5% | Ponderado | Evidencia | Fuente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Dentiqa | LatAm (AR) | Odontología con IA | 5.0 | 5.0 | 4.5 | 3.5 | 4.5 | 4.5 | 3.0 | 4.50 | Adopción inicial (10 clínicas); caja/obras sociales No evidenciado | raw/argentina.md · https://dentiqa.app/ar |
| 2 | DentalSaaS | Argentina | Odontología 100% | 4.0 | 5.0 | 3.5 | 5.0 | 4.0 | 5.0 | 3.0 | 4.33 | Adopción y AFIP/ARCA No evidenciado | raw/argentina.md · https://dental.delriotech.com.ar/ |
| 3 | DentalSoft | Argentina | Odontología 100% | 4.5 | 5.0 | 4.0 | 4.5 | 4.0 | 3.0 | 4.0 | 4.30 | Adopción sin verificar; AFIP/auditoría No evidenciado | raw/argentina.md · https://dentalsoft.com.ar/ |
| 4 | Clinicorp | Brasil | Odontología y estética | 4.0 | 4.5 | 5.0 | 5.0 | 3.5 | 2.0 | 4.0 | 4.15 | LGPD/auditoría/respaldo No evidenciado | raw/latam.md · https://www.clinicorp.com/ |
| 5 | DoctorYa | Argentina | Turnos + historia clínica | 4.5 | 3.5 | 4.5 | 4.5 | 4.0 | 3.0 | 4.0 | 4.08 | Ley 25.326/auditoría/exportación No evidenciado | raw/argentina.md · https://doctorya.com.ar/ |
| 6 | Doctocliq | Perú/México | Odontología y estética | 4.5 | 4.0 | 4.0 | 3.5 | 4.5 | 2.5 | 4.0 | 3.95 | Pagos online solo Perú; respaldo/auditoría No evidenciado | raw/latam.md · https://www.doctocliq.com/ |
| 7 | iDentalSoft | EE.UU. | Cloud, consultorio a multi-sitio | 4.0 | 4.5 | 3.5 | 3.5 | 4.0 | 3.5 | 3.5 | 3.88 | Único con WhatsApp publicado; fiscal AR/API No evidenciado | raw/internacional.md · https://www.identalsoft.com/ |
| 8 | Dentally | Reino Unido | Clínicas privadas/NHS (cloud) | 4.5 | 4.0 | 2.0 | 3.5 | 4.0 | 4.0 | 3.5 | 3.73 | WhatsApp/Google Calendar No evidenciado | raw/internacional.md · https://www.dentally.com/en-gb/ |
| 9 | Curve Dental | EE.UU./Canadá | Cloud all-in-one | 4.0 | 4.0 | 2.5 | 4.0 | 4.0 | 3.5 | 3.0 | 3.68 | Sin precio público; WhatsApp/local No evidenciado | raw/internacional.md · https://www.curvedental.com/ |
| 10 | CareStack | EE.UU. | Cloud all-in-one, solos a DSO | 4.5 | 4.0 | 2.0 | 4.0 | 4.0 | 3.0 | 3.0 | 3.68 | WhatsApp/API local No evidenciado | raw/internacional.md · https://carestack.com/ |
| 11 | Bilog | Argentina | Odontología 100% | 4.0 | 4.0 | 2.5 | 4.0 | 4.0 | 2.5 | 4.5 | 3.65 | Precio no publicado; WhatsApp/AFIP No evidenciado | raw/argentina.md · https://bilog.com.ar/ |
| 12 | Dentrix Ascend | EE.UU. | Cloud, multi-localización/DSO | 4.0 | 4.0 | 2.5 | 4.0 | 4.0 | 3.0 | 3.0 | 3.63 | Sin precio público; WhatsApp/fiscal AR No evidenciado | raw/internacional.md · https://www.dentrixascend.com/ |
| 13 | Open Dental | EE.UU. | Self-hosted, 1–3+ profesionales | 4.0 | 3.5 | 3.0 | 3.5 | 3.5 | 3.5 | 4.5 | 3.60 | Sin WhatsApp/obras sociales; respaldo a cargo del cliente | raw/internacional.md · https://opendental.com/ |
| 14 | Denticon | EE.UU. | Cloud, multi-localización/DSO | 4.0 | 3.5 | 2.5 | 4.0 | 3.5 | 4.0 | 3.0 | 3.58 | Precio alto y costo de exportación; WhatsApp No evidenciado | raw/internacional.md · https://www.planetdds.com/denticon/ |
| 15 | Dentalink | Chile (CO/MX/ES) | Odontología 100% | 3.5 | 5.0 | 2.5 | 4.0 | 3.0 | 2.0 | 3.5 | 3.53 | Precio no publicado; exportación No evidenciado | raw/latam.md · https://www.softwaredentalink.com/cl |
| 16 | tab32 | EE.UU. | Cloud, solos y grupos/DSO | 4.0 | 3.5 | 2.0 | 3.5 | 4.0 | 3.5 | 4.0 | 3.48 | WhatsApp/calendario local No evidenciado | raw/internacional.md · https://tab32.com/ |
| 17 | AgendaPro | Chile/LatAm | Belleza/salud (vertical dental) | 4.0 | 2.0 | 3.5 | 4.0 | 4.5 | 3.0 | 3.5 | 3.45 | Sin odontograma; auditoría/exportación No evidenciado | raw/latam.md · https://agendapro.com/cl |
| 18 | Reservo | LatAm (AR) | Software médico multirrubro | 3.5 | 3.0 | 4.0 | 4.0 | 3.5 | 2.5 | 3.0 | 3.43 | Todo declarado sin demo; Ley 25.326 No evidenciado | raw/argentina.md · https://reservo.cl/ |
| 19 | Eaglesoft | EE.UU. | On-premise, clínicas privadas | 3.5 | 4.0 | 2.5 | 3.5 | 3.0 | 3.5 | 3.0 | 3.38 | Windows-only; sin precios en sitio | raw/internacional.md · https://www.pattersondental.com/cp/software/dental-practice-management-software/eaglesoft |
| 20 | Nimbo | México/LatAm | Clínica multipropósito, módulo dental | 4.0 | 2.5 | 3.5 | 3.5 | 4.0 | 2.5 | 3.0 | 3.35 | Precios no publicados; AFIP/auditoría No evidenciado | raw/argentina.md · https://www.nimbo-x.com/ar |
| 21 | Feegow Clinic | Brasil | Clínicas médicas/odonto multiprof. | 3.5 | 1.5 | 3.5 | 4.5 | 2.5 | 4.5 | 3.0 | 3.23 | Odontograma/WhatsApp No evidenciado | raw/latam.md · https://feegowclinic.com.br/ |
| 22 | Docturno | Argentina | Directorio + agenda profesionales | 4.0 | 2.0 | 4.0 | 2.0 | 4.5 | 2.0 | 3.0 | 3.10 | Precio no publicado; AFIP/auditoría No evidenciado | raw/argentina.md · https://www.docturno.com/ |
| 23 | DenPro | UE (comercializado en AR) | Odontología 100% | 3.0 | 4.0 | 1.5 | 3.0 | 3.0 | 4.0 | 3.0 | 3.08 | Datos en UE; AFIP/WhatsApp No evidenciado | raw/argentina.md · https://denpro.ar/ |
| 24 | Dentora | Argentina | Odontología 100% | 4.0 | 2.0 | 3.0 | 3.0 | 4.0 | 1.5 | 3.0 | 3.00 | Odontograma no evidenciado; seguridad No evidenciado | raw/argentina.md · https://dentora.com.ar/ |
| 25 | Medilink | Chile/LatAm | Centros de salud (incl. odontología) | 4.0 | 2.5 | 3.0 | 2.5 | 3.5 | 1.5 | 2.5 | 2.95 | Precio no publicado; odontograma/seguridad No evidenciado | raw/latam.md · https://www.softwaremedilink.com/ |
| 26 | Doctoralia | Argentina | Marketplace + agenda (odonto.) | 4.0 | 1.5 | 3.0 | 1.5 | 5.0 | 2.0 | 5.0 | 2.93 | Sin odontograma/WhatsApp/AFIP No evidenciado | raw/argentina.md · https://www.doctoraliar.com/ |
| 27 | SimpleTurno | No evidenciado | Turnos multirrubro (vertical odonto.) | 4.0 | 1.0 | 3.0 | 3.0 | 4.0 | 2.0 | 4.0 | 2.90 | Sin historia clínica; país/moneda No evidenciado | raw/argentina.md · https://simpleturno.com/ |
| 28 | SoftDent | EE.UU. | On-premise y hosted | 2.5 | 3.0 | 1.5 | 3.0 | 2.0 | 3.0 | 2.0 | 2.50 | El caso con más No evidenciado; sin booking online | raw/internacional.md · https://www.carestreamdental.com/ |
| 29 | Ninsaúde Clinic | Brasil | Clínicas/franquias (incl. odonto.) | 2.5 | 2.0 | 2.0 | 3.0 | 2.5 | 1.5 | 2.0 | 2.28 | Precio/WhatsApp/recordatorios No evidenciado | raw/latam.md · https://www.ninsaude.com/pt-br/software-odontologia/ |
| 30 | Dentisoft Technologies | EE.UU. | Cloud básico, consultorios chicos | 2.0 | 2.0 | 1.5 | 2.5 | 2.0 | 3.0 | 3.0 | 2.15 | Sin online booking/automatización No evidenciado | raw/internacional.md · https://www.dentisoft.com/ |
| 31 | Dental Total | Argentina | Red de clínicas (no vende software) | 3.5 | 0.0 | 1.5 | 0.0 | 4.5 | 0.0 | 3.5 | 1.73 | No vende software; seguridad No evidenciado | raw/argentina.md · https://dentaltotal.com.ar/ |
| 32 | Clinicloud | Chile | Centros médicos pequeños/medianos | 1.5 | 0.5 | 1.0 | 2.0 | 2.5 | 1.0 | 1.0 | 1.33 | Solo agenda médica; automatización No evidenciado | raw/latam.md · https://www.clinicloud.cl/ |
| 33 | OdontoApp | Argentina (declarado) | Odontología 100% | 1.5 | 1.5 | 0.5 | 0.0 | 1.0 | 0.0 | 1.5 | 0.93 | Evidencia pública mínima (SPA sin render) | raw/argentina.md · https://odontoapp.com.ar/ |

---

## Resumen

**Cantidad consolidada por región:** Argentina **14** · LatAm **8** · Internacional **11** · **Total 33**.

**Top-10 global (ponderado):**

| Puesto | Producto | Región | Ponderado |
|---|---|---|---|
| 1 | Dentiqa | LatAm (AR) | 4.50 |
| 2 | DentalSaaS | Argentina | 4.33 |
| 3 | DentalSoft | Argentina | 4.30 |
| 4 | Clinicorp | Brasil | 4.15 |
| 5 | DoctorYa | Argentina | 4.08 |
| 6 | Doctocliq | Perú/México | 3.95 |
| 7 | iDentalSoft | EE.UU. | 3.88 |
| 8 | Dentally | Reino Unido | 3.73 |
| 9 | Curve Dental | EE.UU./Canadá | 3.68 |
| 10 | CareStack | EE.UU. | 3.68 |

**Quién lidera cada eje (lectura corta):**

- **Turnos/automatización (25%):** máximo 5.0 en **Dentiqa** (chatbot IA WhatsApp + agenda con bloqueos). 4.5 en DentalSoft, DoctorYa, Doctocliq, Dentally, CareStack.
- **Clínica odontológica (20%):** 5.0 en **Dentiqa**, **DentalSaaS**, **DentalSoft** y **Dentalink**; el odontograma + periodontograma + planes por pieza es el ancla de retención clínica (los internacionales lo esconden como "charting").
- **Integraciones locales/WhatsApp (15%):** **Clinicorp (5.0)** manda con WhatsApp con tarifa publicada + API + NFS-e; en Argentina, **DoctorYa (4.5)** es el más completo (WhatsApp + MercadoPago + AFIP/ARCA).
- **Admin/cobros/facturación (15%):** 5.0 en **Clinicorp** (PIX/boletos/SPC/NFS-e) y **DentalSaaS** (caja, +10 reportes, liquidaciones, obras sociales, stock).
- **Experiencia paciente (10%):** **Doctoralia (5.0)** por el marketplace de dos lados (no es ERP odontológico).
- **Seguridad/exportación/trazabilidad (10%):** el talón de Aquiles regional; solo **DentalSaaS (5.0)**, **Feegow (4.5)** y **Dentiqa (4.5)** muestran algo verificable.
- **Precio/adopción (5%):** **Doctoralia (5.0)** y **Open Dental (4.5)** por transparencia de precios + escala.

**Aprendizajes vs. el alcance del TP (v1: turnos/agenda, sin recordatorios ni cobros):**

- En el eje que el TP sí ataca (**Turnos**, 25%), el techo lo ponen Dentiqa/DoctorYa/DentalSoft (4.5–5.0); el hueco real del mercado es el **anti-solapamiento con reglas explícitas** (borde a borde, duración derivada de la prestación): casi nadie lo demuestra públicamente.
- Para v1 **quedan fuera** recordatorios (throws por WhatsApp/email) y cobros/facturación: justamente los ejes donde empujan los líderes (Clinicorp, DentalSaaS, DoctorYa). El TP compite con la capa **agenda + reserva pública + validación de franjas**, no con el odontograma ni con AFIP.
- La barrera de entrada más dura (facturación local AFIP/ARCA) **ningún** competidor internacional la resuelve para Argentina, y los locales que la tienen (DoctorYa, Reservo) son de agenda/EHR, no de reserva liviana — espacio de posicionamiento para un turnero minimalista.
- **Alcance acotado defendible:** un turnero v1 que gane en *Turnos* + *Experiencia paciente* + *Seguridad básica (Ley 25.326)* sin pretender odontograma, obras sociales ni recordatorios, evitando compararse en los ejes donde los 33 productos relevados ya son fuertes.
