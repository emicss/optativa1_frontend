import Modal from "../ui/Modal.jsx";
import InvoiceForm from "./InvoiceForm.jsx";
import InvoiceDetails from "./InvoiceDetails.jsx";
import ClientDetails from "../clients/ClientDetails.jsx";
import ServiceDetails from "../services/ServiceDetails.jsx";
const titles = {
  create: "Nueva factura",
  invoice: "Detalle de factura",
  client: "Detalle del cliente",
  service: "Detalle del servicio",
};
export default function BillingDialog({
  dialog,
  invoices,
  onClose,
  onSave,
  onCreate,
  onViewInvoices,
}) {
  if (!dialog) return null;
  return (
    <Modal title={titles[dialog.type]} onClose={onClose}>
      {dialog.type === "create" && (
        <InvoiceForm
          initialClient={dialog.client}
          initialService={dialog.service}
          onCancel={onClose}
          onSave={onSave}
        />
      )}
      {dialog.type === "invoice" && (
        <InvoiceDetails item={dialog.item} onClose={onClose} />
      )}
      {dialog.type === "client" && (
        <ClientDetails
          item={dialog.item}
          invoices={invoices}
          onViewInvoices={onViewInvoices}
          onCreate={onCreate}
        />
      )}
      {dialog.type === "service" && (
        <ServiceDetails item={dialog.item} onCreate={onCreate} />
      )}
    </Modal>
  );
}
