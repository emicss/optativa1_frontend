import { useEffect, useState } from "react";
import { clients, services, seedInvoices } from "../data/demo.js";
import { createDraft } from "../utils/invoices.js";
const STORAGE_KEY = "folio-billing-demo";
function readInvoices() {
  try {
    const data = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
    const valid =
      Array.isArray(data) &&
      data.length &&
      data.every(
        (item) =>
          typeof item.id === "string" &&
          clients.some((client) => client.id === item.client) &&
          ["Pagada", "Pendiente", "Vencida", "Borrador"].includes(
            item.status,
          ) &&
          /^\d{4}-\d{2}-\d{2}$/.test(item.date) &&
          /^\d{4}-\d{2}-\d{2}$/.test(item.due) &&
          Array.isArray(item.lines) &&
          item.lines.length &&
          item.lines.every(
            (line) =>
              services.some((service) => service.id === line.service) &&
              Number.isInteger(line.qty) &&
              line.qty > 0,
          ),
      );
    return valid ? data : seedInvoices;
  } catch {
    return seedInvoices;
  }
}
export default function useInvoices() {
  const [invoices, setInvoices] = useState(readInvoices);
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(invoices));
    } catch {
      /* Se conservan en memoria si el navegador bloquea storage. */
    }
  }, [invoices]);
  function saveDraft(data) {
    setInvoices((previous) => [createDraft(data, previous), ...previous]);
  }
  return {
    invoices,
    saveDraft,
  };
}
