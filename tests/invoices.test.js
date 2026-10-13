import test from 'node:test';
import assert from 'node:assert/strict';
import { subtotal, total, createDraft } from '../src/utils/invoices.js';
import { seedInvoices } from '../src/data/demo.js';

test('suma servicios y cantidades y aplica IVA una sola vez', () => {
  const invoice = { lines: [{ service: 'SRV-001', qty: 2 }, { service: 'SRV-004', qty: 1 }] };
  assert.equal(subtotal(invoice), 6200);
  assert.equal(total(invoice), 7192);
});
test('genera un folio nuevo y guarda como borrador sin modificar los datos de origen', () => {
  const original = structuredClone(seedInvoices);
  const data = { client: 'CL-001', date: '2026-10-01', due: '2026-10-15', lines: [{ service: 'SRV-001', qty: 1 }] };
  const first = createDraft(data, seedInvoices);
  const second = createDraft(data, [first, ...seedInvoices]);
  assert.equal(first.id, 'FAC-2026-0088');
  assert.equal(second.id, 'FAC-2026-0089');
  assert.equal(first.status, 'Borrador');
  assert.deepEqual(seedInvoices, original);
});
