import { formatearFecha } from "../shared/utils";

export default function Agenda() {
  return (
    <>
      <h1>Mi agenda</h1>
      <p>Acá vas a ver tus turnos. Hoy es {formatearFecha(new Date())}.</p>
    </>
  );
}
