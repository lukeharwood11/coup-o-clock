export type CardType = 'contessa' | 'captain' | 'duke' | 'ambassador' | 'assassin' | 'unknown';

export interface Player {
    id: string;
    name: string;
    coins: number;
    cards: CardType[];
    revealed_cards: CardType[];
    is_alive: boolean;
}

export interface GameState {
    status: 'WAITING' | 'PLAYING' | 'FINISHED';
    players: Player[];
    current_player: string;
    turn_number: number;
    is_your_turn: boolean;
    challenge_window_open: boolean;
    counteraction_window_open: boolean;
    pending_action?: {
        player_id: string;
        action: {
            action_type: string;
            [key: string]: any;
        };
    };
    pending_counteraction?: {
        player_id: string;
        counter_action: {
            counter_type: string;
            [key: string]: any;
        };
        claimed_character: CardType;
    };
}

export type GameAction = {
    action_type: string;
    [key: string]: any;
};
