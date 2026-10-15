export default function CustomerIdentity({ client, subtitle }) {
  if (!client) return <div className="customer-cell"><span>Cliente no asignado</span></div>;
  const name = client.razon_social || client.name || "Sin nombre";
  const initials = client.initials || name.substring(0, 2).toUpperCase();
  const color = client.color || "sage";
  const sub = subtitle ?? (client.rfc ? `${client.rfc} · ${client.correo || client.email || ""}` : (client.email || ""));

  return (
    <div className="customer-cell">
      <span className={"customer-avatar " + color}>
        {initials}
      </span>
      <div>
        <strong>{name}</strong>
        <small>{sub}</small>
      </div>
    </div>
  );
}
