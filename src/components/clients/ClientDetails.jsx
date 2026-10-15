import CustomerIdentity from "../clients/CustomerIdentity.jsx";
import Icon from "../ui/Icon.jsx";

export default function ClientDetails({
  item,
  invoices = [],
  onViewInvoices,
  onCreate,
  onEdit,
  onDelete,
}) {
  const clientId = item.cliente_id || item.id;
  const name = item.razon_social || item.name;
  const rfc = item.rfc || "Sin RFC registrado";
  const tipo = item.tipo_persona || item.sector || "RECEPTOR";
  const email = item.correo || item.email || "Sin correo";
  const regimen = item.regimen_fiscal || "N/A";
  const cp = item.codigo_postal || "N/A";

  const clientInvoices = invoices.filter(
    (inv) => inv.client === clientId || inv.receptor_id === clientId || inv.emisor_id === clientId
  );

  return (
    <div className="entity-detail">
      <CustomerIdentity client={item} subtitle={`${rfc} · ${tipo}`} />
      <dl>
        <dt>Razón Social</dt>
        <dd>{name}</dd>
        <dt>RFC Fiscal</dt>
        <dd>
          <strong>{rfc}</strong>
        </dd>
        <dt>Tipo de Persona</dt>
        <dd>{tipo}</dd>
        <dt>Régimen Fiscal</dt>
        <dd>{regimen}</dd>
        <dt>Código Postal</dt>
        <dd>{cp}</dd>
        <dt>Correo electrónico</dt>
        <dd>{email}</dd>
        <dt>Facturas asociadas</dt>
        <dd>{clientInvoices.length}</dd>
      </dl>
      <div className="modal-actions">
        {onEdit && (
          <button
            className="button secondary"
            onClick={() => onEdit(item)}
            style={{ marginRight: "auto" }}
          >
            Editar
          </button>
        )}
        <button
          className="button secondary"
          onClick={() => onViewInvoices(name)}
        >
          Ver facturas
        </button>
        <button
          className="button primary"
          onClick={() =>
            onCreate({
              client: clientId,
            })
          }
        >
          Nueva factura <Icon name="plus" size={14} />
        </button>
      </div>
    </div>
  );
}
