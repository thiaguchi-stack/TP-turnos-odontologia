import { createContext, useContext } from "react";

import type { Rol, UsuarioSesion } from "../types/auth";

export interface SesionContexto {
  usuario: UsuarioSesion | null;
  rol: Rol | null;
  profesional_id: number | null;
  cargando: boolean;
  iniciarSesion: (token: string) => Promise<UsuarioSesion>;
  cerrarSesion: () => void;
  hidratar: () => Promise<UsuarioSesion | null>;
}

export const SesionContext = createContext<SesionContexto | null>(null);

export function useSesion(): SesionContexto {
  const contexto = useContext(SesionContext);
  if (!contexto) {
    throw new Error("useSesion debe usarse dentro de SesionProvider");
  }
  return contexto;
}
