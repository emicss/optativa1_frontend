import Icon from "../ui/Icon.jsx";
import Brand from "../ui/Brand.jsx";
import { titles, tabs } from "../../data/navigation.js";
export default function Sidebar({
  email,
  section,
  invoices,
  onNavigate,
  onCreate,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <Brand />
      <div className="company-switch">
        <span className="company-symbol">N</span>
        <div>
          <strong>Mi negocio</strong>
          <small>Espacio de facturación</small>
        </div>
        <span className="company-chevron">⌄</span>
      </div>
      <div className="workspace-label">PRINCIPAL</div>
      <nav aria-label="Navegación principal">
        {tabs.map((tab, index) => (
          <button
            key={tab}
            className={"nav-item " + (section === tab ? "active" : "")}
            aria-label={tab === "inicio" ? "Inicio" : titles[tab]}
            title={tab === "inicio" ? "Inicio" : titles[tab]}
            aria-current={section === tab ? "page" : undefined}
            onClick={() => onNavigate(tab)}
          >
            <Icon name={["grid", "file", "users", "book"][index]} />
            <span className="nav-label">
              {tab === "inicio" ? "Inicio" : titles[tab]}
            </span>
            {tab === "facturas" && (
              <span className="nav-count">{invoices.length}</span>
            )}
          </button>
        ))}
      </nav>
      <div className="sidebar-tip">
        <span className="tip-icon">✦</span>
        <h3>Tu negocio, en orden.</h3>
        <p>Clientes, servicios y facturas conectados en un mismo lugar.</p>
        <button onClick={onCreate}>
          Crea una factura <Icon name="arrow" size={14} />
        </button>
      </div>
      <div className="profile">
        <div className="avatar">{email[0].toUpperCase()}</div>
        <div>
          <strong>Mi cuenta</strong>
          <span title={email}>{email}</span>
        </div>
        <button
          className="icon-button"
          aria-label="Cerrar sesión"
          onClick={onLogout}
        >
          <Icon name="logout" />
        </button>
      </div>
    </aside>
  );
}
