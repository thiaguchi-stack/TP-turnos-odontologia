import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import SinAcceso from "./components/SinAcceso";
import Agenda from "./pages/Agenda";
import DashboardAdmin from "./pages/DashboardAdmin";
import Home from "./pages/Home";
import Login from "./pages/Login";
import SesionProvider from "./store/SesionContext";

function conLayout(contenido: ReactNode) {
  return <Layout>{contenido}</Layout>;
}

export function Rutas() {
  return (
    <SesionProvider>
      <Routes>
        <Route path="/" element={conLayout(<Home />)} />
        <Route path="/login" element={conLayout(<Login />)} />
        <Route path="/sin-acceso" element={conLayout(<SinAcceso />)} />
        <Route
          path="/agenda"
          element={
            <ProtectedRoute roles={["admin", "odontologo"]}>
              {conLayout(<Agenda />)}
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute roles={["admin"]}>
              {conLayout(<DashboardAdmin />)}
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </SesionProvider>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Rutas />
    </BrowserRouter>
  );
}
