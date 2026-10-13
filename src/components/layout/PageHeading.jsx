import Icon from "../ui/Icon.jsx";
import { titles, captions } from "../../data/navigation.js";
export default function PageHeading({ section, onCreate }) {
  return (
    <div className="page-heading">
      <div>
        <span className="eyebrow">
          {section === "inicio"
            ? "CADA NÚMERO CUENTA UNA HISTORIA"
            : "TU NEGOCIO, BIEN ORGANIZADO"}
        </span>
        <h1>
          {titles[section]}
          <span>.</span>
        </h1>
        <p className="muted">{captions[section]}</p>
      </div>
      <button className="button primary" onClick={onCreate}>
        <Icon name="plus" size={18} />
        Nueva factura
      </button>
    </div>
  );
}
