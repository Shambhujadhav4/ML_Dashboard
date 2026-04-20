import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function DashboardPreparePage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard initialSection="prepare" showSectionTabs={false} />
    </Suspense>
  );
}
