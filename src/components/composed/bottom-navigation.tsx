import { BoxIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

type Section = "liveCounter" | "builds" | "champions";

interface BottomNavigationProps {
  activeSection: Section;
  setActiveSection: (section: Section) => void;
}

export function BottomNavigation({ activeSection, setActiveSection }: BottomNavigationProps) {
  return (
    <nav className="flex justify-around items-center h-16 border-2 m-1 rounded-lg border-slate-100/20">
      <Button
        variant={activeSection === "liveCounter" ? "default" : "ghost"}
        size="icon"
        onClick={() => setActiveSection("liveCounter")}
      >
        <BoxIcon />
        <span className="sr-only">Live Counter</span>
      </Button>
      <Button
        variant={activeSection === "builds" ? "default" : "ghost"}
        size="icon"
        onClick={() => setActiveSection("builds")}
      >
        <BoxIcon />
        <span className="sr-only">Builds</span>
      </Button>
      <Button
        variant={activeSection === "champions" ? "default" : "ghost"}
        size="icon"
        onClick={() => setActiveSection("champions")}
      >
        <BoxIcon />
        <span className="sr-only">Champions</span>
      </Button>
    </nav>
  );
}
