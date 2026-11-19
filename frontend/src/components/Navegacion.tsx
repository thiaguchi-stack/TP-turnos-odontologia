import { Link, useNavigate } from "react-router-dom";

import { useSesion } from "../store/useSesion";

export default function Navegacion() {
  const { rol, cargando, cerrarSesion } = useSesion();
  const navegar = useNavigate();

  return (
    <nav aria-label="Navegación principal">
      <ul>
        <li>
          <Link to="/">Inicio</Link>
        </li>
        {cargando ? (
          <li>Cargando sesión…</li>
        ) : rol ? (
          <>
            <li>
              <Link to="/agenda">Mi agenda</Link>
            </li>
            {rol === "admin" && (
              <li>
                <Link to="/admin">Administración</Link>
              </li>
            )}
            <li>
              <button
                type="button"
                onClick={() => {
                  cerrarSesion();
                  navegar("/");
                }}
              >
                Cerrar sesión
              </button>
            </li>
          </>
        ) : (
          <li>
            <Link to="/login">Iniciar sesión</Link>
          </li>
        )}
      </ul>
    </nav>
  );
}
