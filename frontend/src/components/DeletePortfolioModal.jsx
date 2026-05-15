import { useState } from 'react'
import { Modal, Button, Alert, Spinner } from 'react-bootstrap'

function DeletePortfolioModal({ show, portfolio, onClose, onDelete }) {
    const [error, setError] = useState('')
    const [deleting, setDeleting] = useState(false)

    async function handleConfirm() {
        setDeleting(true)
        try {
            await onDelete()
            setError('')
        } catch (err) {
            setError(err.message)
        } finally {
            setDeleting(false)
        }
    }

    function handleClose() {
        setError('')
        onClose()
    }

    return (
        <Modal show={show} onHide={handleClose} centered>
            <Modal.Header closeButton={!deleting}>
                <Modal.Title>Delete Portfolio</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                {portfolio && (
                    <p>
                        Are you sure you want to delete <strong>{portfolio.name}</strong>? This cannot be undone.
                    </p>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose} disabled={deleting}>No</Button>
                <Button variant="danger" onClick={handleConfirm} disabled={deleting}>
                    {deleting ? <><Spinner size="sm" animation="border" className="me-2" />Deleting...</> : 'Yes, Delete'}
                </Button>
            </Modal.Footer>
        </Modal>
    )
}

export default DeletePortfolioModal
