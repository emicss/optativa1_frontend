import { useEffect, useState } from "react";
import { tabs } from "../data/navigation.js";
function readSection() {
  const section = location.hash.slice(1);
  return tabs.includes(section) ? section : "inicio";
}
export default function useNavigation() {
  const [view, setView] = useState(() => ({
    section: readSection(),
    revision: 0,
  }));
  useEffect(() => {
    const change = () =>
      setView((previous) => ({
        section: readSection(),
        revision: previous.revision + 1,
      }));
    window.addEventListener("hashchange", change);
    window.addEventListener("popstate", change);
    return () => {
      window.removeEventListener("hashchange", change);
      window.removeEventListener("popstate", change);
    };
  }, []);
  function navigate(section, options = {}) {
    if (!tabs.includes(section)) return;
    history.pushState(null, "", "#" + section);
    setView((previous) => ({
      section,
      ...options,
      revision: previous.revision + 1,
    }));
  }
  return {
    view,
    navigate,
  };
}
