import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function DashboardTrainPage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard initialSection="train" showSectionTabs={false} />
    </Suspense>
  );
}
