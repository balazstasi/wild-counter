import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface RuneNodeProps {
  rune: {
    id: number;
    name: string;
    image_url: string;
    description: string;
  } | null;
  isSelected?: boolean;
  onClick?: () => void;
}

export default function RuneNode({ rune, isSelected, onClick }: RuneNodeProps) {
  if (!rune) return null;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onClick}
            className={cn(
              "relative w-16 h-16 rounded-full p-1 transition-all duration-200",
              "bg-slate-800 border-2 border-slate-600",
              "hover:border-green-400/50 hover:shadow-[0_0_15px_rgba(74,222,128,0.3)]",
              isSelected && "border-green-400 shadow-[0_0_20px_rgba(74,222,128,0.4)]"
            )}
          >
            <img
              src={rune.image_url || "/placeholder.svg"}
              alt={rune.name}
              className={cn(
                "w-full h-full rounded-full transition-opacity",
                isSelected ? "opacity-100" : "opacity-50"
              )}
            />
            {/* Golden indicator */}
            {isSelected && (
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.7)]" />
            )}
          </button>
        </TooltipTrigger>
        <TooltipContent className="bg-slate-800 border-slate-700 text-slate-100">
          <div className="max-w-xs">
            <h3 className="font-bold mb-1">{rune.name}</h3>
            <p className="text-sm text-slate-300">{rune.description}</p>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
