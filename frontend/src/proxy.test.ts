// @vitest-environment node

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import config from "../vite.config";

function reglaApi() {
  const proxy = config.server?.proxy;
  if (!proxy || Array.isArray(proxy)) {
    throw new Error("No hay configuración de proxy en vite.config.ts");
  }
  const regla = proxy["/api"];
  if (!regla || typeof regla === "string") {
    throw new Error("No hay regla /api en vite.config.ts");
  }
  return regla;
}

describe("proxy de /api", () => {
  it("apunta al backend local y reescribe /api/auth/login", () => {
    const regla = reglaApi();
    expect(regla.target).toBe("http://localhost:8000");
    expect(regla.changeOrigin).toBe(true);
    if (!regla.rewrite) {
      throw new Error("Falta la función rewrite en la regla /api");
    }
    const reescribir = regla.rewrite as (ruta: string) => string;
    expect(reescribir("/api/auth/login")).toBe("/auth/login");
  });

  it("conserva rutas sin el prefijo /api", () => {
    const regla = reglaApi();
    if (!regla.rewrite) {
      throw new Error("Falta la función rewrite en la regla /api");
    }
    const reescribir = regla.rewrite as (ruta: string) => string;
    expect(reescribir("/auth/login")).toBe("/auth/login");
  });

  it("la URL base del cliente es /api", () => {
    const ejemplo = readFileSync(
      resolve(process.cwd(), ".env.example"),
      "utf8",
    );
    expect(ejemplo).toContain("VITE_API_URL=/api");
  });
});
