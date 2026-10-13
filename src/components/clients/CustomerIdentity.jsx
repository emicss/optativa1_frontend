export default function CustomerIdentity({ client, subtitle = client.email }) {
  return (
    <div className="customer-cell">
      <span className={"customer-avatar " + client.color}>
        {client.initials}
      </span>
      <div>
        <strong>{client.name}</strong>
        <small>{subtitle}</small>
      </div>
    </div>
  );
}
