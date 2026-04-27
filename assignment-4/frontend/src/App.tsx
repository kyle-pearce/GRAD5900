import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { getOnboardingStatus } from "./api/client";
import Chat from "./pages/Chat";
import Onboard from "./pages/Onboard";

function AppRoutes() {
  const [onboarded, setOnboarded] = useState<boolean | null>(null);

  useEffect(() => {
    getOnboardingStatus()
      .then(({ onboarded }) => setOnboarded(onboarded))
      .catch(() => setOnboarded(false));
  }, []);

  if (onboarded === null) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center text-zinc-500 text-sm">
        Connecting…
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/onboard" element={<Onboard />} />
      <Route
        path="/"
        element={onboarded ? <Chat /> : <Navigate to="/onboard" replace />}
      />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
