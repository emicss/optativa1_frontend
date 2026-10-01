import Icon from "../ui/Icon.jsx";
import StatusBadge from "../ui/StatusBadge.jsx";
import CustomerIdentity from "../clients/CustomerIdentity.jsx";
import { clients } from "../../data/demo.js";
import { money, dateLabel } from "../../utils/format.js";
import { total } from "../../utils/invoices.js";
export default function InvoiceTable({ rows, onOpen, onClear }) {
  return (
    <div className="table-scroll">
      <table className="invoice-table">
        <thead>
          <tr>
            <th>FACTURA / CLIENTE</th>
            <th>FECHA</th>
            <th>IMPORTE</th>
            <th>ESTADO</th>
            <th>
              <span className="sr-only">Ver detalle</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((item) => (
            <tr key={item.id}>
              <td>
                <CustomerIdentity
                  client={clients.find((client) => client.id === item.client)}
                  subtitle={item.id}
                />
              </td>
              <td>{dateLabel(item.date)}</td>
              <td className="amount-cell">
                {money(total(item))}
                <small>MXN</small>
              </td>
              <td>
                <StatusBadge status={item.status} />
              </td>
              <td>
                <button
                  className="icon-button"
                  aria-label={"Ver " + item.id}
                  onClick={() => onOpen(item)}
                >
                  <Icon name="arrow" size={17} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length && (
        <div className="empty-state">
          <Icon name="search" size={30} />
          <h3>No encontramos facturas</h3>
          <p>Intenta con otro cliente, folio o estado.</p>
          <button className="button secondary" onClick={onClear}>
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}
