import { useState } from "react";
import SearchField from "../components/ui/SearchField.jsx";
import EmptyState from "../components/ui/EmptyState.jsx";
import ClientCard from "../components/clients/ClientCard.jsx";
import { clients } from "../data/demo.js";
export default function ClientsPage({ invoices, onOpenClient }) {
  const [query, setQuery] = useState("");
  const filtered = clients.filter((client) =>
    (client.name + client.contact + client.email)
      .toLocaleLowerCase()
      .includes(query.toLocaleLowerCase()),
  );
  return (
    <section>
      <div className="section-toolbar">
        <div>
          <h2>Personas detrás de cada proyecto</h2>
          <p>{clients.length} clientes en tu directorio</p>
        </div>
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Buscar cliente o contacto…"
        />
      </div>
      <div className="client-grid">
        {filtered.map((client) => (
          <ClientCard
            key={client.id}
            client={client}
            invoices={invoices}
            onOpen={onOpenClient}
          />
        ))}
      </div>
      {!filtered.length && (
        <EmptyState
          title="No encontramos clientes"
          description="Prueba con otro nombre o contacto."
        />
      )}
    </section>
  );
}
