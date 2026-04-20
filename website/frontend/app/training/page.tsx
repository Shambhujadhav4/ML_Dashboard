import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function TrainingPage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard
        initialSection="train"
        showSectionTabs={false}
        stepLabel="Step 4"
        pageTitle="Model training"
        description="Choose a task type, select an algorithm, train the model, and jump to results."
      />
    </Suspense>
  );
}
