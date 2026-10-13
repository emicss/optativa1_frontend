import { money } from "../../utils/format.js";
import { tax, roundMoney } from "../../utils/invoices.js";
export default function InvoiceTotals({ subtotal }) {
  return (
    <div className="total-summary">
      <p>
        <span>Subtotal</span>
        <strong>{money(subtotal)}</strong>
      </p>
      <p>
        <span>IVA (16%)</span>
        <strong>{money(tax(subtotal))}</strong>
      </p>
      <p className="grand-total">
        <span>Total</span>
        <strong>
          {money(roundMoney(subtotal + tax(subtotal)))} <small>MXN</small>
        </strong>
      </p>
    </div>
  );
}
