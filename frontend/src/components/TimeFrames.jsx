export default function TimeFrames()
{
    return(
        <div className="timeframes">
                    <button className="timeframe min-1">1M</button>
                    <button className="timeframe min-15">15M</button>
                    <button className="timeframe min-30">30M</button>
                    <button className="timeframe hr-1">1H</button>
                    <button className="timeframe hr-6">6H</button>
                    <button className="timeframe hr-12">12H</button>
                    <button className="timeframe day-1">1D</button>
                    <button className="timeframe week-1">1W</button>
            </div>
    )
}