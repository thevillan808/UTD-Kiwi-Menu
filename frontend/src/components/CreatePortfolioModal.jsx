import { useState } from 'react'
import { Modal, Button, Form } from 'react-bootstrap'

function CreatePortfolioModal({ show, onHide, onCreate }) {
    const [name, setName] = useState('')
    const [description, setDescription] = useState('')

    function handleSubmit(e) {
        e.preventDefault()
        onCreate(name, description)
        setName('')
        setDescription('')
    }

    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title>New Portfolio</Modal.Title>
            </Modal.Header>
            <Form onSubmit={handleSubmit}>
                <Modal.Body>
                    <Form.Group className="mb-3">
                        <Form.Label>Name</Form.Label>
                        <Form.Control
                            value={name}
                            onChange={e => setName(e.target.value)}
                            placeholder="e.g. Growth Tech"
                            required
                        />
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>Description</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            value={description}
                            onChange={e => setDescription(e.target.value)}
                            placeholder="Short description"
                            required
                        />
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={onHide}>Cancel</Button>
                    <Button variant="success" type="submit">Create</Button>
                </Modal.Footer>
            </Form>
        </Modal>
    )
}

export default CreatePortfolioModal
