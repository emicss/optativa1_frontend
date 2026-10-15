import { useState } from "react";
import Icon from "../ui/Icon.jsx";

export default function ServiceForm({ onSave, onCancel }) {
  const [sku, setSku] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [precioBase, setPrecioBase] = useState("");
  const [claveSat, setClaveSat] = useState("80101500");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!sku.trim() || !descripcion.trim() || !precioBase) {
      setError("Completa SKU, descripción y precio base.");
      return;
    }

    const precio = parseFloat(precioBase);
    if (isNaN(precio) || precio <= 0) {
      setError("El precio base debe ser un número positivo.");
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      await onSave({
        sku: sku.trim().toUpperCase(),
        descripcion: descripcion.trim(),
        precio_base: precio,
        clave_sat: claveSat.trim(),
      });
    } catch (err) {
      setError(err.message || "Error al registrar servicio.");
      setSubmitting(false);
    }
  }

  return (
    <form className="invoice-form" onSubmit={handleSubmit}>
      <p className="modal-description">
        Ingresa los datos del nuevo servicio para guardarlo en el catálogo RDS mediante <code>sp_CrearServicioCatalogos</code>.
      </p>

      {error && (
        <div
          style={{
            padding: "10px 14px",
            background: "#fdf2f0",
            color: "#b24531",
            borderRadius: 8,
            fontSize: 13,
            marginBottom: 12,
          }}
        >
          {error}
        </div>
      )}

      <div className="form-columns">
        <div>
          <label htmlFor="service-sku">SKU o Código Único</label>
          <input
            id="service-sku"
            type="text"
            required
            placeholder="SRV-101"
            value={sku}
            onChange={(e) => setSku(e.target.value.toUpperCase())}
          />
        </div>
        <div>
          <label htmlFor="service-clave-sat">Clave SAT (Catálogo SAT)</label>
          <input
            id="service-clave-sat"
            type="text"
            required
            placeholder="80101500"
            value={claveSat}
            onChange={(e) => setClaveSat(e.target.value)}
          />
        </div>
      </div>

      <label htmlFor="service-desc">Descripción del Servicio</label>
      <input
        id="service-desc"
        type="text"
        required
        placeholder="Ej. Consultoría Fiscal y Financiera Avanzada"
        value={descripcion}
        onChange={(e) => setDescripcion(e.target.value)}
      />

      <label htmlFor="service-precio">Precio Base (Antes de IVA)</label>
      <input
        id="service-precio"
        type="number"
        step="0.01"
        min="0.01"
        required
        placeholder="1500.00"
        value={precioBase}
        onChange={(e) => setPrecioBase(e.target.value)}
      />

      <div className="modal-actions" style={{ marginTop: 24 }}>
        <button
          type="button"
          className="button secondary"
          onClick={onCancel}
          disabled={submitting}
        >
          Cancelar
        </button>
        <button type="submit" className="button primary" disabled={submitting}>
          {submitting ? "Guardando..." : "Guardar en Catálogo (sp_CrearServicioCatalogos)"}
          <Icon name="arrow" size={16} />
        </button>
      </div>
    </form>
  );
}
