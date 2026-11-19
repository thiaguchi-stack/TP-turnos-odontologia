import type { ReactNode } from "react";

import Encabezado from "./Encabezado";
import Navegacion from "./Navegacion";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div>
      <Encabezado titulo="Consultorio odontológico" />
      <Navegacion />
      <main>{children}</main>
    </div>
  );
}
