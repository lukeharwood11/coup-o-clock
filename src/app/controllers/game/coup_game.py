from typing import Dict, List, Optional, Tuple
import random
from app.models.game import GameState, PlayerState, GameStatus
import logging

# Define Coup-specific constants
CHARACTERS = ["duke", "assassin", "captain", "ambassador", "contessa"]
STARTING_COINS = 2
CARDS_PER_PLAYER = 2

# Define action costs
COUP_COST = 7
ASSASSINATE_COST = 3


# Define actions
class ActionType:
    INCOME = "income"
    FOREIGN_AID = "foreign_aid"
    COUP = "coup"
    TAX = "tax"  # Duke action
    ASSASSINATE = "assassinate"  # Assassin action
    STEAL = "steal"  # Captain action
    EXCHANGE = "exchange"  # Ambassador action

    # Counteractions
    BLOCK_FOREIGN_AID = "block_foreign_aid"  # Duke
    BLOCK_ASSASSINATION = "block_assassination"  # Contessa
    BLOCK_STEALING = "block_stealing"  # Captain or Ambassador

    # Challenge
    CHALLENGE = "challenge"


class CoupGame:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.pending_action = None
        self.pending_challenge = None
        self.pending_counteraction = None
        self.challenge_window_open = False
        self.counteraction_window_open = False

    def create_deck(self) -> List[str]:
        """Create a deck of cards for Coup"""
        cards = []
        for character in CHARACTERS:
            cards.extend([character] * 3)  # 3 copies of each character
        random.shuffle(cards)
        return cards

    def deal_cards(self) -> None:
        """Deal cards to players"""
        for player in self.game_state.players:
            player.cards = [self.game_state.deck.pop() for _ in range(CARDS_PER_PLAYER)]
            player.coins = STARTING_COINS

    def is_action_valid(self, player_id: str, action: Dict) -> Tuple[bool, str]:
        """Check if an action is valid"""
        logger = logging.getLogger(__name__)

        logger.info(f"Validating action: {action} for player {player_id}")

        action_type = action.get("action_type")
        if not action_type:
            logger.error(f"No action type specified in action: {action}")
            return False, "No action type specified"

        # Find the player
        player = next((p for p in self.game_state.players if p.id == player_id), None)
        if not player:
            logger.error(f"Player {player_id} not found")
            return False, "Player not found"

        # Check if it's the player's turn
        current_player = self.game_state.get_current_player()
        if not current_player or current_player.id != player_id:
            logger.error(
                f"Not player {player_id}'s turn. Current player: {current_player.id if current_player else 'None'}"
            )
            return False, "Not your turn"

        # Check if the player is alive
        if not player.is_alive:
            return False, "Player is not alive"

        # If player has 10+ coins, they must coup
        if player.coins >= 10 and action_type != ActionType.COUP:
            return False, "You must perform a coup when you have 10 or more coins"

        # Check action-specific requirements
        if action_type == ActionType.COUP:
            # Check if player has enough coins
            if player.coins < COUP_COST:
                return False, "Not enough coins for coup"

            # Check if target is specified and valid
            target_id = action.get("target_id")
            if not target_id:
                return False, "No target specified for coup"

            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )
            if not target:
                return False, "Target player not found"

            if not target.is_alive:
                return False, "Target player is not alive"

        elif action_type == ActionType.ASSASSINATE:
            # Check if player has enough coins
            if player.coins < ASSASSINATE_COST:
                return False, "Not enough coins for assassination"

            # Check if target is specified and valid
            target_id = action.get("target_id")
            if not target_id:
                return False, "No target specified for assassination"

            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )
            if not target:
                return False, "Target player not found"

            if not target.is_alive:
                return False, "Target player is not alive"

        elif action_type == ActionType.STEAL:
            # Check if target is specified and valid
            target_id = action.get("target_id")
            if not target_id:
                return False, "No target specified for stealing"

            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )
            if not target:
                return False, "Target player not found"

            if not target.is_alive:
                return False, "Target player is not alive"

            if target.coins == 0:
                return False, "Target player has no coins to steal"

        return True, ""

    def perform_action(self, player_id: str, action: Dict) -> Dict:
        """Perform an action in the game"""
        action_type = action.get("action_type")

        # Find the player
        player = next((p for p in self.game_state.players if p.id == player_id), None)
        if not player:
            return {"success": False, "message": "Player not found"}

        # For actions that can be challenged or countered, set up the pending action
        if action_type in [
            ActionType.TAX,
            ActionType.ASSASSINATE,
            ActionType.STEAL,
            ActionType.EXCHANGE,
            ActionType.FOREIGN_AID,
        ]:
            self.pending_action = {"player_id": player_id, "action": action}

            # Open challenge window for character claims
            if action_type in [
                ActionType.TAX,
                ActionType.ASSASSINATE,
                ActionType.STEAL,
                ActionType.EXCHANGE,
            ]:
                self.challenge_window_open = True
                return {
                    "success": True,
                    "message": f"Player {player.name} is attempting {action_type}",
                    "state": "challenge_window",
                }

            # Open counteraction window for foreign aid
            if action_type == ActionType.FOREIGN_AID:
                self.counteraction_window_open = True
                return {
                    "success": True,
                    "message": f"Player {player.name} is attempting to take foreign aid",
                    "state": "counteraction_window",
                }

        # For direct actions that can't be challenged or countered, execute immediately
        if action_type == ActionType.INCOME:
            player.coins += 1
            self.game_state.last_action = {
                "type": ActionType.INCOME,
                "player": player.name,
            }
            self.game_state.next_player()
            return {"success": True, "message": f"Player {player.name} took income"}

        elif action_type == ActionType.COUP:
            target_id = action.get("target_id")
            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )

            # Deduct coins
            player.coins -= COUP_COST

            # Target loses a card
            self._lose_card(target_id, action.get("card_index", 0))

            self.game_state.last_action = {
                "type": ActionType.COUP,
                "player": player.name,
                "target": target.name,
            }

            # Check if game is over
            if self.game_state.is_game_over():
                self.game_state.status = GameStatus.FINISHED
                return {
                    "success": True,
                    "message": f"Player {player.name} performed a coup against {target.name}",
                    "game_over": True,
                }

            self.game_state.next_player()
            return {
                "success": True,
                "message": f"Player {player.name} performed a coup against {target.name}",
            }

        return {"success": False, "message": "Invalid action"}

    def resolve_challenge(self, challenger_id: str, challenge_successful: bool) -> Dict:
        """Resolve a challenge"""
        if not self.pending_action:
            return {"success": False, "message": "No pending action to challenge"}

        action_player_id = self.pending_action["player_id"]
        action_player = next(
            (p for p in self.game_state.players if p.id == action_player_id), None
        )
        challenger = next(
            (p for p in self.game_state.players if p.id == challenger_id), None
        )

        if not action_player or not challenger:
            return {"success": False, "message": "Player not found"}

        action = self.pending_action["action"]
        action_type = action.get("action_type")

        # Determine which character is being claimed
        claimed_character = None
        if action_type == ActionType.TAX:
            claimed_character = "duke"
        elif action_type == ActionType.ASSASSINATE:
            claimed_character = "assassin"
        elif action_type == ActionType.STEAL:
            claimed_character = "captain"
        elif action_type == ActionType.EXCHANGE:
            claimed_character = "ambassador"

        if not claimed_character:
            return {"success": False, "message": "Invalid action for challenge"}

        # Check if the player has the claimed character
        has_character = claimed_character in action_player.cards

        if has_character:  # Challenge fails
            # Challenger loses a card
            self._lose_card(challenger_id)

            # Player with the character returns it to the deck and draws a new one
            card_index = action_player.cards.index(claimed_character)
            self.game_state.deck.append(action_player.cards.pop(card_index))
            random.shuffle(self.game_state.deck)
            action_player.cards.append(self.game_state.deck.pop())

            # Execute the action
            result = self._execute_action(action_player_id, action)

            self.challenge_window_open = False
            self.pending_action = None

            return {
                "success": True,
                "message": f"Challenge failed! {action_player.name} had the {claimed_character}. {challenger.name} loses a card.",
                "action_result": result,
            }
        else:  # Challenge succeeds
            # Player being challenged loses a card
            self._lose_card(action_player_id)

            self.challenge_window_open = False
            self.pending_action = None

            # Move to next player if the current player lost
            if not action_player.is_alive:
                self.game_state.next_player()

            # Check if game is over
            if self.game_state.is_game_over():
                self.game_state.status = GameStatus.FINISHED
                return {
                    "success": True,
                    "message": f"Challenge successful! {action_player.name} did not have the {claimed_character} and loses a card.",
                    "game_over": True,
                }

            return {
                "success": True,
                "message": f"Challenge successful! {action_player.name} did not have the {claimed_character} and loses a card.",
            }

    def resolve_counteraction(
        self, counter_player_id: str, counter_action: Dict
    ) -> Dict:
        """Resolve a counteraction"""
        if not self.pending_action:
            return {"success": False, "message": "No pending action to counter"}

        action_player_id = self.pending_action["player_id"]
        action_player = next(
            (p for p in self.game_state.players if p.id == action_player_id), None
        )
        counter_player = next(
            (p for p in self.game_state.players if p.id == counter_player_id), None
        )

        if not action_player or not counter_player:
            return {"success": False, "message": "Player not found"}

        action = self.pending_action["action"]
        action_type = action.get("action_type")
        counter_type = counter_action.get("counter_type")

        # Validate the counteraction
        if (
            action_type == ActionType.FOREIGN_AID
            and counter_type == ActionType.BLOCK_FOREIGN_AID
        ):
            # Duke blocks foreign aid
            self.pending_counteraction = {
                "player_id": counter_player_id,
                "counter_action": counter_action,
                "claimed_character": "duke",
            }

            # Open challenge window for the counteraction
            self.challenge_window_open = True
            self.counteraction_window_open = False

            return {
                "success": True,
                "message": f"{counter_player.name} is blocking foreign aid with Duke",
                "state": "challenge_window",
            }

        elif (
            action_type == ActionType.ASSASSINATE
            and counter_type == ActionType.BLOCK_ASSASSINATION
        ):
            # Contessa blocks assassination
            self.pending_counteraction = {
                "player_id": counter_player_id,
                "counter_action": counter_action,
                "claimed_character": "contessa",
            }

            # Open challenge window for the counteraction
            self.challenge_window_open = True
            self.counteraction_window_open = False

            return {
                "success": True,
                "message": f"{counter_player.name} is blocking assassination with Contessa",
                "state": "challenge_window",
            }

        elif (
            action_type == ActionType.STEAL
            and counter_type == ActionType.BLOCK_STEALING
        ):
            # Captain or Ambassador blocks stealing
            claimed_character = counter_action.get("character", "captain")
            if claimed_character not in ["captain", "ambassador"]:
                return {
                    "success": False,
                    "message": "Invalid character for blocking stealing",
                }

            self.pending_counteraction = {
                "player_id": counter_player_id,
                "counter_action": counter_action,
                "claimed_character": claimed_character,
            }

            # Open challenge window for the counteraction
            self.challenge_window_open = True
            self.counteraction_window_open = False

            return {
                "success": True,
                "message": f"{counter_player.name} is blocking stealing with {claimed_character.capitalize()}",
                "state": "challenge_window",
            }

        return {"success": False, "message": "Invalid counteraction"}

    def resolve_counteraction_challenge(
        self, challenger_id: str, challenge_successful: bool
    ) -> Dict:
        """Resolve a challenge to a counteraction"""
        if not self.pending_counteraction:
            return {
                "success": False,
                "message": "No pending counteraction to challenge",
            }

        counter_player_id = self.pending_counteraction["player_id"]
        counter_player = next(
            (p for p in self.game_state.players if p.id == counter_player_id), None
        )
        challenger = next(
            (p for p in self.game_state.players if p.id == challenger_id), None
        )

        if not counter_player or not challenger:
            return {"success": False, "message": "Player not found"}

        claimed_character = self.pending_counteraction["claimed_character"]

        # Check if the counter player has the claimed character
        has_character = claimed_character in counter_player.cards

        if has_character:  # Challenge fails
            # Challenger loses a card
            self._lose_card(challenger_id)

            # Player with the character returns it to the deck and draws a new one
            card_index = counter_player.cards.index(claimed_character)
            self.game_state.deck.append(counter_player.cards.pop(card_index))
            random.shuffle(self.game_state.deck)
            counter_player.cards.append(self.game_state.deck.pop())

            # Counteraction succeeds, original action is blocked
            action_player_id = self.pending_action["player_id"]
            action_player = next(
                (p for p in self.game_state.players if p.id == action_player_id), None
            )

            # If it was an assassination, return the coins
            if (
                self.pending_action["action"].get("action_type")
                == ActionType.ASSASSINATE
            ):
                action_player.coins += ASSASSINATE_COST

            self.challenge_window_open = False
            self.pending_action = None
            self.pending_counteraction = None

            # Move to next player
            self.game_state.next_player()

            return {
                "success": True,
                "message": f"Challenge failed! {counter_player.name} had the {claimed_character}. {challenger.name} loses a card. Action blocked.",
            }
        else:  # Challenge succeeds
            # Counter player loses a card
            self._lose_card(counter_player_id)

            # Original action proceeds
            action_player_id = self.pending_action["player_id"]
            action = self.pending_action["action"]
            result = self._execute_action(action_player_id, action)

            self.challenge_window_open = False
            self.pending_action = None
            self.pending_counteraction = None

            # Check if game is over
            if self.game_state.is_game_over():
                self.game_state.status = GameStatus.FINISHED
                return {
                    "success": True,
                    "message": f"Challenge successful! {counter_player.name} did not have the {claimed_character} and loses a card. Original action proceeds.",
                    "action_result": result,
                    "game_over": True,
                }

            return {
                "success": True,
                "message": f"Challenge successful! {counter_player.name} did not have the {claimed_character} and loses a card. Original action proceeds.",
                "action_result": result,
            }

    def _execute_action(self, player_id: str, action: Dict) -> Dict:
        """Execute an action after challenges/counteractions are resolved"""
        action_type = action.get("action_type")
        player = next((p for p in self.game_state.players if p.id == player_id), None)

        if not player:
            return {"success": False, "message": "Player not found"}

        if action_type == ActionType.TAX:
            # Duke takes 3 coins
            player.coins += 3
            self.game_state.last_action = {
                "type": ActionType.TAX,
                "player": player.name,
            }
            self.game_state.next_player()
            return {
                "success": True,
                "message": f"Player {player.name} took tax (3 coins)",
            }

        elif action_type == ActionType.FOREIGN_AID:
            # Take 2 coins
            player.coins += 2
            self.game_state.last_action = {
                "type": ActionType.FOREIGN_AID,
                "player": player.name,
            }
            self.game_state.next_player()
            return {
                "success": True,
                "message": f"Player {player.name} took foreign aid (2 coins)",
            }

        elif action_type == ActionType.ASSASSINATE:
            target_id = action.get("target_id")
            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )

            if not target:
                return {"success": False, "message": "Target player not found"}

            # Deduct coins
            player.coins -= ASSASSINATE_COST

            # Target loses a card
            card_index = action.get("card_index", 0)
            self._lose_card(target_id, card_index)

            self.game_state.last_action = {
                "type": ActionType.ASSASSINATE,
                "player": player.name,
                "target": target.name,
            }

            # Check if game is over
            if self.game_state.is_game_over():
                self.game_state.status = GameStatus.FINISHED
                return {
                    "success": True,
                    "message": f"Player {player.name} assassinated {target.name}",
                    "game_over": True,
                }

            self.game_state.next_player()
            return {
                "success": True,
                "message": f"Player {player.name} assassinated {target.name}",
            }

        elif action_type == ActionType.STEAL:
            target_id = action.get("target_id")
            target = next(
                (p for p in self.game_state.players if p.id == target_id), None
            )

            if not target:
                return {"success": False, "message": "Target player not found"}

            # Steal up to 2 coins
            steal_amount = min(2, target.coins)
            target.coins -= steal_amount
            player.coins += steal_amount

            self.game_state.last_action = {
                "type": ActionType.STEAL,
                "player": player.name,
                "target": target.name,
                "amount": steal_amount,
            }

            self.game_state.next_player()
            return {
                "success": True,
                "message": f"Player {player.name} stole {steal_amount} coins from {target.name}",
            }

        elif action_type == ActionType.EXCHANGE:
            # Draw 2 cards from the deck
            if len(self.game_state.deck) < 2:
                return {"success": False, "message": "Not enough cards in the deck"}

            drawn_cards = [self.game_state.deck.pop() for _ in range(2)]

            # Add to player's hand temporarily
            all_cards = player.cards + drawn_cards

            # Player will need to choose which cards to keep in a separate action
            self.game_state.last_action = {
                "type": ActionType.EXCHANGE,
                "player": player.name,
                "cards": all_cards,
            }

            return {
                "success": True,
                "message": f"Player {player.name} is exchanging cards",
                "state": "exchange",
                "cards": all_cards,
            }

        return {"success": False, "message": "Invalid action"}

    def complete_exchange(self, player_id: str, kept_indices: List[int]) -> Dict:
        """Complete an exchange action by selecting which cards to keep"""
        player = next((p for p in self.game_state.players if p.id == player_id), None)

        if not player:
            return {"success": False, "message": "Player not found"}

        if (
            not self.game_state.last_action
            or self.game_state.last_action.get("type") != ActionType.EXCHANGE
        ):
            return {"success": False, "message": "No exchange action in progress"}

        all_cards = self.game_state.last_action.get("cards", [])

        if len(kept_indices) != len(player.cards):
            return {
                "success": False,
                "message": f"You must keep exactly {len(player.cards)} cards",
            }

        if max(kept_indices) >= len(all_cards) or min(kept_indices) < 0:
            return {"success": False, "message": "Invalid card indices"}

        # Get the cards the player wants to keep
        kept_cards = [all_cards[i] for i in kept_indices]

        # Return the rest to the deck
        returned_cards = [
            card for i, card in enumerate(all_cards) if i not in kept_indices
        ]
        self.game_state.deck.extend(returned_cards)
        random.shuffle(self.game_state.deck)

        # Update player's cards
        player.cards = kept_cards

        self.game_state.next_player()
        return {"success": True, "message": f"Player {player.name} completed exchange"}

    def _lose_card(self, player_id: str, card_index: int = 0) -> None:
        """Make a player lose a card"""
        player = next((p for p in self.game_state.players if p.id == player_id), None)

        if not player or not player.cards:
            return

        if card_index >= len(player.cards):
            card_index = 0

        # Move card from hand to revealed cards
        revealed_card = player.cards.pop(card_index)
        player.revealed_cards.append(revealed_card)

        # Check if player is eliminated
        if not player.cards:
            player.is_alive = False
