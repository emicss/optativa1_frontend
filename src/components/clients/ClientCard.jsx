import Icon from "../ui/Icon.jsx";
import { money } from "../../utils/format.js";
import { total } from "../../utils/invoices.js";

const COLORS = ["sage", "sand", "lilac", "sky"];

export default function ClientCard({ client, invoices = [], onOpen }) {
  const clientId = client.cliente_id || client.id;
  const name = client.razon_social || client.name;
  const initials = client.initials || (name ? name.substring(0, 2).toUpperCase() : "CL");
  const color = client.color || COLORS[(clientId || 0) % COLORS.length];
  const email = client.correo || client.email || "Sin correo";
  const rfc = client.rfc || "";
  const tipo = client.tipo_persona || client.sector || "RECEPTOR";

  const bills = invoices.filter(
    (item) => item.client === clientId || item.receptor_id === clientId || item.emisor_id === clientId
  );

  return (
    <article className="client-card">
      <div className="client-card-top">
        <span className={"customer-avatar large " + color}>
          {initials}
        </span>
        <span className="client-sector">{rfc ? `${rfc} · ${tipo}` : tipo}</span>
      </div>
      <h3>{name}</h3>
      <p>{client.contact || client.regimen_fiscal ? `Régimen: ${client.regimen_fiscal || client.contact}` : ""}</p>
      <span className="client-email">{email}</span>
      <div className="client-card-bottom">
        <div>
          <small>Facturado</small>
          <strong>
            {money(
              bills
                .filter((item) => item.status !== "Borrador" && item.estado !== "CANCELADA")
                .reduce((sum, item) => sum + (item.total || total(item) || 0), 0),
            )}
          </strong>
        </div>
        <button
          className="icon-button"
          aria-label={"Ver cliente " + name}
          onClick={() => onOpen(client)}
        >
          <Icon name="arrow" />
        </button>
      </div>
    </article>
  );
}
