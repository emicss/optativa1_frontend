/**
 * Script interactivo y utilidades de seguridad para el frontend monolítico de Folio
 */

/**
 * Escapa caracteres peligrosos en el cliente para prevenir DOM XSS
 */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function showToast(message, duration = 3500) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";

  const iconSpan = document.createElement("span");
  iconSpan.textContent = "✦";

  const msgSpan = document.createElement("span");
  // Uso de textContent garantiza que no se ejecute HTML o JavaScript inyectado
  msgSpan.textContent = String(message || '');

  toast.appendChild(iconSpan);
  toast.appendChild(msgSpan);
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Cerrar modales con la tecla Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll("dialog[open]").forEach((d) => d.close());
  }
});

