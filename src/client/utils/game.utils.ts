import { CardType, Player } from '../types/game.types';

export function getPlayerById(players: Player[], id: string): Player | undefined {
  return players.find(player => player.id === id);
}

export function getPlayerByName(players: Player[], name: string): Player | undefined {
  return players.find(player => player.name === name);
}

export function isActionTargetable(actionType: string): boolean {
  return ['coup', 'assassinate', 'steal'].includes(actionType);
}

export function getCardColor(cardType: CardType): string {
  switch (cardType) {
    case 'contessa': return 'var(--contessa-red)';
    case 'captain': return 'var(--captain-blue)';
    case 'duke': return 'var(--duke-purple)';
    case 'ambassador': return 'var(--ambassador-green)';
    case 'assassin': return 'var(--assassin-black)';
    default: return '#888888';
  }
} 