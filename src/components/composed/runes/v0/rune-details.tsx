import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";

interface RuneDetailsProps {
  rune: {
    id: number;
    name: string;
    image_url: string;
    description: string;
  } | null;
  onClose: () => void;
}

export default function RuneDetails({ rune, onClose }: RuneDetailsProps) {
  if (!rune) return null;

  return (
    <Drawer open={!!rune} onClose={onClose}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle className="flex items-center">
            <img src={rune.image_url || "/placeholder.svg"} alt={rune.name} className="w-8 h-8 mr-2" />
            {rune.name}
          </DrawerTitle>
          <DrawerDescription>{rune.description}</DrawerDescription>
        </DrawerHeader>
        <div className="p-4 pt-0">
          <DrawerClose asChild>
            <Button className="w-full" onClick={onClose}>
              Close
            </Button>
          </DrawerClose>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
