import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Rutas } from "../App";
import { apiFetch } from "../services/api";
import SesionProvider from "../store/SesionContext";
import { useSesion } from "../store/useSesion";
import { CLAVE_TOKEN_SESION } from "../types/auth";

const CLAVE_FICTICIA = "clave-ficticia-de-prueba";

function respuesta(status: number, cuerpo: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn(async () => cuerpo),
  } as unknown as Response;
}

function respuestaToken() {
  return respuesta(200, {
    access_token: "token-devuelto-por-el-backend",
    token_type: "Bearer",
  });
}

function respuestaIdentidad(rol: "admin" | "odontologo") {
  return respuesta(200, {
    id: rol === "admin" ? 1 : 9,
    email: `${rol}@clinica.local`,
    rol,
    profesional_id: rol === "admin" ? null : 7,
  });
}

function renderizar() {
  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <Rutas />
    </MemoryRouter>,
  );
}

async function completarYEnviar(usuario: ReturnType<typeof userEvent.setup>) {
  await usuario.type(
    screen.getByLabelText("Correo electrónico"),
    "admin@clinica.local",
  );
  await usuario.type(screen.getByLabelText("Contraseña"), CLAVE_FICTICIA);
  await usuario.click(screen.getByRole("button", { name: "Ingresar" }));
}

function Sonda() {
  const { usuario } = useSesion();
  const ubicacion = useLocation();
  return (
    <div>
      <span data-testid="usuario-sonda">{usuario?.email ?? "sin-usuario"}</span>
      <span data-testid="ruta-sonda">{ubicacion.pathname}</span>
      <button
        type="button"
        onClick={() => {
          void apiFetch("/profesionales").catch(() => {});
        }}
      >
        consultar profesionales
      </button>
    </div>
  );
}

function renderizarSonda(ruta: string) {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <SesionProvider>
        <Sonda />
      </SesionProvider>
    </MemoryRouter>,
  );
}

