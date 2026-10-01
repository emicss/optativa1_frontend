import { useEffect } from "react";
import Icon from "./Icon.jsx";
export default function Toast({ message, onDismiss }) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(onDismiss, 4500);
    return () => clearTimeout(timer);
  }, [message, onDismiss]);
  return message ? (
    <div className="toast" role="status">
      <Icon name="check" />
      {message}
    </div>
  ) : null;
}
