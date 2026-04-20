import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function ExplorationPage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard
        initialSection="explore"
        showSectionTabs={false}
        stepLabel="Step 2"
        pageTitle="Data exploration"
        description="Explore histograms, box plots, correlation heatmaps, scatter plots, and categorical counts."
      />
    </Suspense>
  );
}
