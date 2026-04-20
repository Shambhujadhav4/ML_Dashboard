type MetricItem = {
  label: string;
  value: string;
};

export function MetricsCards({ items }: { items: MetricItem[] }) {
  return (
    <div className="metrics-grid">
      {items.map((item) => (
        <article key={item.label} className="metric-card">
          <p className="metric-label">{item.label}</p>
          <p className="metric-value">{item.value}</p>
        </article>
      ))}
    </div>
  );
}
