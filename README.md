# Coup O' Clock

A web-based implementation of the popular card game Coup.

## Game Rules

In Coup, each player starts with two face-down cards. On your turn, you can take one of the following actions:

- **Income**: Take 1 coin from the bank.
- **Foreign Aid**: Take 2 coins from the bank (can be blocked by the Duke).
- **Coup**: Pay 7 coins to target and eliminate another player's card.
- **Tax**: Take 3 coins from the bank (requires Duke).
- **Assassinate**: Pay 3 coins to target a player and force them to lose a card (requires Assassin, can be blocked by the Contessa).
- **Steal**: Take 2 coins from another player (requires Captain, can be blocked by the Captain or Ambassador).
- **Exchange**: Exchange cards with the deck (requires Ambassador).

Players can also bluff, claiming to have a certain role to use a special action (even if they don't have that role). Other players can challenge the claim, and if the challenger is wrong, they lose a card; if the claim is wrong, the liar loses a card.

The goal is to be the last player with cards remaining.

## Character Cards

- **Duke**: Can take Tax (3 coins) and block Foreign Aid.
- **Assassin**: Can Assassinate (pay 3 coins to make a player lose a card).
- **Captain**: Can Steal (take 2 coins from another player) and block Stealing.
- **Ambassador**: Can Exchange cards with the deck and block Stealing.
- **Contessa**: Can block Assassination.

## API Documentation

API documentation is available at `http://localhost:8080/docs` when the server is running.

## Game Flow

1. Create or join a room
2. Wait for all players to be ready
3. On your turn, select an action
4. Other players can challenge or counter your action
5. The game continues until only one player remains

## WebSocket Messages

The game uses WebSocket for real-time communication. Here are the main message types:

- `chat`: Send chat messages
- `ready`: Mark yourself as ready to start the game
- `game_action`: Perform a game action
  - `perform_action`: Take an action (income, foreign aid, coup, etc.)
  - `challenge`: Challenge another player's action
  - `pass_challenge`: Pass on challenging
  - `counter`: Counter an action
  - `pass_counter`: Pass on countering
  - `complete_exchange`: Complete an exchange action


```bash
uv sync
uv run -m app.main
```

### Frontend
 
```bash
npm install
npm run dev 
```

### Database