import React, { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi, ColorType, LineStyle, LineSeries, CandlestickSeries, createSeriesMarkers } from 'lightweight-charts';

type Candle = { date: string; open: number; high: number; low: number; close: number };
type BandPoint = { date: string; value: number };
type TradeMarker = { date: string; action: 'BUY' | 'SELL'; price: number };

interface BollingerChartProps {
  title?: string;
  candles: Candle[];
  upper?: BandPoint[];
  lower?: BandPoint[];
  trades?: TradeMarker[];
  height?: number;
}

const BollingerChart: React.FC<BollingerChartProps> = ({
  title = 'Price with Bollinger Bands',
  candles,
  upper = [],
  lower = [],
  trades = [],
  height = 400,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const upperRef = useRef<ISeriesApi<'Line'> | null>(null);
  const lowerRef = useRef<ISeriesApi<'Line'> | null>(null);

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
      layout: { textColor: 'white', background: { type: ColorType.Solid, color: 'black' } },
    } as const;
    const chart = createChart(chartContainerRef.current, chartOptions);
    chart.applyOptions({
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.15 } },
      crosshair: { horzLine: { visible: true, labelVisible: true }, vertLine: { labelVisible: true } },
      grid: { vertLines: { color: '#111' }, horzLines: { color: '#111' } },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      borderVisible: false,
    });

    const upperLine = chart.addSeries(LineSeries, { color: '#ec4899', lineWidth: 2, lineStyle: LineStyle.Solid, priceLineVisible: false });
    const lowerLine = chart.addSeries(LineSeries, { color: '#f59e0b', lineWidth: 2, lineStyle: LineStyle.Solid, priceLineVisible: false });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    upperRef.current = upperLine;
    lowerRef.current = lowerLine;

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

    const normalizeDate = (d: string): string => (typeof d === 'string' && d.length >= 10 ? d.substring(0, 10) : (d as unknown as string));

    candleSeriesRef.current.setData(
      candles.map(c => ({ time: normalizeDate(c.date), open: c.open, high: c.high, low: c.low, close: c.close }))
    );

    // Bands
    const times = candles.map(c => normalizeDate(c.date));
    const upperMap = new Map((upper || []).filter(p => typeof p.value === 'number' && isFinite(p.value as number)).map(p => [normalizeDate(p.date), p.value as number]));
    const lowerMap = new Map((lower || []).filter(p => typeof p.value === 'number' && isFinite(p.value as number)).map(p => [normalizeDate(p.date), p.value as number]));

    if (upperRef.current) {
      upperRef.current.setData(times.map(t => (upperMap.has(t) ? { time: t, value: upperMap.get(t)! } : { time: t }) as any));
    }
    if (lowerRef.current) {
      lowerRef.current.setData(times.map(t => (lowerMap.has(t) ? { time: t, value: lowerMap.get(t)! } : { time: t }) as any));
    }

    // Trades as markers
    const markers: Marker[] = [];
    for (const t of trades || []) {
      const action = (t.action || '').toString().toUpperCase();
      markers.push({
        time: normalizeDate(t.date),
        position: action === 'BUY' ? 'belowBar' : 'aboveBar',
        color: action === 'BUY' ? '#2196F3' : '#e91e63',
        shape: action === 'BUY' ? 'arrowUp' : 'arrowDown',
        text: '',
      });
    }
    // Always reset markers (even if none exist)
    if (candleSeriesRef.current) {
      (createSeriesMarkers as any)(candleSeriesRef.current, markers);
    }

    if (chartRef.current) chartRef.current.timeScale().fitContent();
  }, [candles, upper, lower, trades]);

  return (
    <div className="bollinger-chart">
      <h3>{title}</h3>
      <div ref={chartContainerRef} style={{ width: '100%', height: `${height}px`, position: 'relative' }} />
    </div>
  );
};

export default BollingerChart;


