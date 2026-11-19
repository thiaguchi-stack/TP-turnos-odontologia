import { useCallback, useEffect, useReducer, useRef, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";

import {
  ApiError,
  apiFetch,
  establecerManejadorSesionExpirada,
} from "../services/api";
import { CLAVE_TOKEN_SESION, type UsuarioSesion } from "../types/auth";
import { SesionContext, type SesionContexto } from "./useSesion";

interface EstadoSesion {
  token: string | null;
  usuario: UsuarioSesion | null;
  cargando: boolean;
}

type AccionSesion =
  | { tipo: "iniciando"; token?: string }
  | { tipo: "hidratada"; usuario: UsuarioSesion }
  | { tipo: "sin-sesion" };

function estadoInicial(): EstadoSesion {
  const token = tokenGuardado();
  return { token, usuario: null, cargando: token !== null };
}

function reducer(
  estado: EstadoSesion,
  accion: AccionSesion,
): EstadoSesion {
  switch (accion.tipo) {
    case "iniciando":
      return {
        token: accion.token ?? estado.token,
        usuario: estado.usuario,
        cargando: true,
      };
    case "hidratada":
      return { token: estado.token, usuario: accion.usuario, cargando: false };
    case "sin-sesion":
      return { token: null, usuario: null, cargando: false };
  }
}

function tokenGuardado(): string | null {
  try {
    return sessionStorage.getItem(CLAVE_TOKEN_SESION);
  } catch {
    return null;
  }
}

function borrarToken(): void {
  try {
    sessionStorage.removeItem(CLAVE_TOKEN_SESION);
  } catch {
    return;
  }
}

export default function SesionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [estado, dispatch] = useReducer(reducer, undefined, estadoInicial);
  const hidratacionEnCurso = useRef<Promise<UsuarioSesion | null> | null>(null);

  const cerrarSesion = useCallback(() => {
    borrarToken();
    dispatch({ tipo: "sin-sesion" });
  }, []);

  const hidratar = useCallback((): Promise<UsuarioSesion | null> => {
    if (hidratacionEnCurso.current) {
      return hidratacionEnCurso.current;
    }
    const token = tokenGuardado();
    if (!token) {
      dispatch({ tipo: "sin-sesion" });
      return Promise.resolve(null);
    }
    dispatch({ tipo: "iniciando" });
    const promesa = (async () => {
      try {
        const usuario = await apiFetch<UsuarioSesion>("/auth/me");
        if (tokenGuardado() !== token) {
          return null;
        }
        dispatch({ tipo: "hidratada", usuario });
        return usuario;
      } catch (error) {
        if (tokenGuardado() === token) {
          dispatch({ tipo: "sin-sesion" });
        }
        if (error instanceof ApiError && error.status === 401) {
          return null;
        }
        throw error;
      } finally {
        hidratacionEnCurso.current = null;
      }
    })();
    hidratacionEnCurso.current = promesa;
    return promesa;
  }, []);

  const iniciarSesion = useCallback(
    async (token: string): Promise<UsuarioSesion> => {
      sessionStorage.setItem(CLAVE_TOKEN_SESION, token);
      dispatch({ tipo: "iniciando", token });
      const usuario = await hidratar();
      if (!usuario) {
        throw new Error("No se pudo iniciar la sesión. Intentá de nuevo.");
      }
      return usuario;
    },
    [hidratar],
  );

  useEffect(() => {
    if (tokenGuardado()) {
      void hidratar();
    }
  }, [hidratar]);

  useEffect(() => {
    establecerManejadorSesionExpirada(() => {
      cerrarSesion();
      navigate("/login");
    });
    return () => establecerManejadorSesionExpirada(null);
  }, [cerrarSesion, navigate]);

  const valor: SesionContexto = {
    usuario: estado.usuario,
    rol: estado.usuario?.rol ?? null,
    profesional_id: estado.usuario?.profesional_id ?? null,
    cargando: estado.cargando,
    iniciarSesion,
    cerrarSesion,
    hidratar,
  };

  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>;
}
