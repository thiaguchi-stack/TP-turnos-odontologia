import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("toolchain de tests", () => {
  it("registra los matchers de jest-dom", () => {
    render(<p>Hola, mundo</p>);
    expect(screen.getByText("Hola, mundo")).toBeInTheDocument();
  });

  it("limpia el DOM y el almacenamiento entre tests", () => {
    expect(screen.queryByText("Hola, mundo")).not.toBeInTheDocument();
    expect(sessionStorage.length).toBe(0);
    expect(localStorage.length).toBe(0);
  });
});
