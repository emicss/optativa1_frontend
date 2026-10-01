import MetricCard from "../components/ui/MetricCard.jsx";
import Icon from "../components/ui/Icon.jsx";
import InvoiceTable from "../components/invoices/InvoiceTable.jsx";
import { clients, services } from "../data/demo.js";
import { money } from "../utils/format.js";
import { total } from "../utils/invoices.js";
export default function OverviewPage({
  invoices,
  onNavigate,
  onOpenInvoice,
  onOpenService,
}) {
  const paid = invoices.filter((item) => item.status === "Pagada");
  const outstanding = invoices.filter((item) =>
    ["Pendiente", "Vencida"].includes(item.status),
  );
  const overdue = invoices.filter((item) => item.status === "Vencida");
  const issued = invoices.filter((item) => item.status !== "Borrador");
  return (
    <>
      <div className="overview-stats">
        {[
          [
            "Total facturado",
            money(issued.reduce((sum, item) => sum + total(item), 0)),
            "file",
            "sage",
            issued.length + " facturas emitidas",
          ],
          [
            "Cobrado",
            money(paid.reduce((sum, item) => sum + total(item), 0)),
            "check",
            "sage",
            paid.length + " facturas pagadas",
          ],
          [
            "Por cobrar",
            money(outstanding.reduce((sum, item) => sum + total(item), 0)),
            "file",
            "sand",
            outstanding.length + " facturas por cobrar",
          ],
          [
            "Clientes",
            clients.length.toString().padStart(2, "0"),
            "users",
            "lilac",
            "Relaciones que suman",
          ],
        ].map(([label, value, icon, color, note]) => (
          <MetricCard
            key={label}
            label={label}
            value={value}
            icon={icon}
            color={color}
            note={note}
          />
        ))}
      </div>
      <div className="overview-grid">
        <section className="documents-panel recent-panel">
          <div className="panel-toolbar">
            <div>
              <h2>Facturas recientes</h2>
              <span>Los últimos movimientos de tu negocio</span>
            </div>
            <button
              className="text-button"
              onClick={() => onNavigate("facturas")}
            >
              Ver todas <Icon name="arrow" size={15} />
            </button>
          </div>
          <InvoiceTable rows={invoices.slice(0, 5)} onOpen={onOpenInvoice} />
          <div className="panel-footer">
            <span>
              Mostrando {Math.min(invoices.length, 5)} de {invoices.length}{" "}
              facturas
            </span>
            <span>IMPORTES EN MXN</span>
          </div>
        </section>
        <div className="overview-side">
          <section className="collection-health">
            <span className="eyebrow">EL PULSO DE TU NEGOCIO</span>
            <h2>
              Cada cobro,
              <br />
              un paso adelante.
            </h2>
            <div
              className="collection-ring"
              style={{
                "--progress": (paid.length / issued.length) * 100 + "%",
              }}
            >
              <div>
                <strong>
                  {Math.round((paid.length / issued.length) * 100)}
                  <small>%</small>
                </strong>
                <span>facturas pagadas</span>
              </div>
            </div>
            <div className="health-legend">
              <span>
                <i></i>Pagadas <strong>{paid.length}</strong>
              </span>
              <span>
                <i></i>Por cobrar <strong>{outstanding.length}</strong>
              </span>
            </div>
          </section>
          <section className="attention-card">
            <span className="attention-mark">!</span>
            <div>
              <h3>
                {overdue.length} factura{overdue.length !== 1 ? "s" : ""} por
                revisar
              </h3>
              <p>Hay pagos que superaron su fecha de vencimiento.</p>
              <button
                className="text-button"
                onClick={() =>
                  onNavigate("facturas", {
                    filter: "Vencida",
                  })
                }
              >
                Revisar pendientes <Icon name="arrow" size={14} />
              </button>
            </div>
          </section>
        </div>
      </div>
      <section className="quick-services">
        <div>
          <span className="eyebrow">TU CATÁLOGO, A UN CLIC</span>
          <h2>Lo que haces, tiene valor.</h2>
          <p>Encuentra el servicio ideal para tu próxima factura.</p>
        </div>
        <div className="service-mini-list">
          {services.slice(0, 3).map((service) => (
            <button key={service.id} onClick={() => onOpenService(service)}>
              <span className={"metric-icon " + service.color}>
                <Icon name={service.icon} />
              </span>
              <span>
                <strong>{service.name}</strong>
                <small>
                  {money(service.price)} / {service.unit}
                </small>
              </span>
              <Icon name="arrow" size={15} />
            </button>
          ))}
        </div>
      </section>
    </>
  );
}
