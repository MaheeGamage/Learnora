import React, { useState } from "react";

import LockOutlinedIcon from "@mui/icons-material/LockOutlined";

import {
    Avatar,
    Box,
    Button,
    Container,
    Paper,
    TextField,
    Typography,
} from "@mui/material";

const LoginPage: React.FC = () => {
    const [email, setEmail] = useState<string>("");
    const [password, setPassword] = useState<string>("");
    const [error, setError] = useState<string>("");

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!email.trim() || !password) {
            setError("Email and password are required.");
            return;
        }
        setError("");
        // Replace with real auth logic
        console.log("Login attempt:", { email, password });
    };

    return (
        <Container maxWidth="xs">
            <Paper elevation={3} sx={{ mt: 10, p: 4 }}>
                <Box
                    display="flex"
                    flexDirection="column"
                    alignItems="center"
                    gap={2}
                >
                    <Avatar sx={{ bgcolor: "primary.main" }}>
                        <LockOutlinedIcon />
                    </Avatar>
                    <Typography component="h1" variant="h5">
                        Sign in
                    </Typography>

                    <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
                        <TextField
                            label="Email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            margin="normal"
                            fullWidth
                            autoComplete="email"
                        />
                        <TextField
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            margin="normal"
                            fullWidth
                            autoComplete="current-password"
                        />

                        {error && (
                            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
                                {error}
                            </Typography>
                        )}

                        <Button
                            type="submit"
                            fullWidth
                            variant="contained"
                            sx={{ mt: 3 }}
                        >
                            Sign In
                        </Button>
                    </Box>
                </Box>
            </Paper>
        </Container>
    );
};

export default LoginPage;