import { useState } from "react";
import RuneNode from "./rune-node";

interface Rune {
  id: number;
  name: string;
  image_url: string;
  description: string;
}

interface RunePageProps {
  runes: Rune[];
}

export default function RunePage({ runes }: RunePageProps) {
  const [selectedRunes, setSelectedRunes] = useState<number[]>([]);

  const toggleRune = (runeId: number) => {
    setSelectedRunes((prev) =>
      prev.includes(runeId) ? prev.filter((id) => id !== runeId) : [...prev, runeId]
    );
  };

  // Helper function to get rune by index
  const getRune = (index: number) => runes[index] || null;

  return (
    <div className="relative w-full max-w-4xl mx-auto min-h-[600px] p-8">
      {/* Top row */}
      <div className="flex justify-center gap-4 mb-16">
        {[0, 1, 2, 3, 4].map((index) => (
          <RuneNode
            key={index}
            rune={getRune(index)}
            isSelected={selectedRunes.includes(getRune(index)?.id || -1)}
            onClick={() => getRune(index) && toggleRune(getRune(index)!.id)}
          />
        ))}
      </div>

      {/* Middle row */}
      <div className="flex justify-center gap-4 mb-16">
        {[5, 6, 7].map((index) => (
          <RuneNode
            key={index}
            rune={getRune(index)}
            isSelected={selectedRunes.includes(getRune(index)?.id || -1)}
            onClick={() => getRune(index) && toggleRune(getRune(index)!.id)}
          />
        ))}
      </div>

      {/* Bottom row */}
      <div className="flex justify-center gap-4">
        {[8, 9, 10].map((index) => (
          <RuneNode
            key={index}
            rune={getRune(index)}
            isSelected={selectedRunes.includes(getRune(index)?.id || -1)}
            onClick={() => getRune(index) && toggleRune(getRune(index)!.id)}
          />
        ))}
      </div>

      {/* Connecting lines */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none -z-10"
        style={{ filter: "drop-shadow(0 0 2px rgba(74, 222, 128, 0.5))" }}
      >
        {/* Vertical lines */}
        <line x1="50%" y1="15%" x2="50%" y2="40%" className="stroke-green-400/50" strokeWidth="2" />
        <line x1="50%" y1="45%" x2="50%" y2="70%" className="stroke-green-400/50" strokeWidth="2" />

        {/* Horizontal lines */}
        <line x1="30%" y1="15%" x2="70%" y2="15%" className="stroke-green-400/50" strokeWidth="2" />
        <line x1="35%" y1="45%" x2="65%" y2="45%" className="stroke-green-400/50" strokeWidth="2" />
        <line x1="35%" y1="70%" x2="65%" y2="70%" className="stroke-green-400/50" strokeWidth="2" />
      </svg>
    </div>
  );
}
