import { Suspense } from "react";
import { ProjectDashboard } from "@/components/project-dashboard";

export default function DashboardExplorePage() {
  return (
    <Suspense fallback={null}>
      <ProjectDashboard initialSection="explore" showSectionTabs={false} />
    </Suspense>
  );
}
