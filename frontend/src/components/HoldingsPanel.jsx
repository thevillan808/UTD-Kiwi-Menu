import { Table } from 'react-bootstrap'

function HoldingsPanel({ investments }) {
    if (!investments || investments.length === 0) {
        return <p className="text-muted">No holdings in this portfolio.</p>
    }

    return (
        <Table hover bordered responsive>
            <thead className="table-light">
                <tr>
                    <th>Ticker</th>
                    <th>Shares</th>
                </tr>
            </thead>
            <tbody>
                {investments.map(inv => (
                    <tr key={inv.ticker}>
                        <td className="fw-semibold">{inv.ticker}</td>
                        <td>{inv.quantity}</td>
                    </tr>
                ))}
            </tbody>
        </Table>
    )
}

export default HoldingsPanel
