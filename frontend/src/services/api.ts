import { CLAVE_TOKEN_SESION } from "../types/auth";

const API_URL: string = import.meta.env.VITE_API_URL ?? "";

export interface OpcionesApi {
  metodo?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  cuerpo?: unknown;
  formulario?: URLSearchParams;
  publica?: boolean;
  cabeceras?: Record<string, string>;
}

export type ManejadorSesionExpirada = () => void;

let manejadorSesionExpirada: ManejadorSesionExpirada | null = null;

export class ApiError extends Error {
  readonly status: number;
  readonly mensaje: string;

  constructor(status: number, mensaje: string) {
    super(mensaje);
    this.name = "ApiError";
    this.status = status;
    this.mensaje = mensaje;
  }
}

export function establecerManejadorSesionExpirada(
  manejador: ManejadorSesionExpirada | null,
): void {
  manejadorSesionExpirada = manejador;
}

export function mensajeDeError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.mensaje;
  }
  return "Ocurrió un problema. Intentá de nuevo.";
}

export function mensajeDeIngreso(error: unknown): string {
  if (error instanceof ApiError && error.status === 401) {
    return "Las credenciales no son correctas. Revisá tu correo y contraseña e intentá de nuevo.";
  }
  return mensajeDeError(error);
}

function tokenGuardado(): string | null {
  try {
    return sessionStorage.getItem(CLAVE_TOKEN_SESION);
  } catch {
    return null;
  }
}

function cabecerasPeticion(opciones: OpcionesApi, token: string | null): Headers {
  const cabeceras = new Headers(opciones.cabeceras ?? {});
  if (opciones.cuerpo !== undefined && !opciones.formulario) {
    cabeceras.set("Content-Type", "application/json");
  }
  if (!opciones.publica && token) {
    cabeceras.set("Authorization", `Bearer ${token}`);
  }
  return cabeceras;
}

function cuerpoPeticion(opciones: OpcionesApi): BodyInit | undefined {
  if (opciones.formulario) {
    return opciones.formulario;
  }
  if (opciones.cuerpo !== undefined) {
    return JSON.stringify(opciones.cuerpo);
  }
  return undefined;
}

function normalizarMensaje(datos: unknown, status: number): string {
  if (typeof datos === "object" && datos !== null) {
    const registro = datos as Record<string, unknown>;
    const valor = registro.detalle ?? registro.detail;
    if (typeof valor === "string") {
      return valor;
    }
    if (valor !== undefined) {
      return JSON.stringify(valor);
    }
  }
  if (typeof datos === "string") {
    return datos;
  }
  return `Error ${status}`;
}

async function mensajeDelError(respuesta: Response): Promise<string> {
  try {
    return normalizarMensaje(await respuesta.json(), respuesta.status);
  } catch {
    return `Error ${respuesta.status}`;
  }
}

function secretoDe(opciones: OpcionesApi): string | null {
  const delFormulario = opciones.formulario?.get("password");
  if (delFormulario) {
    return delFormulario;
  }
  if (typeof opciones.cuerpo === "object" && opciones.cuerpo !== null) {
    const valor = (opciones.cuerpo as Record<string, unknown>).password;
    if (typeof valor === "string") {
      return valor;
    }
  }
  return null;
}

function ocultarSecreto(mensaje: string, opciones: OpcionesApi): string {
  const secreto = secretoDe(opciones);
  if (!secreto || !mensaje.includes(secreto)) {
    return mensaje;
  }
  return mensaje.split(secreto).join("[oculto]");
}

function notificarSesionExpirada(): void {
  sessionStorage.removeItem(CLAVE_TOKEN_SESION);
  manejadorSesionExpirada?.();
  window.dispatchEvent(new Event("sesion-expirada"));
}

export async function apiFetch<T>(
  ruta: string,
  opciones: OpcionesApi = {},
): Promise<T> {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    method: opciones.metodo ?? "GET",
    headers: cabecerasPeticion(opciones, tokenGuardado()),
    body: cuerpoPeticion(opciones),
  });

  if (!respuesta.ok) {
    const mensaje = ocultarSecreto(
      await mensajeDelError(respuesta),
      opciones,
    );
    if (respuesta.status === 401 && !opciones.publica) {
      notificarSesionExpirada();
    }
    throw new ApiError(respuesta.status, mensaje);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  try {
    return (await respuesta.json()) as T;
  } catch {
    return undefined as T;
  }
}
