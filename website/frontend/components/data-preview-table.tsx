type PreviewRow = Record<string, unknown>;

export function DataPreviewTable({
  columns,
  rows,
  showIndex = false,
}: {
  columns: string[];
  rows: PreviewRow[];
  showIndex?: boolean;
}) {
  if (!columns.length) {
    return <p className="muted">No columns available yet.</p>;
  }

  return (
    <div className="table-shell">
      <table className="data-table">
        <thead>
          <tr>
            {showIndex ? <th className="index-col">#</th> : null}
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${index}-${columns[0] ?? "row"}`}>
              {showIndex ? <td className="index-col">{index}</td> : null}
              {columns.map((column) => (
                <td key={`${index}-${column}`}>
                  {formatCellValue(row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCellValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}
