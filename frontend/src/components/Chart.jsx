import React, { useState, useEffect, useRef } from "react";
import { createChart } from "lightweight-charts";

const ChartComponent = () => {
  const chartContainerRef = useRef(null);
  const chartInstanceRef = useRef(null);
  const recordSourceRef = useRef(null); // Ref for EventSource to clean it up

  const token="RUBY"
  const timeFrame="minute15"

  const fetchSeries = async () => {
    try {
      const response = await fetch(`http://localhost:8000/data/series/${timeFrame}/${token}`);
      const result = await response.json();
      return result; // Return the data to use it in the chart
    } catch (error) {
      console.error("Failed to fetch initial data:", error);
      return [];
    }
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.offsetWidth,
      height: chartContainerRef.current.offsetHeight,
      layout: {
        backgroundColor: "#FFFFFF",
        textColor: "#444",
      },
      grid: {
        vertLines: {
          color: "#e1e1e1",
        },
        horzLines: {
          color: "#e1e1e1",
        },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries();

    // Fetch initial data
    fetchSeries().then((data) => {
      candlestickSeries.setData(data);
    });

    // Set up EventSource for real-time updates
    const recordSource = new EventSource(`http://localhost:8000/data/stream/${timeFrame}/${token}`);
    recordSource.onmessage = (e) => {
      const data = JSON.parse(e.data);
      candlestickSeries.update(data);
    };

    // Save references for cleanup
    chartInstanceRef.current = chart;
    recordSourceRef.current = recordSource;

    // Resize chart on window resize
    const handleResize = () => {
      chart.applyOptions({
        width: chartContainerRef.current.offsetWidth,
        height: chartContainerRef.current.offsetHeight,
      });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      // Cleanup on component unmount
      chart.remove();
      recordSource.close();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return <div className="center-self-h chart" ref={chartContainerRef} />;
};

export default ChartComponent;