describe("página de ingreso", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    sessionStorage.clear();
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("envía el formulario como urlencoded con username y password", async () => {
    fetchMock
      .mockResolvedValueOnce(respuestaToken())
      .mockResolvedValueOnce(respuestaIdentidad("admin"));
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    await screen.findByRole("heading", { name: "Administración" });
    const [url, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/auth/login");
    expect(opciones.method).toBe("POST");
    const cuerpo = opciones.body as URLSearchParams;
    expect(cuerpo).toBeInstanceOf(URLSearchParams);
    expect(cuerpo.get("username")).toBe("admin@clinica.local");
    expect(cuerpo.get("password")).toBe(CLAVE_FICTICIA);
    expect((opciones.headers as Headers).has("Content-Type")).toBe(false);
  });

  it("muestra el estado de carga mientras espera la respuesta", async () => {
    let resolver: (valor: Response) => void = () => {};
    fetchMock.mockImplementationOnce(
      () =>
        new Promise<Response>((resolve) => {
          resolver = resolve;
        }),
    );
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    expect(await screen.findByRole("status")).toHaveTextContent("Ingresando…");
    expect(screen.getByRole("button", { name: "Ingresar" })).toBeDisabled();
    resolver(respuestaToken());
    fetchMock.mockResolvedValueOnce(respuestaIdentidad("odontologo"));
    await screen.findByRole("heading", { name: "Mi agenda" });
  });

  it("guarda el token y redirige al admin según su rol", async () => {
    fetchMock
      .mockResolvedValueOnce(respuestaToken())
      .mockResolvedValueOnce(respuestaIdentidad("admin"));
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    expect(
      await screen.findByRole("heading", { name: "Administración" }),
    ).toBeInTheDocument();
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBe(
      "token-devuelto-por-el-backend",
    );
    expect(localStorage.length).toBe(0);
  });

  it("redirige al odontólogo a su agenda", async () => {
    fetchMock
      .mockResolvedValueOnce(respuestaToken())
      .mockResolvedValueOnce(respuestaIdentidad("odontologo"));
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    expect(
      await screen.findByRole("heading", { name: "Mi agenda" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Administración" })).toBeNull();
  });

  it("muestra un error legible ante credenciales inválidas sin guardar token", async () => {
    fetchMock.mockResolvedValueOnce(
      respuesta(401, { detalle: "Credenciales inválidas" }),
    );
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /credenciales no son correctas/i,
    );
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(
      screen.getByRole("heading", { name: "Ingresar al consultorio" }),
    ).toBeInTheDocument();
  });

  it("muestra el mensaje del backend ante demasiados intentos", async () => {
    fetchMock.mockResolvedValueOnce(
      respuesta(429, { detalle: "Demasiados intentos. Probá más tarde." }),
    );
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Demasiados intentos. Probá más tarde.",
    );
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
  });

  it("no deja la contraseña en el DOM ni en los logs", async () => {
    const consola = vi.spyOn(console, "log").mockImplementation(() => {});
    const errorConsola = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});
    fetchMock.mockResolvedValueOnce(
      respuesta(401, { detalle: `Credenciales inválidas: ${CLAVE_FICTICIA}` }),
    );
    const usuario = userEvent.setup();

    renderizar();
    await completarYEnviar(usuario);

    await screen.findByRole("alert");
    expect(document.body.textContent).not.toContain(CLAVE_FICTICIA);
    for (const llamada of [...consola.mock.calls, ...errorConsola.mock.calls]) {
      expect(JSON.stringify(llamada)).not.toContain(CLAVE_FICTICIA);
    }
  });

  it("restaura la sesión al recargar con un token vigente", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vigente");
    fetchMock.mockResolvedValue(respuestaIdentidad("odontologo"));

    render(
      <MemoryRouter initialEntries={["/agenda"]}>
        <Rutas />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", { name: "Mi agenda" }),
    ).toBeInTheDocument();
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBe("token-vigente");
    expect(fetchMock.mock.calls[0][0]).toBe("/auth/me");
  });

  it("un token vencido al hidratar lleva al ingreso sin datos", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vencido");
    fetchMock.mockResolvedValue(
      respuesta(401, { detalle: "El usuario no existe o está inactivo." }),
    );

    render(
      <MemoryRouter initialEntries={["/agenda"]}>
        <Rutas />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", { name: "Ingresar al consultorio" }),
    ).toBeInTheDocument();
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(screen.queryByRole("heading", { name: "Mi agenda" })).toBeNull();
  });

  it("un 401 en una petición posterior cierra la sesión y redirige", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vigente");
    fetchMock
      .mockResolvedValueOnce(respuestaIdentidad("admin"))
      .mockResolvedValueOnce(respuesta(401, { detalle: "Token vencido" }));
    const usuario = userEvent.setup();

    renderizarSonda("/");
    await screen.findByText("admin@clinica.local");
    await usuario.click(
      screen.getByRole("button", { name: "consultar profesionales" }),
    );

    await waitFor(() => {
      expect(screen.getByTestId("ruta-sonda")).toHaveTextContent("/login");
    });
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(screen.getByTestId("usuario-sonda")).toHaveTextContent(
      "sin-usuario",
    );
  });

  it("un 401 público no cierra una sesión vigente", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vigente");
    fetchMock
      .mockResolvedValueOnce(respuestaIdentidad("admin"))
      .mockResolvedValueOnce(respuesta(401, { detalle: "Credenciales inválidas" }));
    const usuario = userEvent.setup();

    renderizar();
    await screen.findByRole("link", { name: "Administración" });
    await completarYEnviar(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /credenciales no son correctas/i,
    );
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBe("token-vigente");
    expect(
      screen.getByRole("link", { name: "Administración" }),
    ).toBeInTheDocument();
  });

  it("usa la base /api del entorno al armar la URL", async () => {
    vi.stubEnv("VITE_API_URL", "/api");
    vi.resetModules();
    const { apiFetch } = await import("../services/api");
    fetchMock.mockResolvedValue(respuesta(200, { ok: true }));

    await apiFetch("/auth/login");

    expect(fetchMock.mock.calls[0][0]).toBe("/api/auth/login");
    vi.unstubAllEnvs();
  });
});
