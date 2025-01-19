import { useState } from "react";
import { BottomNavigation } from "@/components/composed/bottom-navigation";
type Section = "liveCounter" | "builds" | "champions";

export function Layout() {
  const [activeSection, setActiveSection] = useState<Section>("liveCounter");

  return (
    <div className="flex flex-col h-screen bg-background">
      <main className="flex-1 overflow-y-auto p-4">
        {activeSection === "liveCounter" && <LiveCounter />}
        {activeSection === "builds" && <Builds />}
        {activeSection === "champions" && <Champions />}
      </main>
      <BottomNavigation activeSection={activeSection} setActiveSection={setActiveSection} />
    </div>
  );
}

function LiveCounter() {
  return <h2 className="text-2xl font-bold">Live Counter</h2>;
}

function Builds() {
  return (
    <div>
      <h2 className="text-2xl font-bold">Builds</h2>
    </div>
  );
}

function Champions() {
  return <h2 className="text-2xl font-bold">Champions</h2>;
}
