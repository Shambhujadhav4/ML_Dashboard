import { Suspense } from "react";
import { ResultsOverview } from "@/components/results-overview";

export default function ResultsPage() {
  return (
    <Suspense fallback={null}>
      <ResultsOverview
        stepLabel="Step 6"
        pageTitle="Results and visualizations"
        description="Review trained-model metrics, feature importance, and evaluation charts from the backend."
      />
    </Suspense>
  );
}
