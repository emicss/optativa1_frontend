export default function FilterTabs({
  options,
  value,
  onChange,
  className = "filter-tabs",
  label,
}) {
  return (
    <div className={className} aria-label={label} role="group">
      {options.map((option) => (
        <button
          type="button"
          key={option.value}
          className={value === option.value ? "selected" : ""}
          aria-pressed={value === option.value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
          {option.count !== undefined && <span>{option.count}</span>}
        </button>
      ))}
    </div>
  );
}
