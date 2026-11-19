import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  apiFetch,
  establecerManejadorSesionExpirada,
  mensajeDeError,
} from "./api";
import { CLAVE_TOKEN_SESION } from "../types/auth";

function respuesta(status: number, cuerpo: unknown = undefined): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: "respuesta de prueba",
    json: vi.fn(async () => cuerpo),
  } as unknown as Response;
}

describe("wrapper HTTP con JWT", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    sessionStorage.clear();
    establecerManejadorSesionExpirada(null);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    establecerManejadorSesionExpirada(null);
  });

  it("adjunta el Bearer en una petición privada", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-de-prueba");
    fetchMock.mockResolvedValue(respuesta(200, { ok: true }));

    const resultado = await apiFetch<{ ok: boolean }>("/profesionales");

    expect(resultado).toEqual({ ok: true });
    const [, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((opciones.headers as Headers).get("Authorization")).toBe(
      "Bearer token-de-prueba",
    );
  });

  it("no adjunta el Bearer en una petición pública", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-de-prueba");
    fetchMock.mockResolvedValue(respuesta(200, { ok: true }));

    await apiFetch("/auth/login", {
      metodo: "POST",
      formulario: new URLSearchParams({ username: "a", password: "b" }),
      publica: true,
    });

    const [, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((opciones.headers as Headers).has("Authorization")).toBe(false);
    expect((opciones.headers as Headers).has("Content-Type")).toBe(false);
    expect(opciones.body).toBeInstanceOf(URLSearchParams);
    expect((opciones.body as URLSearchParams).get("username")).toBe("a");
  });

  it("expone status y mensaje de un 401 con detalle", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vencido");
    fetchMock.mockResolvedValue(
      respuesta(401, { detalle: "Credenciales inválidas" }),
    );

    await expect(apiFetch("/auth/me")).rejects.toMatchObject({
      status: 401,
      mensaje: "Credenciales inválidas",
    });
  });

  it("expone status y mensaje de un 401 con detail", async () => {
    fetchMock.mockResolvedValue(
      respuesta(401, { detail: "No autorizado" }),
    );

    let error: unknown;
    try {
      await apiFetch("/auth/me");
    } catch (fallo) {
      error = fallo;
    }

    expect(error).toBeInstanceOf(ApiError);
    const apiError = error as ApiError;
    expect(apiError.status).toBe(401);
    expect(apiError.mensaje).toBe("No autorizado");
    expect(mensajeDeError(apiError)).toBe("No autorizado");
  });

  it.each([
    [403, "Acceso denegado"],
    [429, "Demasiados intentos"],
    [400, "Datos inválidos"],
  ])("expone el status %i tipado con su mensaje", async (status, mensaje) => {
    fetchMock.mockResolvedValue(respuesta(status, { detalle: mensaje }));

    await expect(apiFetch("/profesionales")).rejects.toMatchObject({
      status,
      mensaje,
    });
  });

  it("cierra la sesión y avisa ante un 401", async () => {
    const cerrar = vi.fn();
    establecerManejadorSesionExpirada(cerrar);
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vencido");
    fetchMock.mockResolvedValue(respuesta(401, { detalle: "Vencido" }));

    await expect(apiFetch("/profesionales")).rejects.toBeInstanceOf(ApiError);
    expect(cerrar).toHaveBeenCalledOnce();
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
  });

  it("no envía el header cuando el token está vacío", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "");
    fetchMock.mockResolvedValue(respuesta(200, { ok: true }));

    await apiFetch("/profesionales");

    const [, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((opciones.headers as Headers).has("Authorization")).toBe(false);
  });

  it("tolera un 401 sin cuerpo y avisa igual", async () => {
    const cerrar = vi.fn();
    establecerManejadorSesionExpirada(cerrar);
    fetchMock.mockResolvedValue(respuesta(401));

    const fallo = await apiFetch("/auth/me").catch((error: unknown) => error);

    expect(fallo).toBeInstanceOf(ApiError);
    expect((fallo as ApiError).status).toBe(401);
    expect((fallo as ApiError).mensaje).not.toBe("");
    expect(cerrar).toHaveBeenCalledOnce();
  });

  it("nunca deja la contraseña en el error ni en la consola", async () => {
    const consola = vi.spyOn(console, "log").mockImplementation(() => {});
    const errorConsola = vi.spyOn(console, "error").mockImplementation(() => {});
    const secreto = "clave-secreta-123";
    fetchMock.mockResolvedValue(
      respuesta(401, { detalle: `Credenciales inválidas: ${secreto}` }),
    );

    const fallo = await apiFetch("/auth/login", {
      metodo: "POST",
      formulario: new URLSearchParams({ username: "admin@clinica.local", password: secreto }),
      publica: true,
    }).catch((error: unknown) => error);

    expect(mensajeDeError(fallo)).not.toContain(secreto);
    expect(mensajeDeError(fallo)).toContain("[oculto]");
    for (const llamada of [...consola.mock.calls, ...errorConsola.mock.calls]) {
      expect(JSON.stringify(llamada)).not.toContain(secreto);
    }
    consola.mockRestore();
    errorConsola.mockRestore();
  });

  it("no parsea dos veces un 200 con cuerpo vacío", async () => {
    const json = vi.fn(async () => undefined);
    fetchMock.mockResolvedValue({ ok: true, status: 200, json } as unknown as Response);

    const resultado = await apiFetch("/profesionales");

    expect(resultado).toBeUndefined();
    expect(json).toHaveBeenCalledOnce();
  });
});
