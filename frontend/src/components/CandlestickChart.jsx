import React, { useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";

const CandlestickChart = () => {
  const chartContainerRef = useRef(null);

  const timeframe='minute_30'
  const target='10.00'

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { background: { color: "#fff" }, textColor: "#000" },
      grid: { vertLines: { color: "#eee" }, horzLines: { color: "#eee" } },
    });

    const candleSeries = chart.addCandlestickSeries();

    function fetchInitialData(url) {
      fetch(url)
          .then(response => response.json())
          .then(data => {
              const formattedData = data.map(item => ({
                  time: item.unix_time,
                  open: item.open,
                  high: item.high,
                  low: item.low,
                  close: item.close,
              }));
              candleSeries.setData(formattedData);
              lastCandle = formattedData[formattedData.length - 1];
          })
          .catch(error => console.error("Error fetching initial data:", error));
  }
fetchInitialData(`http://localhost:8000/market/history?timeframe=${timeframe}&target=${target}`)
    return () => {
      chart.remove();
    };
  }, []);

  return <div ref={chartContainerRef} style={{ width: "100%", height: "400px" }} />;
};

export default CandlestickChart;
