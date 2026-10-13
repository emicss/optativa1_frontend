import ServiceTags from "./ServiceTags.jsx";
import Icon from "../ui/Icon.jsx";
import { money } from "../../utils/format.js";
export default function ServiceDetails({ item, onCreate }) {
  return (
    <div className="entity-detail">
      <span className={"service-symbol " + item.color}>
        <Icon name={item.icon} size={26} />
      </span>
      <h3>{item.name}</h3>
      <p className="modal-description">{item.description}</p>
      <dl>
        <dt>Categoría</dt>
        <dd>{item.category}</dd>
        <dt>Precio por {item.unit}</dt>
        <dd>{money(item.price)} + IVA</dd>
      </dl>
      <ServiceTags tags={item.tags} />
      <button
        className="button primary full-width"
        onClick={() =>
          onCreate({
            service: item.id,
          })
        }
      >
        Agregar a nueva factura <Icon name="plus" size={16} />
      </button>
    </div>
  );
}
