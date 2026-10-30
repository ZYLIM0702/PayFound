import { useEffect, useRef } from 'react';
import { AgCharts, type AgChartInstance, type AgChartOptions } from 'ag-charts-community';

/** Thin wrapper around a standalone AG Chart; updates in place when options change. */
export function ChartBox({ options, height = 280, label }: { options: AgChartOptions; height?: number; label: string }) {
  const host = useRef<HTMLDivElement>(null);
  const chart = useRef<AgChartInstance | null>(null);
  useEffect(() => {
    if (!host.current) return;
    if (chart.current) { void chart.current.update(options); return; }
    chart.current = AgCharts.create({ ...options, container: host.current });
  }, [options]);
  useEffect(() => () => { chart.current?.destroy(); chart.current = null; }, []);
  return <div ref={host} role="img" aria-label={label} style={{ height }} />;
}
