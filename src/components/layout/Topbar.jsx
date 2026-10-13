import { titles } from "../../data/navigation.js";
export default function Topbar({ email, section }) {
  return (
    <header className="topbar">
      <span>
        Mi negocio <span className="breadcrumb">/</span>
        <strong>{section === "inicio" ? "Inicio" : titles[section]}</strong>
      </span>
      <div className="topbar-right">
        <span className="demo-pill">
          <span className="status-dot"></span> Vista de demostración
        </span>
        <span className="currency-label">MXN</span>
        <div className="avatar">{email[0].toUpperCase()}</div>
      </div>
    </header>
  );
}
