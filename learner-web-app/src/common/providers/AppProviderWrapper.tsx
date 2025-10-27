import * as React from 'react';
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import type { Authentication, Navigation } from '@toolpad/core';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import SessionContext, { type Session } from '../../contexts/SessionContext';
import { signOut, getCurrentSession } from '../../services/auth';

const NAVIGATION: Navigation = [
  {
    kind: 'header',
    title: 'Main items',
  },
  {
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
  {
    segment: 'orders',
    title: 'Orders',
    icon: <ShoppingCartIcon />,
  },
];

const BRANDING = {
  title: 'Learnora',
};

const AUTHENTICATION: Authentication = {
  signIn: () => {
    // This is handled by the SignInPage component
    // No-op function, actual sign-in happens in SignInPage
  },
  signOut: () => {
    signOut();
  },
};

export default function AppProviderWrapper({ children }: Readonly<{ children: React.ReactNode }>) {
  const [session, setSession] = React.useState<Session | null>(null);
  const [loading, setLoading] = React.useState(true);

  const sessionContextValue = React.useMemo(
    () => ({
      session,
      setSession,
      loading,
    }),
    [session, loading],
  );

  React.useEffect(() => {
    // Check for existing session on mount
    getCurrentSession()
      .then((currentSession: Session | null) => {
        setSession(currentSession);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <ReactRouterAppProvider 
      navigation={NAVIGATION} 
      branding={BRANDING}
      session={session}
      authentication={AUTHENTICATION}
    >
      <SessionContext.Provider value={sessionContextValue}>
        
        {children}
      </SessionContext.Provider>
    </ReactRouterAppProvider>
  );
}
