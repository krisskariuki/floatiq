import TokenRecord from "./TokenRecord"
export default function MarketTokens()
{
    return(
        <div className="market-tokens">
            <h4>Market</h4>
            <div className="market-tokens_list">
            <TokenRecord/>
            <TokenRecord/>
            <TokenRecord/>
            <TokenRecord/>
            <TokenRecord/>
            <TokenRecord/>
            </div>
        </div>
    )
}