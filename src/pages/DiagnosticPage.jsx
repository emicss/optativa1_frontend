import { useEffect, useState } from "react";
import Icon from "../components/ui/Icon.jsx";
import { api } from "../api/client.js";

export default function DiagnosticPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDiagnostico = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDiagnostico();
      setData(res);
    } catch (err) {
      setError(err.message || "Error al conectar con el servidor Flask");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDiagnostico();
  }, []);

  const rds = data?.rds;
  const dynamo = data?.dynamodb;

  return (
    <section className="diagnostic-view">
      <div className="section-toolbar">
        <div>
          <h2>Panel de Diagnóstico · AWS RDS & DynamoDB</h2>
          <p>Supervisa el estado de la conexión, las 8 tablas SQL, los 10 Stored Procedures y NoSQL.</p>
        </div>
        <button
          className="button secondary"
          onClick={loadDiagnostico}
          disabled={loading}
          style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
        >
          <Icon name="refresh" size={16} />
          {loading ? "Verificando..." : "Actualizar diagnóstico"}
        </button>
      </div>

      {error && (
        <div className="attention-card" style={{ marginBottom: 24, borderLeftColor: "#b24531" }}>
          <span className="attention-mark" style={{ background: "#f9e5e3", color: "#b24531" }}>!</span>
          <div>
            <h3>Atención: No se pudo conectar con el backend</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Tarjeta de Resumen de Conexión RDS */}
      <div className="overview-stats" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 24 }}>
        <article className="metric">
          <div className="metric-top">
            <span className="metric-label">Conexión AWS RDS</span>
            <span className={`metric-icon ${rds?.connected ? "sage" : "sand"}`}>
              <Icon name="database" />
            </span>
          </div>
          <div className="metric-value">
            {rds?.connected ? "Conectado" : "Desconectado"}
          </div>
          <small className="metric-note">
            {rds?.host}:{rds?.port} ({rds?.database || "facturacion_db"})
          </small>
        </article>

        <article className="metric">
          <div className="metric-top">
            <span className="metric-label">Motor de Base de Datos</span>
            <span className="metric-icon sky">
              <Icon name="grid" />
            </span>
          </div>
          <div className="metric-value" style={{ fontSize: 20 }}>
            {rds?.engine_version ? rds.engine_version.split("-")[0] : "MySQL/MariaDB"}
          </div>
          <small className="metric-note">
            {rds?.connected ? "Instancia activa en AWS RDS" : "Esperando configuración .env"}
          </small>
        </article>

        <article className="metric">
          <div className="metric-top">
            <span className="metric-label">AWS DynamoDB (NoSQL)</span>
            <span className={`metric-icon ${dynamo?.connected ? "sage" : "lilac"}`}>
              <Icon name="check" />
            </span>
          </div>
          <div className="metric-value">
            {dynamo?.connected ? "Activo" : "Standby"}
          </div>
          <small className="metric-note">
            Región: {dynamo?.region || "us-east-1"} (Idempotencia y Logs)
          </small>
        </article>
      </div>

      {/* Tablas SQL (8 tablas) */}
      <div className="documents-panel" style={{ marginBottom: 28 }}>
        <div className="panel-toolbar">
          <div>
            <h2>8 Tablas SQL Requeridas en RDS</h2>
            <span>Conteo de registros actuales en cada entidad del modelo relacional</span>
          </div>
        </div>

        <div className="table-scroll">
          <table className="invoice-table">
            <thead>
              <tr>
                <th>TABLA</th>
                <th>TIPO</th>
                <th>REGISTROS</th>
                <th>ESTADO EN RDS</th>
                <th>REQUISITO</th>
              </tr>
            </thead>
            <tbody>
              {rds?.tablas &&
                Object.entries(rds.tablas).map(([tableName, info]) => {
                  let reqNote = "Modelo SQL";
                  if (tableName === "Servicios") reqNote = "Catálogo +100 registros";
                  if (tableName === "Caracteristicas") reqNote = "Catálogo +50 registros";
                  if (tableName === "Servicio_Caracteristicas") reqNote = "Relación N:M";
                  if (tableName === "Clientes") reqNote = "Emisores y Receptores";

                  return (
                    <tr key={tableName}>
                      <td>
                        <strong>{tableName}</strong>
                      </td>
                      <td>
                        <span style={{ fontSize: 12, color: "#6e7766" }}>
                          {tableName.includes("_") ? "Intermedia / N:M" : "Entidad Principal"}
                        </span>
                      </td>
                      <td className="amount-cell">
                        <strong>{info.count ?? 0}</strong>
                        <small>filas</small>
                      </td>
                      <td>
                        <span
                          className={`status-badge ${
                            info.exists ? "paid" : "overdue"
                          }`}
                        >
                          <span />
                          {info.exists ? "Tabla Creada" : "Pendiente"}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: 12, color: "#4f654b" }}>{reqNote}</span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stored Procedures (10 SPs) */}
      <div className="documents-panel">
        <div className="panel-toolbar">
          <div>
            <h2>10 Procedimientos Almacenados (Stored Procedures)</h2>
            <span>Prioridad de ejecución transaccional con fallback SQL transparente</span>
          </div>
        </div>

        <div className="table-scroll">
          <table className="invoice-table">
            <thead>
              <tr>
                <th>PROCEDIMIENTO</th>
                <th>FUNCIÓN TRANSACCIONAL</th>
                <th>DISPONIBILIDAD</th>
                <th>ESTRATEGIA BACKEND</th>
              </tr>
            </thead>
            <tbody>
              {rds?.stored_procedures &&
                Object.entries(rds.stored_procedures).map(([spName, spInfo]) => {
                  const spDescriptions = {
                    sp_AltaCliente: "Valida RFC (12-13 chars) e inserta en Clientes",
                    sp_CrearServicioCatalogos: "Inserta servicios en catálogo de RDS",
                    sp_AsignarCaracteristica: "Vincula servicio y característica en Servicio_Caracteristicas",
                    sp_ValidarDatosFiscales: "Verifica emisor y receptor activos",
                    sp_GenerarFolioFactura: "Genera folio y crea encabezado de Facturas",
                    sp_InsertarPartida: "Inserta concepto en Factura_Detalles",
                    sp_CalcularTotales: "Calcula impuestos y actualiza subtotal y total",
                    sp_ActualizarUUID: "Guarda UUID SAT y timbra la factura",
                    sp_ConsultarFacturaCompleta: "SELECT con JOINs de factura completa",
                    sp_CancelarFactura: "Cambia estado a CANCELADA",
                  };

                  return (
                    <tr key={spName}>
                      <td>
                        <code style={{ fontSize: 13, color: "#2d4734", fontWeight: 600 }}>{spName}</code>
                      </td>
                      <td>
                        <span style={{ fontSize: 13, color: "#546050" }}>
                          {spDescriptions[spName] || "Operación de facturación"}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`status-badge ${
                            spInfo.exists ? "paid" : "pending"
                          }`}
                        >
                          <span />
                          {spInfo.exists ? "En RDS (CALL)" : "Fallback SQL"}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: 12, color: "#455941" }}>
                          {spInfo.exists ? "CALL " + spName : "Transacción SQL Directa"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
