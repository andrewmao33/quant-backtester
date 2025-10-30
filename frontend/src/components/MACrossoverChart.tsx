import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, ColorType, LineStyle, LineSeries, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts';

type Candle = {
  date: string; // YYYY-MM-DD
  open: number;
  high: number;
  low: number;
  close: number;
};

type TradeMarker = {
  date: string; // YYYY-MM-DD
  action: 'BUY' | 'SELL';
  price: number;
};

type SeriesPoint = {
  date: string; // YYYY-MM-DD
  value: number;
};

interface MACrossoverChartProps {
  title?: string;
  candles: Candle[];
  trades?: TradeMarker[];
  fastMA?: SeriesPoint[]; // e.g., fast SMA/EMA
  slowMA?: SeriesPoint[]; // e.g., slow SMA/EMA
  height?: number;
}

const MACrossoverChart: React.FC<MACrossoverChartProps> = ({
  title = 'Price with MA Crossover',
  candles,
  trades = [],
  fastMA = [],
  slowMA = [],
  height = 400,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const fastMARef = useRef<ISeriesApi<'Line'> | null>(null);
  const slowMARef = useRef<ISeriesApi<'Line'> | null>(null);

  type Marker = {
    time: string | number | { year: number; month: number; day: number };
    position: 'aboveBar' | 'belowBar';
    color: string;
    shape: 'arrowUp' | 'arrowDown' | 'circle';
    text?: string;
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chartOptions = {
      layout: {
        textColor: 'white',
        background: { type: ColorType.Solid, color: 'black' },
      },
    } as const;

    const chart = createChart(chartContainerRef.current, chartOptions);
    chart.applyOptions({
      rightPriceScale: {
        scaleMargins: {
          top: 0.1,
          bottom: 0.15,
        },
      },
      crosshair: {
        horzLine: { visible: true, labelVisible: true },
        vertLine: { labelVisible: true },
      },
      grid: {
        vertLines: { color: '#111' },
        horzLines: { color: '#111' },
      },
    });

    // Candles
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      borderVisible: false,
    });

    // Fast MA line
    const fastLine = chart.addSeries(LineSeries, {
      color: '#ec4899',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
    });

    // Slow MA line
    const slowLine = chart.addSeries(LineSeries, {
      color: '#f59e0b',
      lineWidth: 2,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    fastMARef.current = fastLine;
    slowMARef.current = slowLine;

    // Resize handling
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chart) chart.remove();
    };
  }, [height]);

  useEffect(() => {
    if (!candleSeriesRef.current || candles.length === 0) return;

    const normalizeDate = (d: string): string => {
      // Accept 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:mm:ss' and coerce to 'YYYY-MM-DD'
      if (typeof d === 'string' && d.length >= 10) return d.substring(0, 10);
      return d as unknown as string;
    };

    // Candles
    candleSeriesRef.current.setData(
      candles.map(c => ({ time: normalizeDate(c.date), open: c.open, high: c.high, low: c.low, close: c.close }))
    );

    // Markers (trades) via helper
    const markers: Marker[] = [];
    if (trades && trades.length > 0) {
      for (const t of trades) {
        const action = (t.action || '').toString().toUpperCase();
        markers.push({
          time: normalizeDate(t.date),
          position: action === 'BUY' ? 'belowBar' : 'aboveBar',
          color: action === 'BUY' ? '#2196F3' : '#e91e63',
          shape: action === 'BUY' ? 'arrowUp' : 'arrowDown',
          text: '',
        } as Marker);
      }
    }
    // Always reset markers (even if empty)
    if (candleSeriesRef.current) {
      (createSeriesMarkers as any)(candleSeriesRef.current, markers);
    }

    // Build aligned MA series (provide whitespace points before MA starts)
    const candleTimes = candles.map(c => normalizeDate(c.date));
    const fastMap = new Map(
      (fastMA || [])
        .filter(p => typeof p.value === 'number' && isFinite(p.value as number))
        .map(p => [normalizeDate(p.date), p.value as number])
    );
    const slowMap = new Map(
      (slowMA || [])
        .filter(p => typeof p.value === 'number' && isFinite(p.value as number))
        .map(p => [normalizeDate(p.date), p.value as number])
    );

    if (fastMARef.current) {
      const alignedFast = candleTimes.map((t) => {
        const v = fastMap.get(t);
        return typeof v === 'number' && isFinite(v) ? { time: t, value: v } : { time: t };
      });
      fastMARef.current.setData(alignedFast as any);
    }

    if (slowMARef.current) {
      const alignedSlow = candleTimes.map((t) => {
        const v = slowMap.get(t);
        return typeof v === 'number' && isFinite(v) ? { time: t, value: v } : { time: t };
      });
      slowMARef.current.setData(alignedSlow as any);
    }

    // Fit content
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  }, [candles, trades, fastMA, slowMA]);

  return (
    <div className="ma-crossover-chart">
      <h3>{title}</h3>
      <div
        ref={chartContainerRef}
        style={{ width: '100%', height: `${height}px`, position: 'relative' }}
      />
    </div>
  );
};

export default MACrossoverChart;


