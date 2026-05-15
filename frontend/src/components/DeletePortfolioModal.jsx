import { Modal, Button } from 'react-bootstrap'

function DeletePortfolioModal({ show, onHide, portfolio, onConfirm }) {
    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title>Delete Portfolio</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                Are you sure you want to delete <strong>{portfolio?.name}</strong>? This cannot be undone.
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>Cancel</Button>
                <Button variant="danger" onClick={onConfirm}>Delete</Button>
            </Modal.Footer>
        </Modal>
    )
}

export default DeletePortfolioModal
