import {useState,useEffect} from 'react'

import TokenCard from "./TokenCard"
import Chart from "./Chart"
import TimeFrames from "./TimeFrames"
import TransactionCard from "./TransactionCard"
import MarketTokens from "./MarketTokens"

export default function Dashboard()
{   
    // const data = [
    //     { time: "2023-01-01", open: 100, high: 110, low: 90, close: 105 },
    //     { time: "2023-01-02", open: 105, high: 115, low: 95, close: 100 },
    //     { time: "2023-01-03", open: 100, high: 120, low: 80, close: 110 },
    //     { time: "2023-01-04", open: 110, high: 130, low: 100, close: 125 },
    //   ]

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