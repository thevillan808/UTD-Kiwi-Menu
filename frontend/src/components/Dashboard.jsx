import { useState, useEffect } from 'react'
import { Container, Tabs, Tab, Spinner, Toast, ToastContainer, Navbar, Button, Nav } from 'react-bootstrap'
import { getAccessToken, getUsername, logout } from '../cognito'
import PortfolioList from './PortfolioList'
import CreatePortfolioModal from './CreatePortfolioModal'
import DeletePortfolioModal from './DeletePortfolioModal'
import HoldingsPanel from './HoldingsPanel'
import TradePanel from './TradePanel'
import TransactionLog from './TransactionLog'

const API = import.meta.env.VITE_API_BASE_URL

async function apiFetch(path, options = {}) {
    const token = getAccessToken()
    const res = await fetch(API + path, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...(options.headers || {}),
        },
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || data.error || 'Request failed')
    return data
}

function Dashboard() {
    const username = getUsername()

    const [portfolios, setPortfolios] = useState([])
    const [selectedPortfolio, setSelectedPortfolio] = useState(null)
    const [transactions, setTransactions] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('portfolios')
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [portfolioToDelete, setPortfolioToDelete] = useState(null)
    const [toast, setToast] = useState({ show: false, msg: '', variant: 'success' })

    function showToast(msg, variant = 'success') {
        setToast({ show: true, msg, variant })
    }

    function fetchPortfolios() {
        return apiFetch(`/portfolios/user/${username}`)
            .then(data => setPortfolios(data))
            .catch(e => showToast(e.message, 'danger'))
    }

    function loadPortfolioDetail(id) {
        apiFetch(`/portfolios/${id}`)
            .then(data => setSelectedPortfolio(data))
            .catch(e => showToast(e.message, 'danger'))
        apiFetch(`/portfolios/${id}/transactions`)
            .then(data => setTransactions(data))
            .catch(() => setTransactions([]))
    }

    useEffect(() => {
        fetchPortfolios().finally(() => setLoading(false))
    }, [])

    function handleSelectPortfolio(id) {
        loadPortfolioDetail(id)
        setActiveTab('holdings')
    }

    async function handleCreatePortfolio(name, description) {
        try {
            await apiFetch('/portfolios/', {
                method: 'POST',
                body: JSON.stringify({ username, name, description }),
            })
            setShowCreateModal(false)
            showToast('Portfolio created!')
            fetchPortfolios()
        } catch (e) {
            showToast(e.message, 'danger')
        }
    }

    async function handleDeletePortfolio() {
        try {
            await apiFetch(`/portfolios/${portfolioToDelete.id}`, { method: 'DELETE' })
            setPortfolioToDelete(null)
            showToast('Portfolio deleted.')
            if (selectedPortfolio?.id === portfolioToDelete.id) {
                setSelectedPortfolio(null)
                setActiveTab('portfolios')
            }
            fetchPortfolios()
        } catch (e) {
            showToast(e.message, 'danger')
        }
    }

    async function handleBuy(portfolioId, ticker, quantity) {
        try {
            await apiFetch('/trades/buy', {
                method: 'POST',
                body: JSON.stringify({ ticker, portfolio_id: portfolioId, quantity }),
            })
            showToast(`Bought ${quantity} × ${ticker}`)
            loadPortfolioDetail(portfolioId)
        } catch (e) {
            showToast(e.message, 'danger')
        }
    }

    async function handleSell(portfolioId, ticker, quantity) {
        try {
            await apiFetch('/trades/sell', {
                method: 'POST',
                body: JSON.stringify({ ticker, portfolio_id: portfolioId, quantity }),
            })
            showToast(`Sold ${quantity} × ${ticker}`)
            loadPortfolioDetail(portfolioId)
        } catch (e) {
            showToast(e.message, 'danger')
        }
    }

    return (
        <>
            <Navbar bg="dark" variant="dark" expand="lg">
                <Container>
                    <Navbar.Brand href="#">Kiwi</Navbar.Brand>
                    <Nav className="ms-auto">
                        <span className="navbar-text me-3 small">{username}</span>
                        <Button variant="outline-light" size="sm" onClick={logout}>Logout</Button>
                    </Nav>
                </Container>
            </Navbar>

            <Container className="mt-4">
                {loading ? (
                    <div className="text-center mt-5">
                        <Spinner animation="border" variant="success" />
                    </div>
                ) : (
                    <Tabs activeKey={activeTab} onSelect={k => setActiveTab(k)} className="mb-3">
                        <Tab eventKey="portfolios" title="Portfolios">
                            <PortfolioList
                                portfolios={portfolios}
                                onSelect={handleSelectPortfolio}
                                onDelete={p => setPortfolioToDelete(p)}
                                onCreateClick={() => setShowCreateModal(true)}
                            />
                        </Tab>

                        <Tab
                            eventKey="holdings"
                            title="Holdings"
                            disabled={!selectedPortfolio}
                        >
                            {selectedPortfolio && (
                                <>
                                    <h5>{selectedPortfolio.name}</h5>
                                    <p className="text-muted">{selectedPortfolio.description}</p>
                                    <HoldingsPanel investments={selectedPortfolio.investments} />
                                </>
                            )}
                        </Tab>

                        <Tab
                            eventKey="trade"
                            title="Trade"
                            disabled={!selectedPortfolio}
                        >
                            {selectedPortfolio && (
                                <TradePanel
                                    portfolioId={selectedPortfolio.id}
                                    onBuy={handleBuy}
                                    onSell={handleSell}
                                />
                            )}
                        </Tab>

                        <Tab
                            eventKey="transactions"
                            title="Transactions"
                            disabled={!selectedPortfolio}
                        >
                            <TransactionLog transactions={transactions} />
                        </Tab>
                    </Tabs>
                )}
            </Container>

            <CreatePortfolioModal
                show={showCreateModal}
                onHide={() => setShowCreateModal(false)}
                onCreate={handleCreatePortfolio}
            />

            <DeletePortfolioModal
                show={!!portfolioToDelete}
                onHide={() => setPortfolioToDelete(null)}
                portfolio={portfolioToDelete}
                onConfirm={handleDeletePortfolio}
            />

            <ToastContainer position="bottom-end" className="p-3">
                <Toast
                    show={toast.show}
                    onClose={() => setToast(t => ({ ...t, show: false }))}
                    delay={3000}
                    autohide
                    bg={toast.variant}
                >
                    <Toast.Body className="text-white">{toast.msg}</Toast.Body>
                </Toast>
            </ToastContainer>
        </>
    )
}

export default Dashboard
