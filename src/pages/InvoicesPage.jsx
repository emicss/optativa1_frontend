import { useState } from "react";
import SearchField from "../components/ui/SearchField.jsx";
import FilterTabs from "../components/ui/FilterTabs.jsx";
import InvoiceTable from "../components/invoices/InvoiceTable.jsx";
import { clients } from "../data/demo.js";
const statuses = [
  {
    value: "Todas",
    label: "Todas",
  },
  {
    value: "Pagada",
    label: "Pagadas",
  },
  {
    value: "Pendiente",
    label: "Pendientes",
  },
  {
    value: "Vencida",
    label: "Vencidas",
  },
  {
    value: "Borrador",
    label: "Borradores",
  },
];
export default function InvoicesPage({
  invoices,
  initialQuery = "",
  initialFilter = "Todas",
  onOpenInvoice,
}) {
  const [query, setQuery] = useState(initialQuery);
  const [filter, setFilter] = useState(initialFilter);
  const filtered = invoices.filter(
    (item) =>
      (filter === "Todas" || item.status === filter) &&
      (item.id + " " + clients.find((client) => client.id === item.client).name)
        .toLocaleLowerCase()
        .includes(query.toLocaleLowerCase()),
  );
  const options = statuses.map((status) => ({
    ...status,
    count:
      status.value === "Todas"
        ? invoices.length
        : invoices.filter((item) => item.status === status.value).length,
  }));
  return (
    <section className="documents-panel">
      <div className="panel-toolbar">
        <div>
          <h2>
            Todas tus facturas{" "}
            <span className="count-pill">{invoices.length}</span>
          </h2>
          <span>Da seguimiento a cada etapa de tu facturación</span>
        </div>
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Buscar cliente o folio…"
        />
      </div>
      <FilterTabs
        options={options}
        value={filter}
        onChange={setFilter}
        label="Filtrar por estado"
      />
      <InvoiceTable
        rows={filtered}
        onOpen={onOpenInvoice}
        onClear={() => {
          setQuery("");
          setFilter("Todas");
        }}
      />
      <div className="panel-footer">
        <span>{filtered.length} resultados</span>
        <span>IMPORTES EN MXN · IVA INCLUIDO</span>
      </div>
    </section>
  );
}
