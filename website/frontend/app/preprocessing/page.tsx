import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function PreprocessingPage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard
        initialSection="prepare"
        showSectionTabs={false}
        stepLabel="Step 3"
        pageTitle="Preprocessing"
        description="Drop columns, handle missing values, encode categorical fields, scale features, and handle outliers."
      />
    </Suspense>
  );
}
