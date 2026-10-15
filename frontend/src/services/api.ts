const API_URL: string = import.meta.env.VITE_API_URL ?? "";

export async function apiFetch<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    headers: {
      "Content-Type": "application/json",
      ...(opciones.headers ?? {}),
    },
    ...opciones,
  });

  if (!respuesta.ok) {
    throw new Error(`Error ${respuesta.status}: ${respuesta.statusText}`);
  }

  return (await respuesta.json()) as T;
}
