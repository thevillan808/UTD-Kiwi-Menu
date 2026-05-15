import { Row, Col, Card, Button } from 'react-bootstrap'

function PortfolioList({ portfolios, onSelect, onDelete, onCreateClick }) {
    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Your Portfolios</h5>
                <Button variant="success" size="sm" onClick={onCreateClick}>+ New Portfolio</Button>
            </div>
            {portfolios.length === 0 && (
                <p className="text-muted">No portfolios yet. Create one to get started.</p>
            )}
            <Row>
                {portfolios.map(p => (
                    <Col md={4} key={p.id} className="mb-3">
                        <Card>
                            <Card.Body>
                                <Card.Title>{p.name}</Card.Title>
                                <Card.Text className="text-muted">{p.description}</Card.Text>
                                <Button variant="danger" size="sm" className="me-2" onClick={() => onDelete(p)}>Delete</Button>
                                <Button variant="outline-success" size="sm" onClick={() => onSelect(p.id)}>View Holdings</Button>
                            </Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>
        </div>
    )
}

export default PortfolioList
