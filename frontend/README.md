# Kiwi Portfolio Manager - Frontend

React frontend for the Kiwi Portfolio Manager. Connects to the Flask backend API and authenticates users via AWS Cognito.

## Setup

### 1. Install dependencies

```
cd frontend
npm install
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your Cognito details:

```
cp .env.example .env
```

Edit `.env`:
- `VITE_COGNITO_DOMAIN` - Your Cognito hosted UI domain (e.g. https://my-pool.auth.us-east-1.amazoncognito.com)
- `VITE_COGNITO_CLIENT_ID` - The app client ID from your Cognito User Pool
- `VITE_REDIRECT_URI` - Set to http://localhost:5173/callback (must match what you registered in Cognito)
- `VITE_API_BASE_URL` - URL of the running Flask backend (e.g. http://localhost:5000)

### 3. Start the backend

From the kiwi-starter-code directory:

```
flask --app app.main run
```

### 4. Run the frontend dev server

```
npm run dev
```

Open http://localhost:5173 in your browser.

## How it works

1. Click Sign in - you are redirected to the Cognito hosted login page
2. After logging in, Cognito redirects back to /callback where the token is stored
3. You land on your portfolios list
4. Click a portfolio to view holdings, buy/sell shares, and see transaction history
5. Click Logout to clear your session and return to the login page

## Notes

- The identity token (JWT) is stored in localStorage
- Every API request includes the token as a Bearer header in Authorization
- If the token is missing or expired, the app redirects to /login
