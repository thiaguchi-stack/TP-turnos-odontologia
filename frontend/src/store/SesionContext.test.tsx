import { StrictMode } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SesionProvider from "./SesionContext";
import { useSesion } from "./useSesion";
import { CLAVE_TOKEN_SESION } from "../types/auth";

const identidad = {
  id: 9,
  email: "odontologo@clinica.local",
  rol: "odontologo",
  profesional_id: 7,
};

function respuesta(status: number, cuerpo: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn(async () => cuerpo),
  } as unknown as Response;
}

function Consumidor() {
  const sesion = useSesion();
  return (
    <div>
      <span data-testid="estado">
        {sesion.cargando ? "cargando" : "listo"}
      </span>
      <span data-testid="usuario">
        {sesion.usuario ? JSON.stringify(sesion.usuario) : "sin-usuario"}
      </span>
      <span data-testid="rol">{sesion.rol ?? "sin-rol"}</span>
      <button onClick={() => void sesion.iniciarSesion("token-ficticio")}>
        ingresar
      </button>
      <button onClick={() => sesion.cerrarSesion()}>salir</button>
    </div>
  );
}

function renderizar(stricto = false) {
  const contenido = (
    <MemoryRouter>
      <SesionProvider>
        <Consumidor />
      </SesionProvider>
    </MemoryRouter>
  );
  return render(stricto ? <StrictMode>{contenido}</StrictMode> : contenido);
}

describe("store de sesión", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    sessionStorage.clear();
    localStorage.clear();
  });

  it("guarda el token solo en sessionStorage al iniciar sesión", async () => {
    fetchMock.mockResolvedValue(respuesta(200, identidad));
    const usuario = userEvent.setup();

    renderizar();
    await usuario.click(screen.getByRole("button", { name: "ingresar" }));

    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBe("token-ficticio");
    expect(localStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(localStorage.length).toBe(0);
    await waitFor(() => {
      expect(screen.getByTestId("usuario")).toHaveTextContent(
        JSON.stringify(identidad),
      );
    });
  });

  it("toma la identidad de /auth/me y no del JWT", async () => {
    const jwtConClaimsDistintos = `${btoa(
      JSON.stringify({ sub: "1", rol: "admin", profesional_id: null }),
    )}.firma-ficticia`;
    sessionStorage.setItem(CLAVE_TOKEN_SESION, jwtConClaimsDistintos);
    fetchMock.mockResolvedValue(respuesta(200, identidad));

    renderizar();

    await waitFor(() => {
      expect(screen.getByTestId("rol")).toHaveTextContent("odontologo");
    });
    expect(screen.getByTestId("usuario")).toHaveTextContent('"id":9');
    expect(screen.getByTestId("usuario")).toHaveTextContent(
      '"profesional_id":7',
    );
    const [url, opciones] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/auth/me");
    expect((opciones.headers as Headers).get("Authorization")).toBe(
      `Bearer ${jwtConClaimsDistintos}`,
    );
  });

  it("limpia token e identidad al cerrar sesión", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-ficticio");
    fetchMock.mockResolvedValue(respuesta(200, identidad));
    const usuario = userEvent.setup();

    renderizar();
    await screen.findByTestId("rol");
    await waitFor(() =>
      expect(screen.getByTestId("rol")).toHaveTextContent("odontologo"),
    );
    await usuario.click(screen.getByRole("button", { name: "salir" }));

    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(screen.getByTestId("usuario")).toHaveTextContent("sin-usuario");
    expect(screen.getByTestId("rol")).toHaveTextContent("sin-rol");
  });

  it("trata un 401 al hidratar como sesión expirada", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-vencido");
    fetchMock.mockResolvedValue(
      respuesta(401, { detalle: "El token venció" }),
    );

    renderizar();

    await waitFor(() => {
      expect(screen.getByTestId("estado")).toHaveTextContent("listo");
    });
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
    expect(screen.getByTestId("usuario")).toHaveTextContent("sin-usuario");
    expect(screen.getByTestId("rol")).toHaveTextContent("sin-rol");
    expect(screen.queryByText(identidad.email)).not.toBeInTheDocument();
  });

  it("no duplica /auth/me bajo StrictMode", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-ficticio");
    fetchMock.mockResolvedValue(respuesta(200, identidad));

    renderizar(true);

    await waitFor(() =>
      expect(screen.getByTestId("rol")).toHaveTextContent("odontologo"),
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("conserva el profesional_id del odontólogo", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-ficticio");
    fetchMock.mockResolvedValue(respuesta(200, identidad));

    renderizar();

    await waitFor(() =>
      expect(screen.getByTestId("usuario")).toHaveTextContent(
        '"profesional_id":7',
      ),
    );
  });

  it("cerrar sesión sin token deja el estado vacío", async () => {
    const usuario = userEvent.setup();
    renderizar();

    await usuario.click(screen.getByRole("button", { name: "salir" }));

    expect(screen.getByTestId("estado")).toHaveTextContent("listo");
    expect(screen.getByTestId("usuario")).toHaveTextContent("sin-usuario");
    expect(screen.getByTestId("rol")).toHaveTextContent("sin-rol");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("una hidratación que termina después del cierre no restaura la identidad", async () => {
    let resolver: (valor: Response) => void = () => {};
    fetchMock.mockImplementation(
      () =>
        new Promise<Response>((resolve) => {
          resolver = resolve;
        }),
    );
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-ficticio");
    const usuario = userEvent.setup();

    renderizar();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledOnce());
    await usuario.click(screen.getByRole("button", { name: "salir" }));

    resolver(respuesta(200, identidad));

    await waitFor(() =>
      expect(screen.getByTestId("estado")).toHaveTextContent("listo"),
    );
    expect(screen.getByTestId("usuario")).toHaveTextContent("sin-usuario");
    expect(sessionStorage.getItem(CLAVE_TOKEN_SESION)).toBeNull();
  });
});
