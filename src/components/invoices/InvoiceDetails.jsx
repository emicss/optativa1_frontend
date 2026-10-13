import InvoiceTotals from "./InvoiceTotals.jsx";
import StatusBadge from "../ui/StatusBadge.jsx";
import CustomerIdentity from "../clients/CustomerIdentity.jsx";
import { clients, services } from "../../data/demo.js";
import { money, dateLabel } from "../../utils/format.js";
import { subtotal } from "../../utils/invoices.js";
export default function InvoiceDetails({ item, onClose }) {
  return (
    <div className="invoice-detail">
      <div className="invoice-detail-title">
        <span>{item.id}</span>
        <StatusBadge status={item.status} />
      </div>
      <CustomerIdentity
        client={clients.find((client) => client.id === item.client)}
      />
      <div className="detail-dates">
        <div>
          <small>Fecha de creación</small>
          <strong>{dateLabel(item.date)}</strong>
        </div>
        <div>
          <small>Vencimiento</small>
          <strong>{dateLabel(item.due)}</strong>
        </div>
      </div>
      <div className="invoice-lines">
        {item.lines.map((line, index) => {
          const service = services.find(
            (service) => service.id === line.service,
          );
          return (
            <div key={index}>
              <span>
                {service.name}
                <small>
                  {line.qty} × {money(service.price)}
                </small>
              </span>
              <strong>{money(line.qty * service.price)}</strong>
            </div>
          );
        })}
      </div>
      <InvoiceTotals subtotal={subtotal(item)} />
      <p className="preview-disclaimer">
        Vista de ejemplo · Sin validez fiscal
      </p>
      <button className="button secondary full-width" onClick={onClose}>
        Volver a mis facturas
      </button>
    </div>
  );
}
