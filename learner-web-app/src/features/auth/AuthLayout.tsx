import type {ReactNode} from 'react';
import {Box, Stack, Typography} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import TimelineIcon from '@mui/icons-material/Timeline';

interface AuthLayoutProps {
    children: ReactNode;
}

export default function AuthLayout({children}: AuthLayoutProps) {
    return (
        <Box
            sx={{
                minHeight: '100vh',
                width: '100vw',
                display: 'flex',
                bgcolor: '#050608',
                color: '#fff',
            }}
        >
            {/* LEFT: content (card/form) */}
            <Box
                sx={{
                    flexBasis: {xs: '100%', md: '40%'},
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    px: {xs: 2, md: 4},
                    py: {xs: 4, md: 0},
                }}
            >
                {children}
            </Box>

            {/* RIGHT: animated education hero */}
            <Box
                sx={{
                    flexGrow: 1,
                    display: {xs: 'none', md: 'flex'},
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'hidden',
                    background:
                        'radial-gradient(circle at top left, #1d4ed8 0, transparent 50%), radial-gradient(circle at bottom right, #06b6d4 0, transparent 55%), #050608',
                }}
            >
                {/* Subtle grid overlay */}
                <Box
                    sx={{
                        position: 'absolute',
                        inset: 0,
                        opacity: 0.08,
                        backgroundImage:
                            'linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(180deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                        backgroundSize: '40px 40px',
                    }}
                />

                <Box
                    sx={{
                        position: 'relative',
                        maxWidth: 520,
                        px: 4,
                        '@keyframes float': {
                            '0%': {transform: 'translateY(0px)'},
                            '50%': {transform: 'translateY(-12px)'},
                            '100%': {transform: 'translateY(0px)'},
                        },
                        '@keyframes floatSlow': {
                            '0%': {transform: 'translateY(0px)'},
                            '50%': {transform: 'translateY(16px)'},
                            '100%': {transform: 'translateY(0px)'},
                        },
                    }}
                >
                    <Typography
                        variant="h3"
                        sx={{fontWeight: 800, mb: 2, color: '#f9fafb'}}
                    >
                        Learn smarter,
                        <br/>
                        not harder.
                    </Typography>

                    <Typography
                        variant="body1"
                        sx={{mb: 4, color: '#e5e7eb', maxWidth: 420}}
                    >
                        Track progress, unlock new skills, and stay motivated with guided
                        learning paths tailored to you.
                    </Typography>

                    <Stack
                        direction="row"
                        spacing={3}
                        sx={{mb: 3, flexWrap: 'wrap', rowGap: 3}}
                    >
                        <Box
                            sx={{
                                flex: '1 1 160px',
                                p: 2.5,
                                borderRadius: 3,
                                bgcolor: 'rgba(15,23,42,0.9)',
                                boxShadow: '0 18px 45px rgba(15,23,42,0.7)',
                                animation: 'float 6s ease-in-out infinite',
                            }}
                        >
                            <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                                <Box
                                    sx={{
                                        width: 36,
                                        height: 36,
                                        borderRadius: '999px',
                                        bgcolor: 'rgba(59,130,246,0.25)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <SchoolIcon sx={{fontSize: 22, color: '#93c5fd'}}/>
                                </Box>
                                <Typography variant="subtitle1" fontWeight={600}>
                                    Personalised paths
                                </Typography>
                            </Box>
                            <Typography variant="body2" sx={{color: '#d1d5db'}}>
                                Curated modules based on your level and goals.
                            </Typography>
                        </Box>

                        <Box
                            sx={{
                                flex: '1 1 160px',
                                p: 2.5,
                                borderRadius: 3,
                                bgcolor: 'rgba(15,23,42,0.9)',
                                boxShadow: '0 18px 45px rgba(15,23,42,0.7)',
                                animation: 'floatSlow 8s ease-in-out infinite',
                            }}
                        >
                            <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                                <Box
                                    sx={{
                                        width: 36,
                                        height: 36,
                                        borderRadius: '999px',
                                        bgcolor: 'rgba(45,212,191,0.18)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                    }}
                                >
                                    <MenuBookIcon sx={{fontSize: 22, color: '#6ee7b7'}}/>
                                </Box>
                                <Typography variant="subtitle1" fontWeight={600}>
                                    Bite-sized lessons
                                </Typography>
                            </Box>
                            <Typography variant="body2" sx={{color: '#d1d5db'}}>
                                Short, focused activities that fit into your day.
                            </Typography>
                        </Box>
                    </Stack>

                    <Box
                        sx={{
                            mt: 1,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 1.5,
                            p: 1.8,
                            borderRadius: 999,
                            bgcolor: 'rgba(15,23,42,0.9)',
                            border: '1px solid rgba(148,163,184,0.4)',
                            animation: 'float 10s ease-in-out infinite',
                        }}
                    >
                        <Box
                            sx={{
                                width: 32,
                                height: 32,
                                borderRadius: 999,
                                bgcolor: 'rgba(56,189,248,0.3)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                            }}
                        >
                            <TimelineIcon sx={{fontSize: 20, color: '#e0f2fe'}}/>
                        </Box>
                        <Typography variant="body2" sx={{color: '#e5e7eb'}}>
                            Learners complete courses <strong>3× faster</strong> with
                            structured journeys.
                        </Typography>
                    </Box>
                </Box>
            </Box>
        </Box>
    );
}