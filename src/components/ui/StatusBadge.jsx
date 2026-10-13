const statusClass = (value) =>
  ({
    Pagada: "paid",
    Pendiente: "pending",
    Vencida: "overdue",
    Borrador: "draft",
  })[value];
export default function StatusBadge({ status }) {
  return (
    <span className={"status-badge " + statusClass(status)}>
      <span />
      {status}
    </span>
  );
}
