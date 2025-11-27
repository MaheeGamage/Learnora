import { type FormEvent, useState } from 'react';
import { Alert, Box, Button, Link as MuiLink, Paper, Stack, TextField, Typography, } from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router';
import AuthLayout from './AuthLayout';
import { registerUser } from './authService';

export default function SignupForm() {
    const [firstName, setFirstName] = useState<string>('');
    const [lastName, setLastName] = useState<string>('');
    const [email, setEmail] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [confirmPassword, setConfirmPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const [success, setSuccess] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            const result = await registerUser(email, password, firstName, lastName);
            if (!result.success) {
                throw new Error(result.error || 'Registration failed');
            }
            else {
                // redirect user to sign-in page after successful registration using react-router
                navigate('/sign-in');
            }

            setSuccess('Account created successfully. You can now sign in.');
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
                    <Box>
                        <Typography variant="h5" fontWeight={700} color="white">
                            Create your account ✨
                        </Typography>
                        <Typography
                            variant="body2"
                            sx={{ mt: 0.5, color: '#cbd5f5' }}
                        >
                            Join the learning journey in a few steps.
                        </Typography>
                    </Box>

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

                    <Box component="form" onSubmit={handleSubmit} noValidate>
                        <Stack spacing={2.5}>
                            <TextField
                                label="First Name"
                                required
                                fullWidth
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                InputLabelProps={{ style: { color: '#d1d5db' } }}
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

                            <TextField
                                label="Last Name"
                                required
                                fullWidth
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                InputLabelProps={{ style: { color: '#d1d5db' } }}
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

                            <TextField
                                label="Email"
                                type="email"
                                required
                                fullWidth
                                autoComplete="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                InputLabelProps={{ style: { color: '#d1d5db' } }}
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

                            <TextField
                                label="Password"
                                type="password"
                                required
                                fullWidth
                                autoComplete="new-password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                InputLabelProps={{ style: { color: '#d1d5db' } }}
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

                            <TextField
                                label="Confirm Password"
                                type="password"
                                required
                                fullWidth
                                autoComplete="new-password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                InputLabelProps={{ style: { color: '#d1d5db' } }}
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
                                {loading ? 'Creating account…' : 'Create account'}
                            </Button>
                        </Stack>
                    </Box>

                    <Box textAlign="center">
                        <Typography variant="body2" sx={{ color: '#e5e7eb' }}>
                            Already have an account?{' '}
                            <MuiLink
                                component={RouterLink}
                                to="/sign-in"
                                underline="hover"
                                sx={{ fontWeight: 600, color: '#93c5fd' }}
                            >
                                Sign in
                            </MuiLink>
                        </Typography>
                    </Box>
                </Stack>
            </Paper>
        </AuthLayout>
    );
}