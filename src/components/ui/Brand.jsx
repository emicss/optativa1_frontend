import Icon from "./Icon.jsx";
const Brand = () => (
  <a className="brand" href="/" aria-label="Folio, inicio">
    <span className="brand-icon">
      <Icon name="book" size={24} />
    </span>
    folio<span className="brand-dot">.</span>
  </a>
);
export default Brand;
