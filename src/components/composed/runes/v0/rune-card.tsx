import { Card, CardContent } from "@/components/ui/card";

interface RuneCardProps {
  rune: {
    id: number;
    name: string;
    image_url: string;
  };
  onClick: () => void;
}

export default function RuneCard({ rune, onClick }: RuneCardProps) {
  return (
    <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={onClick}>
      <CardContent className="p-4 flex flex-col items-center">
        <img src={rune.image_url || "/placeholder.svg"} alt={rune.name} className="w-16 h-16 mb-2" />
        <h3 className="text-sm font-medium text-center">{rune.name}</h3>
      </CardContent>
    </Card>
  );
}
