import { Navigate, Route, Routes } from "react-router-dom";
import { Shell } from "@/components/layout/Shell";
import { AskScreen } from "@/screens/AskScreen";
import { CompareScreen } from "@/screens/CompareScreen";
import { FindingScreen } from "@/screens/FindingScreen";
import { MemoryScreen } from "@/screens/MemoryScreen";
import { RunDetailScreen } from "@/screens/RunDetailScreen";
import { RunsScreen } from "@/screens/RunsScreen";
import { VerifyScreen } from "@/screens/VerifyScreen";

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<Navigate to="/runs" replace />} />
        <Route path="/runs" element={<RunsScreen />} />
        <Route path="/runs/:jobId" element={<RunDetailScreen />} />
        <Route path="/runs/:jobId/findings/:findingId" element={<FindingScreen />} />
        <Route path="/ask" element={<AskScreen />} />
        <Route path="/compare" element={<CompareScreen />} />
        <Route path="/memory" element={<MemoryScreen />} />
        <Route path="/verify" element={<VerifyScreen />} />
        <Route path="*" element={<Navigate to="/runs" replace />} />
      </Routes>
    </Shell>
  );
}
