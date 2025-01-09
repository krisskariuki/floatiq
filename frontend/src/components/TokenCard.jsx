export default function TokenCard()
{
    return(
        <div className="token-card">
            <div className="center-self-h token-card_chart"></div>
            <div className="token-card_img"></div>
            <p className="token-card_name">Token</p>
            <p className="token-card_alias">TKN</p>
            <p className="token-card_flop">15.00</p>
            <p className="token-card_change">
                <span className="material-symbols-outlined icon">arrow_drop_up</span>
                <span className="change-value">12.23%</span>
                </p>
            <p className="token-card_price">$12.34</p>
        </div>
    )
}