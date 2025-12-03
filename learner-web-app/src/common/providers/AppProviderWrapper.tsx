import * as React from 'react';
import { ReactRouterAppProvider } from "@toolpad/core/react-router";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { Authentication } from '@toolpad/core';
import { useLocation } from 'react-router';
import SessionContext, { type Session } from '../../contexts/SessionContext';
import { ChatProvider } from '../../contexts/ChatContext';
import { signOut, getCurrentSession } from '../../features/auth/authService';
import { NAVIGATION } from '../constant/navigation';
import { LearningPathContextProvider } from '../../contexts/LearningPathContextProvider';
import appTheme from '../../theme/appTheme';

// List of non-authenticated endpoints
const NON_AUTH_ROUTES = ['/sign-in', '/sign-up'];

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      retry: 1,
    },
  },
});

const BRANDING = {
  logo: <img src="/logo-filled.png" alt="MUI logo" />,
  title: 'Learnora'
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

function isAuthRoute(pathname: string): boolean {
  return !NON_AUTH_ROUTES.some(route => pathname.startsWith(route));
}

function AuthenticatedProvidersWrapper({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isAuthRoute_ = isAuthRoute(location.pathname);

  if (isAuthRoute_) {
    return (
      <LearningPathContextProvider>
        <ChatProvider>
          {children}
        </ChatProvider>
      </LearningPathContextProvider>
    );
  }

  return <>{children}</>;
}

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
    <QueryClientProvider client={queryClient}>
      <ReactRouterAppProvider
        navigation={NAVIGATION}
        branding={BRANDING}
        session={session}
        authentication={AUTHENTICATION}
        theme={appTheme}
      >
        <SessionContext.Provider value={sessionContextValue}>
          <AuthenticatedProvidersWrapper>
            {children}
          </AuthenticatedProvidersWrapper>
        </SessionContext.Provider>
      </ReactRouterAppProvider>
    </QueryClientProvider>
  );
}
