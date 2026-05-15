import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { handleCallback, isLoggedIn } from './cognito'
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import 'bootstrap/dist/css/bootstrap.min.css'

function RequireAuth({ children }) {
    if (!isLoggedIn()) return <Navigate to="/login" />
    return children
}

function CallbackPage() {
    const navigate = useNavigate()
    const [err, setErr] = useState(null)

    useEffect(() => {
        const code = new URLSearchParams(window.location.search).get('code')
        if (!code) { setErr('No code in URL'); return }
        handleCallback(code)
            .then(() => navigate('/dashboard'))
            .catch(e => setErr(e.message))
    }, [])

    if (err) return <div className="text-center mt-5 text-danger">{err}</div>
    return <div className="text-center mt-5">Logging in...</div>
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/callback" element={<CallbackPage />} />
                <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
                <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
        </BrowserRouter>
    )
}
