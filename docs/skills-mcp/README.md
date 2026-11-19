# MCP local de documentación versionada (`context`)

Fecha: 2026-11-18. Este documento reproduce la configuración del servidor MCP
`@neuledge/context@1` usado para el TP. La configuración real vive **fuera del
repo**, en `~/.config/opencode/opencode.json`; acá solo se documenta para que
otra persona pueda repetirla. Es **tooling de desarrollo**, no una integración
externa del producto: la regla dura "Ninguna integración externa en v1" sigue
vigente. La KB del proyecto (`knowledge-base/`) es la fuente de verdad; el MCP
solo confirma firmas y hashing de versiones concretas.

## Requisitos

- Node.js con `npx` disponible (los comandos usan `npx -y @neuledge/context@1`,
  que fija la versión del paquete sin depender de una instalación global).
- OpenCode 1.19.3, que usa el **formato V1** de configuración (`mcp.<nombre>`
  con `enabled`).
- Sin API key ni OAuth: el servidor es local y corre por stdio.
- No requiere variables de entorno.

## Instalación de paquetes de documentación

FastAPI se instala desde el registro; passlib no está en el registro y se agrega
desde el repo fork, con `--tag` obligatorio porque el shell no es interactivo:

```sh
npx -y @neuledge/context@1 install pip/fastapi 0.110.3
npx -y @neuledge/context@1 add https://github.com/notypecheck/passlib --tag 1.7.4 --path docs --name passlib --pkg-version 1.7.4
```

La versión debe ser exacta (`0.110.3`, no `0.110`). Resultado verificado:
`fastapi@0.110.3` (824 secciones) y `passlib@1.7.4` (152 secciones).

## Configuración del cliente (ejemplo sin secretos)

Fragmento de `~/.config/opencode/opencode.json` (archivo global, **no** del
repo). No incluye credenciales ni datos de pacientes:

```json
{
  "mcp": {
    "context": {
      "type": "local",
      "command": ["npx", "-y", "@neuledge/context@1", "serve"],
      "enabled": true
    }
  }
}
```

`serve` se invoca con `npx -y @neuledge/context@1` en lugar del `context serve`
del README oficial para fijar la versión del paquete.

## Comprobación de conexión y ejecución de una herramienta

Comandos ejecutados el 2026-11-18 en este repo:

```sh
npx -y @neuledge/context@1 list
npx -y @neuledge/context@1 query fastapi "OAuth2PasswordRequestForm"
npx -y @neuledge/context@1 query passlib "CryptContext"
```

Salida cruda recortada a lo relevante (sin secretos ni hashes de ejemplo):
[`docs/evidencias/mcp-context-query.txt`](../evidencias/mcp-context-query.txt).

Resumen: `list` devolvió los dos paquetes instalados; la consulta de FastAPI
devolvió `fastapi@0.110.3` con el tutorial de `OAuth2PasswordRequestForm` y la
referencia `fastapi.security` (`source: docs/en/docs/tutorial/security/simple-oauth2.md`);
la consulta de passlib devolvió `passlib@1.7.4` con la API de `CryptContext`
(`source: docs/lib/passlib.context.rst`). Sirve para confirmar firmas y métodos
de hashing, no para definir reglas de negocio.

## Límites de acceso y datos de prueba

- Solo lectura de documentación: no se usa para modificar código ni specs.
- Sin credenciales, tokens ni secretos en comandos, config ni evidencias.
- Sin datos reales de pacientes: la documentación consultada es pública y los
  ejemplos del repo siguen siendo ficticios (RN-DATOS-03).
- Ante cualquier conflicto, **la KB prevalece** sobre la documentación del MCP,
  igual que `AGENTS.md` sobre herramientas externas.

## Problemas resueltos

1. **Versión inexistente**: `install pip/fastapi 0.110` devolvió 404; el registro
   exige la versión exacta, por eso se usa `0.110.3`.
2. **passlib ausente del registro**: se agregó desde
   `https://github.com/notypecheck/passlib` con `add`, `--tag 1.7.4` (obligatorio
   en shell no interactivo), `--path docs`, `--name passlib` y
   `--pkg-version 1.7.4`.
3. **Formato de config V1 vs V2**: la documentación actual de OpenCode muestra
   `mcp.servers` / `disabled` (V2), pero la versión instalada es 1.19.3 y usa V1:
   `mcp.<nombre>` con `enabled: true`.
