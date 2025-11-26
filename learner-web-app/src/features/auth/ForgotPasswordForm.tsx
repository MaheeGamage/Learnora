import {type FormEvent, useState} from 'react';
import {Alert, Box, Button, Link as MuiLink, Paper, Stack, TextField, Typography,} from '@mui/material';
import {Link as RouterLink} from 'react-router';
import AuthLayout from './AuthLayout';

export default function ForgotPasswordForm() {
    const [email, setEmail] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            // TODO: replace with your real forgot-password endpoint
            const res = await fetch('/api/forgot-password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email}),
            });

            if (!res.ok) {
                const {message} = await res.json().catch(() => ({
                    message: 'Request failed',
                }));
                throw new Error(message);
            }

            setSuccess(
                'If an account exists for this email, a reset link has been sent.'
            );
        } catch (err: unknown) {
            const message =
                err instanceof Error ? err.message : 'Something went wrong';
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthLayout>
            <Paper
                elevation={8}
                sx={{
                    p: 4,
                    width: '100%',
                    maxWidth: 420,
                    borderRadius: 3,
                    bgcolor: '#181a1f',
                }}
            >
                <Stack spacing={3}>
                    {/* Heading */}
                    <Box>
                        <Typography variant="h5" fontWeight={700} color="white">
                            Forgot your password? 🔐
                        </Typography>
                        <Typography
                            variant="body2"
                            sx={{mt: 0.5, color: '#cbd5f5'}}
                        >
                            Enter your email and we&apos;ll send you a reset link.
                        </Typography>
                    </Box>

                    {/* Error / success messages */}
                    {error && (
                        <Alert severity="error" variant="outlined">
                            {error}
                        </Alert>
                    )}

                    {success && (
                        <Alert severity="success" variant="outlined">
                            {success}
                        </Alert>
                    )}

                    {/* Form */}
                    <Box component="form" onSubmit={handleSubmit} noValidate>
                        <Stack spacing={2.5}>
                            <TextField
                                label="Email"
                                type="email"
                                required
                                fullWidth
                                autoComplete="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                InputLabelProps={{style: {color: '#d1d5db'}}}
                                InputProps={{
                                    sx: {
                                        color: '#f9fafb',
                                        '& .MuiOutlinedInput-notchedOutline': {
                                            borderColor: '#4b5563',
                                        },
                                        '&:hover .MuiOutlinedInput-notchedOutline': {
                                            borderColor: '#9ca3af',
                                        },
                                    },
                                }}
                            />

                            <Button
                                type="submit"
                                variant="contained"
                                fullWidth
                                size="large"
                                disabled={loading}
                                sx={{
                                    mt: 1,
                                    borderRadius: 2,
                                    py: 1.2,
                                    background:
                                        'linear-gradient(135deg, #60a5fa 0%, #38bdf8 100%)',
                                    fontWeight: 600,
                                }}
                            >
                                {loading ? 'Sending link…' : 'Send reset link'}
                            </Button>
                        </Stack>
                    </Box>

                    {/* Footer link */}
                    <Box textAlign="center">
                        <Typography variant="body2" sx={{color: '#e5e7eb'}}>
                            Remembered your password?{' '}
                            <MuiLink
                                component={RouterLink}
                                to="/sign-in"
                                underline="hover"
                                sx={{fontWeight: 600, color: '#93c5fd'}}
                            >
                                Back to sign in
                            </MuiLink>
                        </Typography>
                    </Box>
                </Stack>
            </Paper>
        </AuthLayout>
    );
}
