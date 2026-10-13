import { services } from "../data/demo.js";
export const subtotal = (invoice) =>
  invoice.lines.reduce(
    (sum, line) =>
      sum +
      (services.find((service) => service.id === line.service)?.price || 0) *
        line.qty,
    0,
  );
export const TAX_RATE = 0.16;
export const roundMoney = (value) =>
  Math.round((value + Number.EPSILON) * 100) / 100;
export const tax = (amount) => roundMoney(amount * TAX_RATE);
export const total = (invoice) =>
  roundMoney(subtotal(invoice) + tax(subtotal(invoice)));
export function createDraft(data, invoices) {
  const next =
    Math.max(
      0,
      ...invoices.map((item) => Number(item.id.split("-").pop()) || 0),
    ) + 1;
  return {
    ...data,
    id: "FAC-2026-" + String(next).padStart(4, "0"),
    status: "Borrador",
  };
}
