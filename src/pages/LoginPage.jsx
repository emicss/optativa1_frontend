import { useState } from "react";
import Icon from "../components/ui/Icon.jsx";
import Brand from "../components/ui/Brand.jsx";
export default function LoginPage({ onLogin }) {
  const [visible, setVisible] = useState(false);
  function submit(event) {
    event.preventDefault();
    onLogin(new FormData(event.currentTarget).get("email"));
  }
  return (
    <main className="login-page">
      <section className="login-story">
        <Brand />
        <div className="story-content">
          <span className="eyebrow">TU NEGOCIO, BIEN ORGANIZADO.</span>
          <h1>
            Tu trabajo vale.
            <br />
            <em>Factúralo con claridad.</em>
          </h1>
          <p>
            Clientes, servicios y facturas en un mismo lugar. Menos pendientes,
            más tiempo para hacer crecer tu negocio.
          </p>
          <div className="paper-scene" aria-hidden="true">
            <div className="paper paper-back"></div>
            <div className="paper paper-front">
              <span className="paper-label">FACTURA / FAC-2026-0087</span>
              <div className="paper-heading">Todo en orden.</div>
              <div className="paper-line"></div>
              <div className="paper-line short"></div>
              <div className="paper-grid">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div className="paper-bottom">
                <span>ESTUDIO NORTE · MXN</span>
                <Icon name="arrow" />
              </div>
            </div>
            <div className="floating-note">
              <span className="check-circle">
                <Icon name="check" size={15} />
              </span>
              Pago recibido
            </div>
          </div>
        </div>
        <div className="story-footer">
          <span>Facturación más simple.</span>
          <span>© {new Date().getFullYear()} Folio</span>
        </div>
      </section>
      <section className="login-form-section">
        <span className="top-tag">
          <span className="status-dot"></span> TU ESPACIO DE FACTURACIÓN
        </span>
        <div className="login-form-wrap">
          <div className="welcome-icon">
            <Icon name="book" size={28} />
          </div>
          <h2>Qué bueno verte.</h2>
          <p className="muted">
            Tu negocio te espera. Retoma el control de tu facturación.
          </p>
          <form onSubmit={submit}>
            <label htmlFor="email">Correo electrónico</label>
            <input
              autoFocus
              id="email"
              name="email"
              type="email"
              placeholder="tu@ejemplo.com"
              autoComplete="username"
              required
            />
            <label htmlFor="password">Contraseña</label>
            <div className="password-field">
              <input
                id="password"
                type={visible ? "text" : "password"}
                placeholder="Escribe tu contraseña"
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="icon-button"
                aria-label={
                  visible ? "Ocultar contraseña" : "Mostrar contraseña"
                }
                aria-pressed={visible}
                onClick={() => setVisible(!visible)}
              >
                <Icon name="eye" />
              </button>
            </div>
            <button className="button primary login-submit" type="submit">
              Entrar a mi espacio <Icon name="arrow" />
            </button>
          </form>
          <div className="demo-note">
            <span className="demo-label">DEMO</span>
            <p>
              Usa cualquier correo y contraseña para explorar. Este acceso es
              solo una demostración.
            </p>
          </div>
        </div>
        <span className="login-bottom">Más claridad en cada factura.</span>
      </section>
    </main>
  );
}
