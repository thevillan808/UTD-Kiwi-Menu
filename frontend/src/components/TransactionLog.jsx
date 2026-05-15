import { Table } from 'react-bootstrap'

function TransactionLog({ transactions }) {
    if (!transactions || transactions.length === 0) {
        return <p className="text-muted">No transactions yet.</p>
    }

    return (
        <Table hover bordered responsive>
            <thead className="table-light">
                <tr>
                    <th>Ticker</th>
                    <th>Type</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {transactions.map((t, i) => (
                    <tr key={i}>
                        <td className="fw-semibold">{t.ticker}</td>
                        <td>
                            <span className={t.transaction_type === 'buy' ? 'text-success' : 'text-danger'}>
                                {t.transaction_type}
                            </span>
                        </td>
                        <td>{t.quantity}</td>
                        <td>${typeof t.price === 'number' ? t.price.toFixed(2) : t.price}</td>
                        <td>{t.date_time}</td>
                    </tr>
                ))}
            </tbody>
        </Table>
    )
}

export default TransactionLog
