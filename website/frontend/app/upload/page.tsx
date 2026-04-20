import { UploadForm } from "@/components/upload-form";

export default function UploadPage() {
  return (
    <section className="stack upload-page">
      <div className="section-heading">
        <p className="eyebrow">Step 1</p>
        <h1>Upload and inspect your dataset</h1>
        <p className="muted">
          Upload a CSV, then review preview rows, column information, and descriptive statistics before moving on.
        </p>
      </div>
      <UploadForm />
    </section>
  );
}
