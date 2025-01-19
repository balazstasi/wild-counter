export interface WildRiftItem {
  id: string;
  name: string;
  type:
    | "PHYSICAL_DAMAGE"
    | "MAGIC_DAMAGE"
    | "BOOTS"
    | "MID_TIER"
    | "BASIC"
    | "KEYSTONE"
    | "DOMINATION"
    | "PRECISION"
    | "RESOLVE"
    | "INSPIRATION"
    | "SPELLS";
  cost?: number;
  stats?: {
    attackDamage?: number;
    abilityPower?: number;
    armor?: number;
    magicResistance?: number;
    health?: number;
    mana?: number;
    attackSpeed?: number;
    criticalRate?: number;
    abilityHaste?: number;
    moveSpeed?: number;
    physicalVamp?: number;
    omnivamp?: number;
    manaRegen?: number;
    healthRegen?: number;
  };
  effects?: {
    name: string;
    description: string;
  }[];
  description?: string;
  tips?: string;
}
