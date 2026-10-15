import Encabezado from "../components/Encabezado";
import { formatearFecha } from "../shared/utils";

export default function Home() {
  return (
    <main>
      <Encabezado titulo="Turnos del consultorio" />
      <p>Reservá tu turno online. Hoy es {formatearFecha(new Date())}.</p>
    </main>
  );
}
