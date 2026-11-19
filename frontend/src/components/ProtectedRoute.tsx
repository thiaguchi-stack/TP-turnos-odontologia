import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useSesion } from "../store/useSesion";
import type { Rol } from "../types/auth";

interface ProtectedRouteProps {
  roles: Rol[];
  children: ReactNode;
}

export default function ProtectedRoute({
  roles,
  children,
}: ProtectedRouteProps) {
  const { usuario, rol, cargando } = useSesion();
  const ubicacion = useLocation();

  if (cargando) {
    return <p>Cargando la sesión…</p>;
  }
  if (!usuario || !rol) {
    return (
      <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
    );
  }
  if (!roles.includes(rol)) {
    return <Navigate to="/sin-acceso" replace />;
  }
  return <>{children}</>;
}
