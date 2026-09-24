import { ParsedCharacterBundle } from './events';

export type ProjectorType = 'summary' | 'slideshow' | 'timeline';

export interface ProjectorProps {
  data: ParsedCharacterBundle;
  selectedCardIds: string[];
  onBackToSelector?: () => void;
}

export interface ProjectorOption {
  id: ProjectorType;
  title: string;
  description: string;
  icon: string;
  badge: string;
}
