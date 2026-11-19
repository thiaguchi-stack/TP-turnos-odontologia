export type Rol = "admin" | "odontologo";

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UsuarioSesion {
  id: number;
  email: string;
  rol: Rol;
  profesional_id: number | null;
}

export const CLAVE_TOKEN_SESION = "turnos.access_token";
