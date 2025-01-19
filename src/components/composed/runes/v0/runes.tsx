import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import RuneCard from "./rune-card";
import RuneDetails from "./rune-details";

interface Rune {
  id: number;
  name: string;
  image_url: string;
  description: string;
}

interface RunesProps {
  runes: Rune[];
}

export default function Runes({ runes }: RunesProps) {
  const [selectedRune, setSelectedRune] = useState<Rune | null>(null);

  return (
    <div>
      <ScrollArea className="h-[calc(100vh-200px)]">
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {runes.map((rune) => (
            <RuneCard key={rune.id} rune={rune} onClick={() => setSelectedRune(rune)} />
          ))}
        </div>
      </ScrollArea>
      <RuneDetails rune={selectedRune} onClose={() => setSelectedRune(null)} />
    </div>
  );
}
