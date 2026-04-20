import type { FeatureImportanceRow } from "@/lib/types";

export function FeatureImportanceTable({
  rows,
}: {
  rows: FeatureImportanceRow[];
}) {
  if (!rows.length) {
    return <p className="muted">Feature importance is not available for this model.</p>;
  }

  return (
    <div className="table-shell">
      <table className="data-table">
        <thead>
          <tr>
            <th>Feature</th>
            <th>Importance</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.feature}>
              <td>{row.feature}</td>
              <td>{row.importance.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
