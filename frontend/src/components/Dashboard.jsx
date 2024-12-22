import TokenCard from "./TokenCard"
import Chart from "./Chart"
import TimeFrames from "./TimeFrames"
import TransactionCard from "./TransactionCard"
import MarketTokens from "./MarketTokens"

export default function Dashboard()
{
    return(
        <section className="page dashboard">

            <div className="left-section">

            <div className="recent-tokens">
            <TokenCard/>
            <TokenCard/>
            <TokenCard/>
            <TokenCard/>
            </div>
            <div className="chart-area">
                <h3 className="chart-area_label">portfolio</h3>
                <TimeFrames/>
            <Chart/>
            </div>
            </div>
            <div className="right-section">
                <TransactionCard/>
                <MarketTokens/>
            </div>
        </section>
    )
}