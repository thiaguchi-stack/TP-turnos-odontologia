import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import Agenda from "../../pages/Agenda";
import { formatearFecha, formatearFechaHora, formatearHora } from "./date";

const INSTANTE_CRUCERO_DIA = new Date("2026-11-19T01:00:00.000Z");
const INSTANTE_CRUCERO_ANIO = new Date("2026-01-01T02:00:00.000Z");

function fechaEnZonaDelNavegador(fecha: Date): string {
  return new Intl.DateTimeFormat("es-AR", {
    dateStyle: "short",
    timeZone: "UTC",
  }).format(fecha);
}

afterEach(() => {
  vi.useRealTimers();
});

describe("utilidad compartida de fechas", () => {
  it("el placeholder muestra la fecha en es-AR y zona del consultorio", () => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(INSTANTE_CRUCERO_DIA);

    render(createElement(Agenda));

    expect(screen.getByText(/Hoy es 18\/11\/26/)).toBeInTheDocument();
  });

  it("formatea fecha, hora y fecha y hora con la zona fija", () => {
    expect(formatearFecha(INSTANTE_CRUCERO_DIA)).toBe("18/11/26");
    expect(formatearHora(INSTANTE_CRUCERO_DIA)).toBe("10:00 p. m.");
    expect(formatearFechaHora(INSTANTE_CRUCERO_DIA)).toBe(
      "18/11/26 10:00 p. m.",
    );
  });

  it("cruza de año y de mes según la zona del consultorio", () => {
    expect(formatearFecha(INSTANTE_CRUCERO_ANIO)).toBe("31/12/25");
    expect(formatearFecha(INSTANTE_CRUCERO_ANIO)).not.toBe(
      fechaEnZonaDelNavegador(INSTANTE_CRUCERO_ANIO),
    );
  });

  it("no equivale a formatear con la zona del navegador", () => {
    expect(formatearFecha(INSTANTE_CRUCERO_DIA)).not.toBe(
      fechaEnZonaDelNavegador(INSTANTE_CRUCERO_DIA),
    );
  });
});
