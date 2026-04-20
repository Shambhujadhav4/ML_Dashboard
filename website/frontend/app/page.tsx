import Link from "next/link";

const highlights = [
  "FastAPI backend that wraps your existing preprocessing and training modules",
  "Next.js frontend with a clean, task-focused experience",
  "A complete workflow from upload to exploration, preprocessing, training, and results",
];

const stats = [
  { label: "Workflow Steps", value: "6" },
  { label: "Core Pages", value: "5" },
  { label: "Live API", value: "FastAPI" },
];

const flow = ["Upload", "Exploration", "Preprocessing", "Training", "Results"];

export default function HomePage() {
  return (
    <section className="stack home-page">
      <div className="home-hero panel">
        <div className="home-hero-content">
          <p className="eyebrow">Data Workflow</p>
          <h1>Build and evaluate machine learning pipelines with clarity.</h1>
          <p className="lead">
            DataPilot combines a polished frontend, reusable API routes, and a clear
            ML workflow so your project looks like a production-ready product, not only a demo.
          </p>
          <div className="button-row">
            <Link href="/upload" className="button button-primary">
              Start with upload flow
            </Link>
            <Link href="/exploration" className="button button-secondary">
              Go to exploration
            </Link>
          </div>
        </div>
        <div className="home-stats">
          {stats.map((item) => (
            <div key={item.label} className="home-stat-card">
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="home-grid">
        <div className="panel home-panel">
          <p className="eyebrow">Why this version is stronger</p>
          <ul className="feature-list">
            {highlights.map((highlight) => (
              <li key={highlight}>{highlight}</li>
            ))}
          </ul>
        </div>

        <div className="panel home-panel">
          <p className="eyebrow">Workflow at a glance</p>
          <div className="flow-track">
            {flow.map((step, index) => (
              <div key={step} className="flow-chip">
                <span>{index + 1}</span>
                <strong>{step}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="panel home-panel">
        <p className="eyebrow">Suggested next milestone</p>
        <h2>Follow the step flow: upload, explore, preprocess, train, results.</h2>
        <p className="muted">
          The app is now organized into separate pages so each stage of the ML workflow has its own URL and layout.
        </p>
      </div>
    </section>
  );
}
