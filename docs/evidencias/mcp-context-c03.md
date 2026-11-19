# Evidencia MCP `context` — C-03 auth JWT/RBAC

Fecha: 2026-11-18. Herramienta: `context_get_docs` (servidor MCP local
`context`, documentación versionada instalada en el repo de tooling). Se
registran las solicitudes exactas, un recorte representativo de cada respuesta y
la decisión de diseño a la que contribuyó.

> Aclaración obligatoria: esta documentación es **apoyo técnico** para confirmar
> firmas y patrones de librería. **Nunca es fuente de reglas de negocio**: los
> claims exigidos, los roles, el rate limit y el algoritmo admitido salen de la
> KB (`knowledge-base/03_actores_y_roles.md`,
> `knowledge-base/05_reglas_de_negocio.md`,
> `knowledge-base/08_arquitectura_propuesta.md`), de `CHANGES.md` y de
> `AGENTS.md`. Ante cualquier conflicto, prevalece la KB.

## Solicitud 1 (fallida, documentada)

```text
context_get_docs(library="fastapi@0.110.3",
                 topic="OAuth2 password flow JWT dependency get_current_user")
```

Respuesta (recorte literal):

```json
{
  "library": "fastapi@0.110.3",
  "version": "0.110.3",
  "results": [],
  "message": "No documentation found. Try a shorter query using just the API or function name, for example 'cors' instead of 'CORS middleware configuration'."
}
```

Aporte: ninguno directo; el mensaje indicó acortar el término. Originó las
solicitudes 3 y 4. Queda registrada para no ocultar el fallo de validación.

## Solicitud 2

```text
context_get_docs(library="passlib@1.7.4",
                 topic="CryptContext bcrypt hash verify")
```

Respuesta (recorte de `quickstart > Introduction (part 3)`, fuente
`docs/narr/quickstart.rst`):

```text
4. The top choices left are :class:`~passlib.hash.bcrypt` and
   :class:`~passlib.hash.pbkdf2_sha256`.
   ... though currently the balance is in favor of bcrypt
   ...
Creating and Using a CryptContext
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256", "des_crypt"], deprecated="auto")
    >>> hash = pwd_context.hash("somepass")
    >>> pwd_context.verify("somepass", hash)
    True
```

Decisión que contribuyó: confirmó el patrón de una instancia global
`CryptContext` con `hash(...)` / `verify(...)` y el uso de bcrypt como esquema
activo recomendado, apoyando la Decisión 3 de `design.md` y las tareas 1.2 y 2.1
de `tasks.md` (declarar `passlib` + `bcrypt` y migrar el hash versionado de
C-02). **No** decidió el esquema legado: eso viene de
`backend/app/core/security.py:7-9` y de RN-AU-04, y sigue supeditado al gate.

## Solicitud 3 (reintento acortado)

```text
context_get_docs(library="fastapi@0.110.3",
                 topic="OAuth2PasswordRequestForm")
```

Respuesta (recorte de `simple-oauth2 > Code to get the username and password`,
fuente `docs/en/docs/tutorial/security/simple-oauth2.md`):

```text
### `OAuth2PasswordRequestForm`
First, import `OAuth2PasswordRequestForm`, and use it as a dependency with
`Depends` in the *path operation* for `/token` ...
`OAuth2PasswordRequestForm` is a class dependency that declares a form body with:
* The `username`.
* The `password`.
* An optional `scope` field ...
* An optional `grant_type`.
```

También aparece `index > OAuth2 Password Form` (fuente
`docs/en/docs/reference/security/index.md`) con:
`::: fastapi.security.OAuth2PasswordRequestForm` y
`OAuth2PasswordRequestFormStrict`.

Decisión que contribuyó: confirmó `OAuth2PasswordRequestForm` como dependencia
de formulario para `POST /auth/login` en la Decisión 1 de `design.md` y en la
tarea 2.3 de `tasks.md` (`username`/`password` urlencoded, 200 esperado). La
elección del path `/auth/login` y del JWT Bearer viene de la KB, no de la doc.

## Solicitud 4 (reintento acortado)

```text
context_get_docs(library="fastapi@0.110.3",
                 topic="get_current_user")
```

Respuesta (recorte de `get-current-user > Create a get_current_user dependency /
Get the user`, fuente `docs/en/docs/tutorial/security/get-current-user.md`):

```text
Let's create a dependency `get_current_user`.
Remember that dependencies can have sub-dependencies?
`get_current_user` will have a dependency with the same `oauth2_scheme` we
created before ... our new dependency `get_current_user` will receive a `token`
as a `str` from the sub-dependency `oauth2_scheme` ...
get_current_user will use a (fake) utility function we created, that takes a
token as a `str` and returns our Pydantic `User` model.
```

Decisión que contribuyó: confirmó el patrón de dependencias anidadas
`OAuth2PasswordBearer` → `get_current_user` → modelo de usuario, usado en las
Decisiones 1/2 de `design.md` y en la tarea 3.2 de `tasks.md`. El comportamiento
exigido (401 sin token, 401 con `exp` vencido, recarga del usuario activo) es
regla del proyecto, no de FastAPI.

## Síntesis

| Solicitud | Resultado | Decisión apoyada |
|-----------|-----------|------------------|
| fastapi: "OAuth2 password flow JWT dependency get_current_user" | Sin resultados | Ninguna; motivó reintentos |
| passlib: "CryptContext bcrypt hash verify" | 1 resultado útil | `CryptContext.hash/verify`, bcrypt activo (Decisión 3; tareas 1.2/2.1) |
| fastapi: "OAuth2PasswordRequestForm" | 4 resultados | Formulario de login (Decisión 1; tarea 2.3) |
| fastapi: "get_current_user" | 3 resultados | Dependencia con sub-dependencia Bearer (Decisiones 1/2; tarea 3.2) |

Estado: evidencia de apoyo técnico; no habilita implementación de C-03
(`governance CRITICO`, gate pendiente).
