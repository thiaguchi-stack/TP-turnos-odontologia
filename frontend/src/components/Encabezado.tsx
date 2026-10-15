interface EncabezadoProps {
  titulo: string;
}

export default function Encabezado({ titulo }: EncabezadoProps) {
  return (
    <header>
      <h1>{titulo}</h1>
    </header>
  );
}
