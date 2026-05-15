import { useState } from 'react'
import { Row, Col, Card, Form, Button } from 'react-bootstrap'

function TradePanel({ portfolioId, onBuy, onSell }) {
    const [buyTicker, setBuyTicker] = useState('')
    const [buyQty, setBuyQty] = useState('')
    const [sellTicker, setSellTicker] = useState('')
    const [sellQty, setSellQty] = useState('')

    function handleBuy(e) {
        e.preventDefault()
        onBuy(portfolioId, buyTicker.toUpperCase(), Number(buyQty))
        setBuyTicker('')
        setBuyQty('')
    }

    function handleSell(e) {
        e.preventDefault()
        onSell(portfolioId, sellTicker.toUpperCase(), Number(sellQty))
        setSellTicker('')
        setSellQty('')
    }

    return (
        <Row>
            <Col md={6}>
                <Card>
                    <Card.Header className="bg-success text-white">Buy</Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleBuy}>
                            <Form.Group className="mb-2">
                                <Form.Label>Ticker</Form.Label>
                                <Form.Control
                                    placeholder="AAPL"
                                    value={buyTicker}
                                    onChange={e => setBuyTicker(e.target.value)}
                                    required
                                />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Quantity</Form.Label>
                                <Form.Control
                                    type="number"
                                    min="1"
                                    value={buyQty}
                                    onChange={e => setBuyQty(e.target.value)}
                                    required
                                />
                            </Form.Group>
                            <Button variant="success" type="submit" className="w-100">Buy</Button>
                        </Form>
                    </Card.Body>
                </Card>
            </Col>
            <Col md={6}>
                <Card>
                    <Card.Header className="bg-danger text-white">Sell</Card.Header>
                    <Card.Body>
                        <Form onSubmit={handleSell}>
                            <Form.Group className="mb-2">
                                <Form.Label>Ticker</Form.Label>
                                <Form.Control
                                    placeholder="AAPL"
                                    value={sellTicker}
                                    onChange={e => setSellTicker(e.target.value)}
                                    required
                                />
                            </Form.Group>
                            <Form.Group className="mb-3">
                                <Form.Label>Quantity</Form.Label>
                                <Form.Control
                                    type="number"
                                    min="1"
                                    value={sellQty}
                                    onChange={e => setSellQty(e.target.value)}
                                    required
                                />
                            </Form.Group>
                            <Button variant="danger" type="submit" className="w-100">Sell</Button>
                        </Form>
                    </Card.Body>
                </Card>
            </Col>
        </Row>
    )
}

export default TradePanel
