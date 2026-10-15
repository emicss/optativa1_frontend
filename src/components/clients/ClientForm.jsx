import { useState } from "react";
import Icon from "../ui/Icon.jsx";

export default function ClientForm({ initialClient, onSave, onCancel }) {
  const isEditing = Boolean(initialClient?.cliente_id);
  const [rfc, setRfc] = useState(initialClient?.rfc || "");
  const [razonSocial, setRazonSocial] = useState(
    initialClient?.razon_social || initialClient?.name || "",
  );
  const [regimenFiscal, setRegimenFiscal] = useState(
    initialClient?.regimen_fiscal || "601",
  );
  const [codigoPostal, setCodigoPostal] = useState(
    initialClient?.codigo_postal || "06000",
  );
  const [correo, setCorreo] = useState(
    initialClient?.correo || initialClient?.email || "",
  );
  const [tipoPersona, setTipoPersona] = useState(
    initialClient?.tipo_persona || "RECEPTOR",
  );
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const cleanRfc = rfc.trim().toUpperCase();

    if (cleanRfc.length !== 12 && cleanRfc.length !== 13) {
      setError("El RFC debe contener 12 (moral) o 13 (física) caracteres.");
      return;
    }

    if (!razonSocial.trim()) {
      setError("La razón social es obligatoria.");
      return;
    }

    setError("");
    setSubmitting(true);
    try {
      await onSave({
        cliente_id: initialClient?.cliente_id,
        rfc: cleanRfc,
        razon_social: razonSocial.trim(),
        regimen_fiscal: regimenFiscal.trim(),
        codigo_postal: codigoPostal.trim(),
        correo: correo.trim(),
        tipo_persona: tipoPersona,
      });
    } catch (err) {
      setError(err.message || "Error al guardar el cliente.");
      setSubmitting(false);
    }
  }

  return (
    <form className="invoice-form" onSubmit={handleSubmit}>
      <p className="modal-description">
        {isEditing
          ? "Actualiza los datos fiscales del cliente."
          : "Ingresa los datos fiscales. Se registrará en RDS mediante sp_AltaCliente."}
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
          <label htmlFor="client-tipo">Tipo de Persona Fiscal</label>
          <select
            id="client-tipo"
            value={tipoPersona}
            onChange={(e) => setTipoPersona(e.target.value)}
            required
          >
            <option value="RECEPTOR">RECEPTOR (Cliente)</option>
            <option value="EMISOR">EMISOR (Mi Empresa)</option>
          </select>
        </div>
        <div>
          <label htmlFor="client-rfc">RFC (12 o 13 caracteres)</label>
          <input
            id="client-rfc"
            type="text"
            required
            maxLength={13}
            placeholder="AAA010101AAA"
            value={rfc}
            onChange={(e) => setRfc(e.target.value.toUpperCase())}
          />
        </div>
      </div>

      <label htmlFor="client-razon">Razón Social o Nombre Legal</label>
      <input
        id="client-razon"
        type="text"
        required
        placeholder="Empresa o Persona Física S.A. de C.V."
        value={razonSocial}
        onChange={(e) => setRazonSocial(e.target.value)}
      />

      <div className="form-columns">
        <div>
          <label htmlFor="client-regimen">Régimen Fiscal (SAT)</label>
          <select
            id="client-regimen"
            value={regimenFiscal}
            onChange={(e) => setRegimenFiscal(e.target.value)}
          >
            <option value="601">601 · General de Ley Personas Morales</option>
            <option value="612">
              612 · Personas Físicas con Actividades Empresariales
            </option>
            <option value="626">
              626 · Régimen Simplificado de Confianza (RESICO)
            </option>
            <option value="605">605 · Sueldos y Salarios</option>
            <option value="606">606 · Arrendamiento</option>
          </select>
        </div>
        <div>
          <label htmlFor="client-cp">Código Postal (C.P.)</label>
          <input
            id="client-cp"
            type="text"
            maxLength={5}
            placeholder="06000"
            value={codigoPostal}
            onChange={(e) => setCodigoPostal(e.target.value)}
          />
        </div>
      </div>

      <label htmlFor="client-correo">Correo Electrónico para Facturación</label>
      <input
        id="client-correo"
        type="email"
        placeholder="contacto@empresa.com"
        value={correo}
        onChange={(e) => setCorreo(e.target.value)}
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
          {submitting
            ? "Guardando..."
            : isEditing
              ? "Actualizar Cliente"
              : "Registrar Cliente (sp_AltaCliente)"}
          <Icon name="arrow" size={16} />
        </button>
      </div>
    </form>
  );
}
