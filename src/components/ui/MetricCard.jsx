import Icon from "./Icon.jsx";
export default function MetricCard({ label, value, icon, color, note }) {
  return (
    <article className="metric">
      <div className="metric-top">
        <span>{label}</span>
        <span className={"metric-icon " + color}>
          <Icon name={icon} size={18} />
        </span>
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}
