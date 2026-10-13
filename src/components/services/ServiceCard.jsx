import ServiceTags from "./ServiceTags.jsx";
import Icon from "../ui/Icon.jsx";
import { money } from "../../utils/format.js";
export default function ServiceCard({ service, onOpen }) {
  return (
    <article className="service-card">
      <div className="service-card-top">
        <span className={"service-symbol " + service.color}>
          <Icon name={service.icon} size={24} />
        </span>
        <span>{service.category}</span>
      </div>
      <h3>{service.name}</h3>
      <p>{service.description}</p>
      <ServiceTags tags={service.tags} />
      <div className="service-card-bottom">
        <div>
          <strong>{money(service.price)}</strong>
          <span> / {service.unit}</span>
          <small>Precio antes de IVA</small>
        </div>
        <button
          className="icon-button"
          aria-label={"Ver servicio " + service.name}
          onClick={() => onOpen(service)}
        >
          <Icon name="arrow" />
        </button>
      </div>
    </article>
  );
}
