import CustomerIdentity from "../clients/CustomerIdentity.jsx";
export default function ClientDetails({
  item,
  invoices,
  onViewInvoices,
  onCreate,
}) {
  return (
    <div className="entity-detail">
      <CustomerIdentity client={item} subtitle={item.sector} />
      <dl>
        <dt>Contacto</dt>
        <dd>{item.contact}</dd>
        <dt>Correo electrónico</dt>
        <dd>{item.email}</dd>
        <dt>Clave de cliente</dt>
        <dd>{item.id}</dd>
        <dt>Facturas registradas</dt>
        <dd>{invoices.filter((item) => item.client === item.id).length}</dd>
      </dl>
      <div className="modal-actions">
        <button
          className="button secondary"
          onClick={() => onViewInvoices(item.name)}
        >
          Ver facturas
        </button>
        <button
          className="button primary"
          onClick={() =>
            onCreate({
              client: item.id,
            })
          }
        >
          Nueva factura
        </button>
      </div>
    </div>
  );
}
