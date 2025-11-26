import { SignInPage, type AuthProvider, type AuthResponse } from '@toolpad/core/SignInPage';
import { useNavigate, useSearchParams } from 'react-router';
import { useSession } from '../../common/hooks/useSession';
import { signInWithCredentials } from './authService';

export default function SignInForm() {
  const { setSession } = useSession();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/';

  const providers: AuthProvider[] = [
    { id: 'credentials', name: 'Email and Password' },
  ];

  const signIn = async (
    provider: AuthProvider,
    formData: FormData
  ): Promise<AuthResponse> => {
    try {
      if (provider.id === 'credentials') {
        const email = formData.get('email') as string;
        const password = formData.get('password') as string;

        if (!email || !password) {
          return { 
            error: 'Email and password are required',
            type: 'CredentialsSignin'
          };
        }

        const result = await signInWithCredentials(email, password);

        if (result.success && result.session) {
          setSession(result.session);
          navigate(callbackUrl, { replace: true });
          return {};
        }

        return { 
          error: result.error || 'Failed to sign in',
          type: 'CredentialsSignin'
        };
      }

      return { 
        error: 'Invalid provider',
        type: 'CredentialsSignin'
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'An error occurred',
        type: 'CredentialsSignin'
      };
    }
  };

  return (
    <SignInPage
      providers={providers}
      signIn={signIn}
    />
  );
}
