import React, { useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";

const Chart = () => {
  const chartContainerRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth || 600,
      height: 400,
      layout: {
        backgroundColor: "#fff",
        textColor: "#000",
      },
      grid: {
        vertLines: { color: "#e1e1e1" },
        horzLines: { color: "#e1e1e1" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candlestickSeries = chart.addCandlestickSeries();

    // Sample candlestick data
    const sampleData = [
      { time: "2023-03-01", open: 100, high: 110, low: 90, close: 105 },
      { time: "2023-03-02", open: 105, high: 115, low: 95, close: 100 },
      { time: "2023-03-03", open: 100, high: 120, low: 80, close: 110 },
      { time: "2023-03-04", open: 110, high: 130, low: 100, close: 125 },
    ];

    candlestickSeries.setData(sampleData);

    // Resize chart on window resize
    const handleResize = () => {
      chart.applyOptions({
        width: chartContainerRef.current.clientWidth,
      });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      chart.remove();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <div ref={chartContainerRef} style={{ width: "100%", height: "400px" }} />;
};

export default Chart;
