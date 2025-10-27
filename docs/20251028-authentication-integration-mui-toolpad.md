# 20251028 - Authentication Integration with MUI Toolpad Core

**Date**: October 28, 2025  
**Feature**: Authentication system integration  
**Framework**: MUI Toolpad Core + React Router + FastAPI (fastapi-users)  
**Status**: ✅ Implemented and Tested

---

## Table of Contents

1. [Overview](#overview)
2. [What Was Implemented](#what-was-implemented)
3. [Architecture](#architecture)
4. [Files Created](#files-created)
5. [Files Modified](#files-modified)
6. [Features](#features)
7. [How It Works](#how-it-works)
8. [Testing Guide](#testing-guide)
9. [API Integration](#api-integration)
10. [Usage Examples](#usage-examples)
11. [Troubleshooting](#troubleshooting)
12. [Next Steps](#next-steps)

---

## Overview

Successfully integrated MUI Toolpad Core authentication with the existing FastAPI backend (using fastapi-users library) following the official MUI documentation. The implementation provides a complete authentication flow with JWT tokens, protected routes, and session management.

### Key Benefits

- ✅ Seamless integration with existing FastAPI backend
- ✅ MUI Toolpad Core's built-in SignInPage component
- ✅ JWT token-based authentication
- ✅ Protected route management
- ✅ Session persistence across page refreshes
- ✅ Automatic token validation
- ✅ Type-safe implementation

---

## What Was Implemented

### Frontend Components (React + TypeScript)

1. **Session Management** - Context-based state management for user sessions
2. **Authentication Service** - API integration layer for auth operations
3. **Sign-in Page** - MUI Toolpad's SignInPage component
4. **Route Protection** - Middleware to protect dashboard routes
5. **Environment Configuration** - API URL configuration

### Backend Integration

- Connected to existing FastAPI endpoints:
  - `/auth/jwt/login` - User login
  - `/auth/jwt/logout` - User logout
  - `/users/me` - Get current user info

### Configuration

- Environment variables for API endpoint
- CORS already configured in backend
- Token storage in localStorage

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                         root.tsx                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         ReactRouterAppProvider                        │  │
│  │  - Navigation config                                  │  │
│  │  - Authentication config                              │  │
│  │  - Session state                                      │  │
│  │                                                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │      SessionContext.Provider                    │  │  │
│  │  │   - session: Session | null                     │  │  │
│  │  │   - loading: boolean                            │  │  │
│  │  │   - setSession: (session) => void               │  │  │
│  │  │                                                  │  │  │
│  │  │  ┌────────────────────────────────────────────┐ │  │  │
│  │  │  │         Routes (Outlet)                    │ │  │  │
│  │  │  │                                            │ │  │  │
│  │  │  │  Protected Routes:                         │ │  │  │
│  │  │  │  ┌──────────────────────────────────────┐  │ │  │  │
│  │  │  │  │  Dashboard Layout                    │  │ │  │  │
│  │  │  │  │  - Checks session                    │  │ │  │  │
│  │  │  │  │  - Redirects if not authenticated    │  │ │  │  │
│  │  │  │  │  ┌────────────────────────────────┐  │  │ │  │  │
│  │  │  │  │  │  / - Home Page                 │  │  │ │  │  │
│  │  │  │  │  │  /orders - Orders Page         │  │  │ │  │  │
│  │  │  │  │  └────────────────────────────────┘  │  │ │  │  │
│  │  │  │  └──────────────────────────────────────┘  │ │  │  │
│  │  │  │                                            │ │  │  │
│  │  │  │  Public Routes:                            │ │  │  │
│  │  │  │  - /sign-in (SignInPage component)         │ │  │  │
│  │  │  └────────────────────────────────────────────┘ │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────────────┐
│ User visits  │
│ protected    │
│ route (/)    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Dashboard Layout │
│ checks session   │
└──────┬───────────┘
       │
       ├──── session exists ────┐
       │                        │
       │                        ▼
       │                  ┌─────────────┐
       │                  │ Show page   │
       │                  └─────────────┘
       │
       └──── no session ───┐
                          │
                          ▼
              ┌─────────────────────────┐
              │ Redirect to /sign-in    │
              │ ?callbackUrl=/          │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ User enters credentials │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ POST /auth/jwt/login    │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ Store JWT token         │
              │ in localStorage         │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ GET /users/me           │
              │ (fetch user data)       │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ Set session in context  │
              └──────────┬──────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ Redirect to callbackUrl │
              │ (original page)         │
              └─────────────────────────┘
```

### Data Flow

```
localStorage          SessionContext          API Service          FastAPI Backend
─────────────────    ──────────────────    ─────────────────    ──────────────────
                                                                
[access_token] ──────▶ getCurrentSession()                      
                           │                                     
                           ├──────────────▶ GET /users/me ─────▶ Validate token
                           │                                     Return user data
                           ◀───────────────                      
                      Set session state                          
                                                                
                      User signs in                              
                           │                                     
                           ├──────────────▶ POST /auth/jwt/login ▶ Validate credentials
                           │                                     Return JWT token
                           ◀───────────────                      
                      Store token ──────────▶                    
[access_token]        Set session state                          
                                                                
                      User signs out                             
                           │                                     
                           ├──────────────▶ POST /auth/jwt/logout ▶ Invalidate token
                           ◀───────────────                      
Clear token ◀─────────                                           
                      Clear session state
```

---

## Files Created

### 1. Session Context (`src/contexts/SessionContext.tsx`)

**Purpose**: Defines the Session interface and provides context for session state management.

**Key Types**:
```typescript
interface Session {
  user: {
    id: string;
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
```

### 2. useSession Hook (`src/hooks/useSession.ts`)

**Purpose**: Custom hook to access session data from any component.

**Usage**:
```typescript
import { useSession } from '../hooks/useSession';

function MyComponent() {
  const { session, loading } = useSession();
  
  if (loading) return <div>Loading...</div>;
  if (!session) return <div>Not authenticated</div>;
  
  return <div>Hello, {session.user.name}!</div>;
}
```

### 3. Authentication Service (`src/services/auth.ts`)

**Purpose**: Handles all API communication for authentication operations.

**Functions**:
- `signInWithCredentials(email, password)` - Login user
- `registerUser(email, password, firstName, lastName)` - Register new user
- `signOut()` - Logout user
- `getCurrentSession()` - Retrieve existing session from localStorage

**Example**:
```typescript
import { signInWithCredentials } from '../services/auth';

const result = await signInWithCredentials('user@example.com', 'password');
if (result.success) {
  setSession(result.session);
} else {
  console.error(result.error);
}
```

### 4. Sign-in Page (`src/pages/sign-in.tsx`)

**Purpose**: Login page using MUI Toolpad's SignInPage component.

**Features**:
- Email/password form
- Error handling
- Loading states
- Automatic redirect after login
- Callback URL support

### 5. Environment Files

**`.env`** and **`.env.example`**:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Files Modified

### 1. Root Component (`src/root.tsx`)

**Changes**:
- Added SessionContext provider
- Added authentication configuration to ReactRouterAppProvider
- Implemented session initialization on app load
- Added session state management

**Key Additions**:
```typescript
const AUTHENTICATION: Authentication = {
  signIn: () => {
    // Handled by SignInPage component
  },
  signOut: () => {
    signOut();
  },
};

// Session state management
const [session, setSession] = React.useState<Session | null>(null);
const [loading, setLoading] = React.useState(true);

// Check for existing session on mount
React.useEffect(() => {
  getCurrentSession()
    .then((currentSession) => {
      setSession(currentSession);
    })
    .finally(() => {
      setLoading(false);
    });
}, []);
```

### 2. Dashboard Layout (`src/common/layouts/dashboard.tsx`)

**Changes**:
- Added session checking logic
- Added loading state
- Added redirect to sign-in for unauthenticated users
- Added callback URL parameter

**Key Additions**:
```typescript
const { session, loading } = useSession();
const location = useLocation();

if (loading) {
  return <LinearProgress />;
}

if (!session) {
  const redirectTo = `/sign-in?callbackUrl=${encodeURIComponent(location.pathname)}`;
  return <Navigate to={redirectTo} replace />;
}
```

### 3. Routes Configuration (`src/routes.ts`)

**Changes**:
- Added `/sign-in` route
- Removed temporary development route

---

## Features

### ✅ Email/Password Authentication

Users can sign in with email and password credentials that are validated against the FastAPI backend.

### ✅ JWT Token Management

- Tokens are stored in localStorage
- Automatically included in API requests
- Validated on app load
- Cleared on sign out

### ✅ Protected Routes

All routes under the dashboard layout are automatically protected:
- Unauthenticated users are redirected to sign-in
- Callback URL preserves intended destination
- After login, users return to original page

### ✅ Session Persistence

- Session survives page refresh
- Token automatically validated on app load
- Invalid tokens trigger re-authentication

### ✅ User Profile Display

- User information shown in dashboard header
- User menu with sign out option
- MUI Toolpad's built-in account menu

### ✅ Loading States

- Loading indicator during authentication check
- Prevents flash of wrong content
- Smooth user experience

### ✅ Error Handling

- Clear error messages for failed login
- Network error handling
- Invalid token handling

---

## How It Works

### Initial App Load

1. App starts, `loading = true`
2. `getCurrentSession()` checks for token in localStorage
3. If token exists, validates with `GET /users/me`
4. If valid, sets session and `loading = false`
5. If invalid or missing, clears token and `loading = false`

### User Sign In

1. User navigates to protected route
2. Dashboard layout checks session
3. No session → redirect to `/sign-in?callbackUrl=/`
4. User enters credentials
5. `signInWithCredentials()` calls `POST /auth/jwt/login`
6. Store token in localStorage
7. Fetch user data with `GET /users/me`
8. Create session object and set in context
9. Redirect to callbackUrl

### User Sign Out

1. User clicks sign out in menu
2. `signOut()` calls `POST /auth/jwt/logout`
3. Clear token from localStorage
4. Clear session from context
5. User redirected to sign-in page

### Protected Route Access

1. User navigates to protected route
2. Dashboard layout renders
3. Checks `useSession()` hook
4. If `loading = true`, show loading indicator
5. If `session = null`, redirect to sign-in
6. If session exists, render page

---

## Testing Guide

### Prerequisites

- ✅ Backend running at http://localhost:8000
- ✅ Frontend running at http://localhost:5173

### Step 1: Create Test User

#### Option A: Using FastAPI Swagger UI

1. Open http://localhost:8000/docs
2. Find `POST /auth/register`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "test@example.com",
     "password": "Test1234!",
     "first_name": "Test",
     "last_name": "User"
   }
   ```
5. Click "Execute"

#### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234!\",\"first_name\":\"Test\",\"last_name\":\"User\"}"
```

### Step 2: Test Login

1. Open http://localhost:5173
2. Should redirect to http://localhost:5173/sign-in
3. Enter credentials:
   - Email: test@example.com
   - Password: Test1234!
4. Click "Sign in"

### Step 3: Verify Authentication

After login, verify:

- ✅ Redirected to dashboard (/)
- ✅ "Test User" appears in top-right
- ✅ Can navigate to /orders
- ✅ User menu icon visible
- ✅ "Sign out" option in menu

### Step 4: Test Session Persistence

1. While logged in, refresh page (F5)
2. Should remain logged in
3. Check DevTools → Application → Local Storage
4. Should see `access_token`

### Step 5: Test Protected Routes

1. Click "Sign out"
2. Try accessing http://localhost:5173/
3. Should redirect to sign-in with callbackUrl
4. After signing in, return to /

### Step 6: Test Sign-in Page Redirect

1. While logged in, go to http://localhost:5173/sign-in
2. Should redirect to / (already authenticated)

### Common Test Scenarios

#### Test Case 1: Invalid Credentials
- Enter wrong password
- Should see: "Invalid email or password"

#### Test Case 2: Empty Fields
- Leave fields empty
- Should see validation error

#### Test Case 3: Backend Down
- Stop backend server
- Try to sign in
- Should see network error

#### Test Case 4: Token Expiration
- Edit `access_token` in localStorage to invalid value
- Refresh page
- Should redirect to sign-in

### Debugging Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can create user via API
- [ ] Can sign in with correct credentials
- [ ] Error shown for wrong credentials
- [ ] Redirected to dashboard after login
- [ ] User info appears in header
- [ ] Session persists after refresh
- [ ] Can sign out
- [ ] Protected routes redirect when logged out
- [ ] Callback URL works correctly
- [ ] Already logged-in redirects from sign-in

---

## API Integration

### Endpoints Used

#### Login
```
POST /auth/jwt/login
Content-Type: application/x-www-form-urlencoded
Body: username=email&password=password

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```
GET /users/me
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

#### Logout
```
POST /auth/jwt/logout
Authorization: Bearer <token>

Response: 200 OK
```

### Error Responses

```json
// Invalid credentials
{
  "detail": "LOGIN_BAD_CREDENTIALS"
}

// Invalid token
{
  "detail": "Invalid token"
}

// User not found
{
  "detail": "User not found"
}
```

---

## Usage Examples

### Accessing User Data in Components

```typescript
import { useSession } from '../hooks/useSession';

export default function ProfilePage() {
  const { session, loading } = useSession();

  if (loading) {
    return <LinearProgress />;
  }

  if (!session) {
    return <Navigate to="/sign-in" />;
  }

  return (
    <div>
      <h1>Profile</h1>
      <p>Email: {session.user.email}</p>
      <p>Name: {session.user.name}</p>
      <p>ID: {session.user.id}</p>
    </div>
  );
}
```

### Making Authenticated API Calls

```typescript
import { useSession } from '../hooks/useSession';

export default function DataPage() {
  const { session } = useSession();
  const [data, setData] = useState(null);

  useEffect(() => {
    if (session) {
      fetch('http://localhost:8000/api/v1/my-data', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      })
        .then(res => res.json())
        .then(setData);
    }
  }, [session]);

  return <div>{/* Render data */}</div>;
}
```

### Conditional Rendering Based on Auth

```typescript
import { useSession } from '../hooks/useSession';

export default function HomePage() {
  const { session } = useSession();

  return (
    <div>
      <h1>Welcome</h1>
      {session ? (
        <p>Hello, {session.user.name}!</p>
      ) : (
        <Link to="/sign-in">Sign in</Link>
      )}
    </div>
  );
}
```

### Creating New Protected Routes

1. Add route in `src/routes.ts` under dashboard layout:
```typescript
layout("./common/layouts/dashboard.tsx", [
  route("/", "./pages/home.tsx"),
  route("/orders", "./pages/orders.tsx"),
  route("/profile", "./pages/profile.tsx"), // New protected route
]),
```

2. Create the page component:
```typescript
// src/pages/profile.tsx
import { useSession } from '../hooks/useSession';

export default function ProfilePage() {
  const { session } = useSession();
  
  return (
    <div>
      <h1>Profile</h1>
      <p>{session?.user.email}</p>
    </div>
  );
}
```

That's it! The dashboard layout automatically protects it.

---

## Troubleshooting

### Issue: Login Doesn't Work

**Symptoms**: Form submits but nothing happens, or error message appears.

**Check**:
1. Backend is running: http://localhost:8000/health
2. `.env` file has correct `VITE_API_BASE_URL=http://localhost:8000`
3. Browser console for errors (F12)
4. Network tab for failed requests
5. User exists in database

**Solutions**:
- Restart backend server
- Verify user credentials
- Check CORS configuration
- Clear browser cache and localStorage

### Issue: Session Lost After Refresh

**Symptoms**: User is logged in, refreshes page, gets logged out.

**Check**:
1. Browser localStorage enabled
2. Token is stored (DevTools → Application → Local Storage)
3. Token format is correct (starts with `eyJ`)
4. Backend `/users/me` endpoint is accessible

**Solutions**:
- Check browser privacy settings
- Verify token isn't expired
- Check backend logs for validation errors

### Issue: CORS Errors

**Symptoms**: Console shows CORS-related errors.

**Check**:
1. Backend CORS configuration in `core-service/app/config.py`
2. Frontend URL in `CORS_ORIGINS` list
3. Backend is running

**Solutions**:
- Add frontend URL to CORS_ORIGINS:
  ```python
  CORS_ORIGINS: list[str] = ["http://localhost:5173"]
  ```
- Restart backend after config changes

### Issue: Protected Routes Not Working

**Symptoms**: Can access protected routes without logging in.

**Check**:
1. Routes are under dashboard layout in `routes.ts`
2. Dashboard layout has session checking logic
3. SessionContext provider wraps the app

**Solutions**:
- Verify route structure in `routes.ts`
- Check dashboard layout implementation
- Ensure root.tsx has SessionContext.Provider

### Issue: Sign Out Doesn't Work

**Symptoms**: Click sign out but remain logged in.

**Check**:
1. signOut function is called
2. localStorage is cleared
3. Session is set to null in context
4. Backend logout endpoint responds

**Solutions**:
- Check browser console for errors
- Manually clear localStorage
- Verify signOut function implementation

### Debug Tools

#### Check Backend Health
```bash
curl http://localhost:8000/health
```

#### Check If User Exists
```bash
# Login to get token
curl -X POST "http://localhost:8000/auth/jwt/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test1234!"

# Use token to check user
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/users/me
```

#### Check localStorage
```javascript
// In browser console
console.log(localStorage.getItem('access_token'));
```

#### Clear All Auth Data
```javascript
// In browser console
localStorage.clear();
location.reload();
```

---

## Next Steps

### Immediate Enhancements

1. **Registration UI**
   - Create sign-up page
   - Use fastapi-users registration endpoint
   - Add form validation

2. **Password Reset Flow**
   - Implement forgot password page
   - Use fastapi-users reset password endpoints
   - Add email verification

3. **User Profile Management**
   - Create profile page
   - Allow users to update their info
   - Use `PATCH /users/me` endpoint

### Short-term Improvements

4. **Token Refresh**
   - Implement automatic token refresh
   - Handle token expiration gracefully
   - Add refresh token support

5. **Remember Me**
   - Add "Remember me" checkbox
   - Use different storage for persistent login
   - Adjust token expiration

6. **Loading States**
   - Add skeleton screens
   - Improve loading indicators
   - Add progress feedback

### Medium-term Features

7. **Social Login**
   - Add Google OAuth
   - Add GitHub OAuth
   - Configure on backend

8. **Email Verification**
   - Implement email verification flow
   - Use fastapi-users verify endpoints
   - Add resend verification email

9. **Two-Factor Authentication**
   - Add 2FA setup page
   - Implement TOTP
   - Add backup codes

### Long-term Security

10. **Enhanced Security**
    - Move to httpOnly cookies
    - Implement CSRF protection
    - Add rate limiting

11. **Session Management**
    - Add "Active Sessions" page
    - Allow revoking sessions
    - Track login history

12. **Audit Logging**
    - Log authentication events
    - Track failed login attempts
    - Add security alerts

---

## Configuration Reference

### Environment Variables

**Frontend** (`.env`):
```env
# Required
VITE_API_BASE_URL=http://localhost:8000

# Optional (for future features)
VITE_ENABLE_SOCIAL_LOGIN=false
VITE_GOOGLE_CLIENT_ID=
VITE_GITHUB_CLIENT_ID=
```

**Backend** (`core-service/.env`):
```env
# Database
DATABASE_URL=sqlite:///./learnora.db

# Security
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

### TypeScript Interfaces

```typescript
// Session
interface Session {
  user: {
    id: string;
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

// Auth Result
interface AuthResult {
  success: boolean;
  session?: Session;
  error?: string;
}

// API Responses
interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
}
```

---

## Security Considerations

### Current Implementation

1. **Token Storage**: localStorage (convenient but less secure)
2. **CORS**: Properly configured for development
3. **HTTPS**: Not enforced (development only)
4. **Token Expiration**: Managed by backend
5. **Input Validation**: Both frontend and backend

### Production Recommendations

1. **Use httpOnly Cookies**
   ```typescript
   // Instead of localStorage
   // Backend sets cookie with httpOnly flag
   credentials: 'include'
   ```

2. **Enforce HTTPS**
   ```python
   # Backend
   secure_cookies=True
   ```

3. **Implement Token Refresh**
   ```typescript
   // Auto-refresh before expiration
   refreshTokenBeforeExpiry();
   ```

4. **Add CSRF Protection**
   ```python
   # Backend
   csrf_protect = CSRFProtect(app)
   ```

5. **Rate Limiting**
   ```python
   # Backend
   limiter = Limiter(app)
   ```

---

## Resources

### Documentation
- [MUI Toolpad Core - React Router Integration](https://mui.com/toolpad/core/integrations/react-router/)
- [FastAPI-Users Documentation](https://fastapi-users.github.io/fastapi-users/)
- [React Router Documentation](https://reactrouter.com/)

### Code Examples
- [MUI Toolpad Examples](https://github.com/mui/toolpad/tree/master/examples/core/)
- [FastAPI-Users Examples](https://github.com/fastapi-users/fastapi-users/tree/master/examples)

### Related Files
- Frontend: `learner-web-app/src/`
- Backend: `core-service/app/features/users/`
- Config: `core-service/app/config.py`

---

## Changelog

### 2025-10-28 - Initial Implementation
- ✅ Created session management context
- ✅ Implemented authentication service
- ✅ Added sign-in page with MUI Toolpad
- ✅ Protected dashboard routes
- ✅ Integrated with FastAPI backend
- ✅ Added session persistence
- ✅ Tested and verified working

---

**Status**: ✅ Complete and Production-Ready (with noted security enhancements for production use)

**Last Updated**: October 28, 2025  
**Maintained By**: Development Team  
**For Questions**: Refer to this document or check the code comments
