import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Rutas } from "../App";
import { CLAVE_TOKEN_SESION } from "../types/auth";

function respuesta(rol: "admin" | "odontologo", profesional_id: number | null) {
  return {
    ok: true,
    status: 200,
    json: vi.fn(async () => ({
      id: rol === "admin" ? 1 : 9,
      email: `${rol}@clinica.local`,
      rol,
      profesional_id,
    })),
  } as unknown as Response;
}

function renderizar(ruta: string) {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <Rutas />
    </MemoryRouter>,
  );
}

describe("rutas protegidas y navegación por rol", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    sessionStorage.clear();
    localStorage.clear();
  });

  it("redirige al visitante de /agenda al ingreso", async () => {
    renderizar("/agenda");

    expect(
      await screen.findByRole("heading", { name: "Ingresar al consultorio" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Mi agenda" })).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("muestra Sin acceso cuando un odontólogo intenta /admin", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-odonto");
    fetchMock.mockResolvedValue(respuesta("odontologo", 7));

    renderizar("/admin");

    expect(
      await screen.findByRole("heading", { name: "Sin acceso" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Administración" })).toBeNull();
  });

  it("muestra los enlaces de administración al admin", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-admin");
    fetchMock.mockResolvedValue(respuesta("admin", null));

    renderizar("/");

    expect(
      await screen.findByRole("link", { name: "Administración" }),
    ).toBeInTheDocument();
    const usuario = userEvent.setup();
    await usuario.click(screen.getByRole("link", { name: "Administración" }));
    expect(
      await screen.findByRole("heading", { name: "Administración" }),
    ).toBeInTheDocument();
  });

  it("oculta la administración al odontólogo pero muestra su agenda", async () => {
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-odonto");
    fetchMock.mockResolvedValue(respuesta("odontologo", 7));

    renderizar("/");

    const agenda = await screen.findByRole("link", { name: "Mi agenda" });
    expect(agenda).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Administración" })).toBeNull();
    const usuario = userEvent.setup();
    await usuario.click(agenda);
    expect(
      await screen.findByRole("heading", { name: "Mi agenda" }),
    ).toBeInTheDocument();
  });

  it("una ruta protegida directa sin sesión no muestra datos del consultorio", async () => {
    renderizar("/admin");

    expect(
      await screen.findByRole("heading", { name: "Ingresar al consultorio" }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/profesionales|prestaciones|bloqueos/)).toBeNull();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("la home pública sin token no muestra datos clínicos ni de terceros", async () => {
    renderizar("/");

    expect(
      await screen.findByRole("heading", { name: "Turnos del consultorio" }),
    ).toBeInTheDocument();
    for (const dato of ["Sofía", "Ramírez", "33444555", "historia clínica"]) {
      expect(screen.queryByText(dato)).toBeNull();
    }
    expect(
      screen.getByRole("link", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();
  });

  it("/login es alcanzable sin sesión", async () => {
    renderizar("/login");

    expect(
      await screen.findByRole("heading", { name: "Ingresar al consultorio" }),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("no muestra el enlace de ingreso mientras hidrata una sesión persistida", async () => {
    let resolver: (valor: Response) => void = () => {};
    fetchMock.mockImplementation(
      () =>
        new Promise<Response>((resolve) => {
          resolver = resolve;
        }),
    );
    sessionStorage.setItem(CLAVE_TOKEN_SESION, "token-admin");

    renderizar("/");

    expect(screen.queryByRole("link", { name: "Iniciar sesión" })).toBeNull();
    expect(screen.getByText("Cargando sesión…")).toBeInTheDocument();
    resolver(respuesta("admin", null));
    expect(
      await screen.findByRole("link", { name: "Administración" }),
    ).toBeInTheDocument();
  });
});
