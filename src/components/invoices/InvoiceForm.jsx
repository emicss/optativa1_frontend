import InvoiceTotals from "./InvoiceTotals.jsx";
import { useState } from "react";
import Icon from "../ui/Icon.jsx";
import { clients, services } from "../../data/demo.js";
import { money } from "../../utils/format.js";
import { subtotal } from "../../utils/invoices.js";
export default function InvoiceForm({
  initialClient,
  initialService,
  onSave,
  onCancel,
}) {
  const [lines, setLines] = useState([
    {
      key: 1,
      service: initialService || services[0].id,
      qty: 1,
    },
  ]);
  const [client, setClient] = useState(initialClient || "");
  const [date, setDate] = useState("2026-10-01"),
    [due, setDue] = useState("2026-10-15");
  function update(key, field, value) {
    setLines(
      lines.map((line) =>
        line.key === key
          ? {
              ...line,
              [field]: value,
            }
          : line,
      ),
    );
  }
  const sum = subtotal({
    lines,
  });
  return (
    <form
      className="invoice-form"
      onSubmit={(event) => {
        event.preventDefault();
        onSave({
          client,
          date,
          due,
          lines: lines.map(({ service, qty }) => ({
            service,
            qty: Number(qty),
          })),
        });
      }}
    >
      <p className="modal-description">
        Selecciona un cliente y agrega los servicios de tu factura.
      </p>
      <label htmlFor="billing-client">Cliente</label>
      <select
        required
        id="billing-client"
        value={client}
        onChange={(event) => setClient(event.target.value)}
      >
        <option value="" disabled>
          Seleccionar cliente
        </option>
        {clients.map((client) => (
          <option value={client.id} key={client.id}>
            {client.name}
          </option>
        ))}
      </select>
      <div className="form-columns">
        <div>
          <label htmlFor="billing-date">Fecha</label>
          <input
            type="date"
            required
            id="billing-date"
            value={date}
            onChange={(event) => {
              setDate(event.target.value);
              if (due < event.target.value) setDue(event.target.value);
            }}
          />
        </div>
        <div>
          <label htmlFor="billing-due">Vencimiento</label>
          <input
            type="date"
            required
            id="billing-due"
            min={date}
            value={due}
            onChange={(event) => setDue(event.target.value)}
          />
        </div>
      </div>
      <div className="line-label">
        Servicios <small>Precio antes de IVA</small>
      </div>
      <div className="editable-lines">
        {lines.map((line, index) => (
          <div className="editable-line" key={line.key}>
            <select
              aria-label={"Servicio " + (index + 1)}
              value={line.service}
              onChange={(event) =>
                update(line.key, "service", event.target.value)
              }
            >
              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name} · {money(service.price)}
                </option>
              ))}
            </select>
            <input
              aria-label={"Cantidad " + (index + 1)}
              type="number"
              min="1"
              max="999"
              step="1"
              required
              value={line.qty}
              onChange={(event) => update(line.key, "qty", event.target.value)}
            />
            <button
              type="button"
              className="icon-button danger"
              disabled={lines.length === 1}
              aria-label={"Quitar servicio " + (index + 1)}
              onClick={() =>
                setLines(lines.filter((item) => item.key !== line.key))
              }
            >
              <Icon name="trash" size={17} />
            </button>
          </div>
        ))}
      </div>
      <button
        className="text-button add-service"
        type="button"
        onClick={() =>
          setLines([
            ...lines,
            {
              key: Math.max(...lines.map((line) => line.key)) + 1,
              service: services[0].id,
              qty: 1,
            },
          ])
        }
      >
        <Icon name="plus" size={16} />
        Agregar servicio
      </button>
      <InvoiceTotals subtotal={sum} />
      <p className="preview-disclaimer">
        Borrador de demostración · No se emitirá una factura real
      </p>
      <div className="modal-actions">
        <button type="button" className="button secondary" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="button primary">
          Guardar borrador <Icon name="arrow" size={16} />
        </button>
      </div>
    </form>
  );
}
