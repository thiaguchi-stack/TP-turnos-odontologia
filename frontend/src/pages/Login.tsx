import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch, mensajeDeIngreso } from "../services/api";
import { useSesion } from "../store/useSesion";
import type { Token } from "../types/auth";

export default function Login() {
  const { iniciarSesion } = useSesion();
  const navegar = useNavigate();
  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function manejarEnvio(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setError(null);
    if (!correo.trim() || !clave) {
      setError("Ingresá tu correo y tu contraseña para continuar.");
      return;
    }
    setEnviando(true);
    try {
      const formulario = new URLSearchParams({
        username: correo,
        password: clave,
      });
      const tokens = await apiFetch<Token>("/auth/login", {
        metodo: "POST",
        formulario,
        publica: true,
      });
      const usuario = await iniciarSesion(tokens.access_token);
      navegar(usuario.rol === "admin" ? "/admin" : "/agenda", {
        replace: true,
      });
    } catch (fallo) {
      setError(mensajeDeIngreso(fallo));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      <h1>Ingresar al consultorio</h1>
      <form onSubmit={(evento) => void manejarEnvio(evento)}>
        <div>
          <label htmlFor="correo">Correo electrónico</label>
          <input
            id="correo"
            type="email"
            autoComplete="username"
            value={correo}
            onChange={(evento) => setCorreo(evento.target.value)}
          />
        </div>
        <div>
          <label htmlFor="clave">Contraseña</label>
          <input
            id="clave"
            type="password"
            autoComplete="current-password"
            value={clave}
            onChange={(evento) => setClave(evento.target.value)}
          />
        </div>
        <button type="submit" disabled={enviando}>
          Ingresar
        </button>
      </form>
      {enviando && <p role="status">Ingresando…</p>}
      {error && <p role="alert">{error}</p>}
    </>
  );
}
