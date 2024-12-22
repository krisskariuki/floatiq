export default function TransactionCard()
{
    return(
        <div className="transaction-card">
        <div className="transaction-card_options">
            <button className="transact withdraw">withdraw</button>
            <button className="transact deposit">deposit</button>
        </div>
        <p className="transaction-card_balance">$12,345.34</p>
        <p className="transaction-card_change">+12.34%</p>
        </div>
    )
}