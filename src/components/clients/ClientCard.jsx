import Icon from "../ui/Icon.jsx";
import { money } from "../../utils/format.js";
import { total } from "../../utils/invoices.js";
export default function ClientCard({ client, invoices, onOpen }) {
  const bills = invoices.filter((item) => item.client === client.id);
  return (
    <article className="client-card">
      <div className="client-card-top">
        <span className={"customer-avatar large " + client.color}>
          {client.initials}
        </span>
        <span className="client-sector">{client.sector}</span>
      </div>
      <h3>{client.name}</h3>
      <p>{client.contact}</p>
      <span className="client-email">{client.email}</span>
      <div className="client-card-bottom">
        <div>
          <small>Facturado</small>
          <strong>
            {money(
              bills
                .filter((item) => item.status !== "Borrador")
                .reduce((sum, item) => sum + total(item), 0),
            )}
          </strong>
        </div>
        <button
          className="icon-button"
          aria-label={"Ver cliente " + client.name}
          onClick={() => onOpen(client)}
        >
          <Icon name="arrow" />
        </button>
      </div>
    </article>
  );
}
