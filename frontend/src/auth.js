// Helper functions for talking to Cognito and storing the token

const COGNITO_DOMAIN = import.meta.env.VITE_COGNITO_DOMAIN
const CLIENT_ID = import.meta.env.VITE_COGNITO_CLIENT_ID
const CLIENT_SECRET = import.meta.env.VITE_COGNITO_CLIENT_SECRET
const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI

export function login() {
    const params = new URLSearchParams({
        response_type: 'code',
        client_id: CLIENT_ID,
        redirect_uri: REDIRECT_URI,
        scope: 'openid',
    })
    window.location.href = `${COGNITO_DOMAIN}/oauth2/authorize?${params}`
}

export async function handleCallback(code) {
    const params = {
        grant_type: 'authorization_code',
        client_id: CLIENT_ID,
        redirect_uri: REDIRECT_URI,
        code: code,
    }
    if (CLIENT_SECRET) params.client_secret = CLIENT_SECRET
    const body = new URLSearchParams(params)

    const res = await fetch(`${COGNITO_DOMAIN}/oauth2/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
    })

    if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(`Token exchange failed: ${err.error || res.status} - ${err.error_description || ''}`)
    }

    const data = await res.json()
    localStorage.setItem('id_token', data.id_token)
}

export function getToken() {
    return localStorage.getItem('id_token')
}

// decode the JWT payload to get the username
export function getUsername() {
    const token = getToken()
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload['cognito:username'] || payload.sub
}

export function isLoggedIn() {
    const token = getToken()
    if (!token) return false
    try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.exp * 1000 > Date.now()
    } catch {
        return false
    }
}

export function logout() {
    localStorage.removeItem('id_token')
    const params = new URLSearchParams({
        client_id: CLIENT_ID,
        logout_uri: window.location.origin,
    })
    window.location.href = `${COGNITO_DOMAIN}/logout?${params}`
}
