import * as React from 'react';

export interface Session {
  user: {
    id: string; // Changed from number to string to match MUI's Session type
    email: string;
    name?: string;
    image?: string;
    first_name?: string;
    last_name?: string;
    is_active: boolean;
    is_superuser: boolean;
    is_verified: boolean;
  };
  access_token: string;
}

interface SessionContextType {
  session: Session | null;
  setSession: (session: Session | null) => void;
  loading: boolean;
}

const SessionContext = React.createContext<SessionContextType>({
  session: null,
  setSession: () => {},
  loading: true,
});

export default SessionContext;
