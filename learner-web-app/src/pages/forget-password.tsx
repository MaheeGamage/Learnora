import LinearProgress from '@mui/material/LinearProgress';
import {Navigate, useSearchParams} from 'react-router';
import {useSession} from '../common/hooks/useSession';
import ForgotPasswordForm from "../features/auth/ForgotPasswordForm";

export default function ForgetPassword() {
    const {session, loading} = useSession();
    const [searchParams] = useSearchParams();
    const callbackUrl = searchParams.get('callbackUrl') || '/';

    if (loading) {
        return (
            <div style={{width: '100%', marginTop: '20px'}}>
                <LinearProgress/>
            </div>
        );
    }

    if (session) {
        return <Navigate to={callbackUrl}/>;
    }

    return <ForgotPasswordForm/>;
}
