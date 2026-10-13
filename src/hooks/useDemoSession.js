import { useState } from "react";
const SESSION_KEY = "folio-demo-email";
export default function useDemoSession() {
  const [email, setEmail] = useState(() => {
    try {
      return sessionStorage.getItem(SESSION_KEY) || "";
    } catch {
      return "";
    }
  });
  function login(value) {
    try {
      sessionStorage.setItem(SESSION_KEY, value);
    } catch {
      /* La demo también funciona sin almacenamiento. */
    }
    setEmail(value);
    if (location.pathname === "/login") history.replaceState(null, "", "/");
  }
  function logout() {
    try {
      sessionStorage.removeItem(SESSION_KEY);
    } catch {
      /* La sesión en memoria se cierra igualmente. */
    }
    setEmail("");
    history.replaceState(null, "", "/login");
  }
  return {
    email,
    login,
    logout,
  };
}
