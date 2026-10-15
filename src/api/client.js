/**
 * Cliente HTTP para interactuar con la API de Facturación (Flask / AWS RDS / DynamoDB)
 */

const API_BASE = "/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.error || `Error HTTP ${response.status}`;
      const err = new Error(errorMsg);
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (err) {
    console.warn(`[API] Error en llamada a ${endpoint}:`, err.message);
    throw err;
  }
}

export const api = {
  // Diagnóstico
  getDiagnostico: () => request("/diagnostico"),

  // Clientes
  getClientes: (tipo) =>
    request(`/clientes${tipo ? `?tipo_persona=${tipo}` : ""}`),
  crearCliente: (data) =>
    request("/clientes", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  actualizarCliente: (id, data) =>
    request(`/clientes/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  eliminarCliente: (id) =>
    request(`/clientes/${id}`, {
      method: "DELETE",
    }),

  // Servicios
  getServicios: () => request("/servicios"),
  crearServicio: (data) =>
    request("/servicios", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  eliminarServicio: (id) =>
    request(`/servicios/${id}`, {
      method: "DELETE",
    }),

  // Características
  getCaracteristicas: () => request("/caracteristicas"),
  getServicioCaracteristicas: (servicioId) =>
    request(`/servicios/${servicioId}/caracteristicas`),
  asignarCaracteristica: (servicioId, data) =>
    request(`/servicios/${servicioId}/caracteristicas`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  desasignarCaracteristica: (servicioId, caracteristicaId) =>
    request(`/servicios/${servicioId}/caracteristicas/${caracteristicaId}`, {
      method: "DELETE",
    }),

  // Impuestos
  getImpuestos: () => request("/impuestos"),

  // Facturas
  getFacturas: () => request("/facturas"),
  getFactura: (id) => request(`/facturas/${id}`),
  emitirFactura: (data, idempotencyKey) => {
    const headers = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }
    return request("/facturas", {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },
  cancelarFactura: (id) =>
    request(`/facturas/${id}/cancelar`, {
      method: "PUT",
    }),
};
