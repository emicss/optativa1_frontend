import Icon from "./Icon.jsx";
export default function SearchField({ value, onChange, placeholder }) {
  return (
    <div className="search-field">
      <Icon name="search" size={18} />
      <input
        aria-label={placeholder}
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      {value && (
        <button
          className="icon-button"
          aria-label="Limpiar búsqueda"
          onClick={() => onChange("")}
        >
          <Icon name="close" size={15} />
        </button>
      )}
    </div>
  );
}
