"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function PlotlyChart({
  figure,
  emptyMessage,
  fontColor = "#1c1a17",
  showModeBar = false,
}: {
  figure: Record<string, unknown> | null;
  emptyMessage: string;
  fontColor?: string;
  showModeBar?: boolean;
}) {
  if (!figure) {
    return <p className="muted">{emptyMessage}</p>;
  }

  const data = Array.isArray(figure.data)
    ? (figure.data as Record<string, unknown>[])
    : [];
  const layout = (figure.layout as Record<string, unknown>) ?? {};
  const config = (figure.config as Record<string, unknown>) ?? {};

  return (
    <div className="plot-shell">
      <Plot
        data={data}
        layout={{
          ...layout,
          autosize: true,
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: fontColor },
        }}
        config={{
          responsive: true,
          displayModeBar: showModeBar,
          ...config,
        }}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler
      />
    </div>
  );
}
