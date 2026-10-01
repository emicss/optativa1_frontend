import { useState } from "react";
import SearchField from "../components/ui/SearchField.jsx";
import EmptyState from "../components/ui/EmptyState.jsx";
import FilterTabs from "../components/ui/FilterTabs.jsx";
import ServiceCard from "../components/services/ServiceCard.jsx";
import { services } from "../data/demo.js";
const categories = [
  "Todos",
  ...new Set(services.map((service) => service.category)),
];
export default function ServicesPage({ onOpenService }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("Todos");
  const filtered = services.filter(
    (service) =>
      (category === "Todos" || service.category === category) &&
      (service.name + service.description)
        .toLocaleLowerCase()
        .includes(query.toLocaleLowerCase()),
  );
  return (
    <section>
      <div className="section-toolbar">
        <div>
          <h2>Servicios que impulsan negocios</h2>
          <p>
            {services.length} servicios · {categories.length - 1} categorías
          </p>
        </div>
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Buscar un servicio…"
        />
      </div>
      <FilterTabs
        className="category-filters"
        label="Categorías de servicios"
        options={categories.map((value) => ({
          value,
          label: value,
        }))}
        value={category}
        onChange={setCategory}
      />
      <div className="service-grid">
        {filtered.map((service) => (
          <ServiceCard
            key={service.id}
            service={service}
            onOpen={onOpenService}
          />
        ))}
      </div>
      {!filtered.length && (
        <EmptyState
          title="No encontramos servicios"
          description="Prueba otra búsqueda o categoría."
        />
      )}
    </section>
  );
}
