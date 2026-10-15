const ZONA_HORARIA = "America/Argentina/Buenos_Aires";

export function formatearFecha(fecha: Date): string {
  return new Intl.DateTimeFormat("es-AR", {
    dateStyle: "short",
    timeZone: ZONA_HORARIA,
  }).format(fecha);
}

export function formatearHora(fecha: Date): string {
  return new Intl.DateTimeFormat("es-AR", {
    timeStyle: "short",
    timeZone: ZONA_HORARIA,
  }).format(fecha);
}

export function formatearFechaHora(fecha: Date): string {
  return `${formatearFecha(fecha)} ${formatearHora(fecha)}`;
}
