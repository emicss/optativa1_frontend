import LoginPage from "./pages/LoginPage.jsx";
import BillingWorkspace from "./components/layout/BillingWorkspace.jsx";
import useDemoSession from "./hooks/useDemoSession.js";
export default function App() {
  const { email, login, logout } = useDemoSession();
  return email ? (
    <BillingWorkspace email={email} onLogout={logout} />
  ) : (
    <LoginPage onLogin={login} />
  );
}
