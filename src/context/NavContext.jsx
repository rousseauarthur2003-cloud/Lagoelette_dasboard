import { createContext, useCallback, useContext, useState } from 'react';

const NavContext = createContext(null);

export function NavProvider({ children }) {
  const [route, setRoute] = useState({ page: 'dashboard', params: {}, version: 0 });

  const navigate = useCallback((page, params = {}) => {
    setRoute((r) => ({ page, params, version: r.version + 1 }));
    if (typeof window !== 'undefined') window.scrollTo({ top: 0 });
  }, []);

  return <NavContext.Provider value={{ route, navigate }}>{children}</NavContext.Provider>;
}

export function useNav() {
  return useContext(NavContext);
}
