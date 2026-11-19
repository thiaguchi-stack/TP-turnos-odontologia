import { formatearFecha } from "../shared/utils";

export default function Home() {
  return (
    <>
      <h1>Turnos del consultorio</h1>
      <p>Reservá tu turno online. Hoy es {formatearFecha(new Date())}.</p>
    </>
  );
}
