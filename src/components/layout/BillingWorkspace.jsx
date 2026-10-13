import { useCallback, useState } from "react";
import AppLayout from "./AppLayout.jsx";
import BillingDialog from "../invoices/BillingDialog.jsx";
import Toast from "../ui/Toast.jsx";
import OverviewPage from "../../pages/OverviewPage.jsx";
import InvoicesPage from "../../pages/InvoicesPage.jsx";
import ClientsPage from "../../pages/ClientsPage.jsx";
import ServicesPage from "../../pages/ServicesPage.jsx";
import useInvoices from "../../hooks/useInvoices.js";
import useNavigation from "../../hooks/useNavigation.js";
export default function BillingWorkspace({ email, onLogout }) {
  const { invoices, saveDraft } = useInvoices();
  const { view, navigate } = useNavigation();
  const [dialog, setDialog] = useState(null);
  const [notice, setNotice] = useState("");
  const dismissNotice = useCallback(() => setNotice(""), []);
  const closeDialog = () => setDialog(null);
  const create = (options = {}) =>
    setDialog({
      type: "create",
      ...options,
    });
  const openInvoice = (item) =>
    setDialog({
      type: "invoice",
      item,
    });
  const openClient = (item) =>
    setDialog({
      type: "client",
      item,
    });
  const openService = (item) =>
    setDialog({
      type: "service",
      item,
    });
  function save(data) {
    saveDraft(data);
    closeDialog();
    navigate("facturas");
    setNotice("Borrador de demostración guardado.");
  }
  function viewInvoices(clientName) {
    navigate("facturas", {
      query: clientName,
    });
    closeDialog();
  }
  return (
    <>
      <AppLayout
        email={email}
        section={view.section}
        invoices={invoices}
        onNavigate={navigate}
        onCreate={() => create()}
        onLogout={onLogout}
      >
        {view.section === "inicio" && (
          <OverviewPage
            invoices={invoices}
            onNavigate={navigate}
            onOpenInvoice={openInvoice}
            onOpenService={openService}
          />
        )}
        {view.section === "facturas" && (
          <InvoicesPage
            key={view.revision}
            invoices={invoices}
            initialQuery={view.query}
            initialFilter={view.filter}
            onOpenInvoice={openInvoice}
          />
        )}
        {view.section === "clientes" && (
          <ClientsPage
            key={view.revision}
            invoices={invoices}
            onOpenClient={openClient}
          />
        )}
        {view.section === "servicios" && (
          <ServicesPage key={view.revision} onOpenService={openService} />
        )}
        <BillingDialog
          dialog={dialog}
          invoices={invoices}
          onClose={closeDialog}
          onSave={save}
          onCreate={create}
          onViewInvoices={viewInvoices}
        />
      </AppLayout>
      <Toast message={notice} onDismiss={dismissNotice} />
    </>
  );
}
