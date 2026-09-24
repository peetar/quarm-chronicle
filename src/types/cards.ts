import { ParsedCharacterBundle } from './events';

export type CardCategory = 'overview' | 'combat' | 'progression' | 'social' | 'interactive';

export interface CardDefinition {
  id: string;
  title: string;
  shortTitle: string;
  category: CardCategory;
  description: string;
  icon: string;
  defaultSelected: boolean;
}

export interface CardProps {
  data: ParsedCharacterBundle;
  className?: string;
  compact?: boolean;
}
