import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, AreaSeries, ColorType } from 'lightweight-charts';

interface PortfolioData {
  date: string;
  portfolio_value: number;
}

interface PortfolioChartProps {
  data: PortfolioData[];
  height?: number;
}

const PortfolioChart: React.FC<PortfolioChartProps> = ({ data, height = 400 }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null);
  const legendRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chartOptions = {
      layout: {
        textColor: 'black',
        background: { type: ColorType.Solid, color: 'white' },
      },
    };

    // Create chart
    const chart = createChart(chartContainerRef.current, chartOptions);

    chart.applyOptions({
      rightPriceScale: {
        scaleMargins: {
          top: 0.4, // leave some space for the legend
          bottom: 0.15,
        },
      },
      crosshair: {
        // hide the horizontal crosshair line
        horzLine: {
          visible: true,
          labelVisible: true,
        },
      },
      // hide the grid lines
      grid: {
        vertLines: {
          visible: false,
        },
        horzLines: {
          visible: false,
        },
      },
    });

    // Create area series
    const areaSeries = chart.addSeries(AreaSeries, {
      topColor: '#2962FF',
      bottomColor: 'rgba(41, 98, 255, 0.28)',
      lineColor: '#2962FF',
      lineWidth: 2,
      crosshairMarkerVisible: false,
    });

    chartRef.current = chart;
    seriesRef.current = areaSeries;

    // Create legend
    const legend = document.createElement('div');
    legend.style.cssText = `
      position: absolute; 
      left: 12px; 
      top: 12px; 
      z-index: 1; 
      font-size: 14px; 
      font-family: sans-serif; 
      line-height: 18px; 
      font-weight: 300;
      color: black;
    `;
    chartContainerRef.current.appendChild(legend);
    legendRef.current = legend;

    // Legend functions
    const getLastBar = (series: ISeriesApi<'Area'>) => {
      // Get the last data point by using a very large index
      const data = series.data();
      if (data.length > 0) {
        return data[data.length - 1];
      }
      return null;
    };

    const formatPrice = (price: number) => (Math.round(price * 100) / 100).toFixed(2);

    const setTooltipHtml = (name: string, date: string, price: string) => {
      if (legendRef.current) {
        legendRef.current.innerHTML = `
          <div style="font-size: 24px; margin: 4px 0px;">${name}</div>
          <div style="font-size: 22px; margin: 4px 0px;">$${price}</div>
          <div>${date}</div>
        `;
      }
    };

    const updateLegend = (param: any) => {
      const validCrosshairPoint = !(
        param === undefined || param.time === undefined || param.point.x < 0 || param.point.y < 0
      );
      const bar = validCrosshairPoint ? param.seriesData.get(areaSeries) : getLastBar(areaSeries);
      
      if (bar) {
        // time is in the same format that you supplied to the setData method,
        // which in this case is YYYY-MM-DD
        const time = bar.time;
        const price = bar.value !== undefined ? bar.value : (bar as any).close;
        const formattedPrice = formatPrice(price);
        setTooltipHtml('Portfolio Value', time, formattedPrice);
      }
    };

    chart.subscribeCrosshairMove(updateLegend);
    updateLegend(undefined);

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chart) {
        chart.remove();
      }
    };
  }, [height]);

  useEffect(() => {
    if (seriesRef.current && data.length > 0) {
      // Convert data to TradingView format
      const chartData = data.map(item => ({
        time: item.date,
        value: item.portfolio_value,
      }));

      seriesRef.current.setData(chartData);
      
      // Fit content and update legend
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }
    }
  }, [data]);

  return (
    <div className="portfolio-chart">
      <h3>Portfolio Value Over Time</h3>
      <div 
        ref={chartContainerRef} 
        style={{ 
          width: '100%', 
          height: `${height}px`,
          position: 'relative'
        }}
      />
    </div>
  );
};

export default PortfolioChart;
