import { login } from '../cognito'
import './LoginPage.css'

function LoginPage() {
    return (
        <div className="login-split">
            <div className="login-left">
                <div className="login-brand">🥝 kiwi</div>
                <h1>Smart portfolio management for modern investors.</h1>
                <p>Track your holdings, execute trades, and review every transaction — all in one place.</p>
                <ul className="login-features">
                    <li>Create and manage multiple portfolios</li>
                    <li>Buy and sell securities instantly</li>
                    <li>Full transaction history with filters</li>
                </ul>
            </div>
            <div className="login-right">
                <div className="login-card">
                    <div className="login-icon">🥝</div>
                    <h2>Welcome back</h2>
                    <p>Sign in to access your portfolio dashboard.</p>
                    <button className="login-btn" onClick={login}>Sign in with Kiwi</button>
                    <p className="login-hint">New here? You can create an account after clicking Sign in.</p>
                </div>
            </div>
        </div>
    )
}

export default LoginPage
