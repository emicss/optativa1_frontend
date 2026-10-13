import Sidebar from "./Sidebar.jsx";
import Topbar from "./Topbar.jsx";
import PageHeading from "./PageHeading.jsx";
export default function AppLayout({
  children,
  section,
  email,
  invoices,
  onNavigate,
  onCreate,
  onLogout,
}) {
  return (
    <div className="app-shell billing-shell">
      <Sidebar
        email={email}
        section={section}
        invoices={invoices}
        onNavigate={onNavigate}
        onCreate={onCreate}
        onLogout={onLogout}
      />
      <main className="dashboard">
        <Topbar email={email} section={section} />
        <div className="dashboard-content">
          <PageHeading section={section} onCreate={onCreate} />
          {children}
          <footer className="dashboard-footer">
            <span>
              <span className="status-dot" /> Datos de ejemplo para explorar el
              diseño
            </span>
            <span>Folio · Facturación más simple</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
