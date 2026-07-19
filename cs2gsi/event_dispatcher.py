"""Event dispatcher for game events."""

import logging
from typing import Dict, Callable, List
from .models.game_state import GameState

logger = logging.getLogger(__name__)


class EventDispatcher:
    \"\"\"Dispatches game events to registered subscribers.\"\"\"

    def __init__(self):
        \"\"\"Initialize the dispatcher.\"\"\"
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        \"\"\"Subscribe to an event.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to invoke
        \"\"\"
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def dispatch(self, event_type: str, *args, **kwargs) -> None:
        \"\"\"Dispatch an event to all subscribers.
        
        Args:
            event_type: Type of event to dispatch
            args: Positional arguments to pass to callbacks
            kwargs: Keyword arguments to pass to callbacks
        \"\"\"
        if event_type not in self._subscribers:
            return
        
        for callback in self._subscribers[event_type]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f\"Error in event callback: {e}\")
    
    def process_game_state(self, current: GameState, previous: GameState) -> None:
        \"\"\"Process game state changes and dispatch events.
        
        Args:
            current: Current game state
            previous: Previous game state
        \"\"\"
        try:
            # Always dispatch new_game_state
            self.dispatch('new_game_state', current)
            
            if not current.is_valid():
                return
            
            # Check for player health changes
            if current.player.is_valid() and previous.player.is_valid():
                curr_health = current.player.state.health
                prev_health = previous.player.state.health
                
                if curr_health != prev_health:
                    if curr_health > prev_health:
                        # Health increased (healing)
                        pass
                    elif curr_health == 0 and prev_health > 0:
                        # Player died
                        event_data = {\n                            'player': current.player,\n                            'new': curr_health,\n                            'previous': prev_health\n                        }\n                        self.dispatch('player_died', event_data)
                    else:
                        # Player took damage
                        event_data = {\n                            'player': current.player,\n                            'new': curr_health,\n                            'previous': prev_health\n                        }\n                        self.dispatch('player_took_damage', event_data)
                
                # Check armor changes
                curr_armor = current.player.state.armor
                prev_armor = previous.player.state.armor
                if curr_armor != prev_armor:
                    self.dispatch('player_armor_changed', {\n                        'player': current.player,\n                        'new': curr_armor,\n                        'previous': prev_armor\n                    })
                
                # Check money changes
                curr_money = current.player.state.money
                prev_money = previous.player.state.money
                if curr_money != prev_money:
                    self.dispatch('player_money_changed', {\n                        'player': current.player,\n                        'new': curr_money,\n                        'previous': prev_money\n                    })
            
            # Check bomb state changes
            if current.bomb.state != previous.bomb.state:
                if current.bomb.state.name == 'Planted':
                    self.dispatch('bomb_planted', current.bomb)
                elif current.bomb.state.name == 'Planting':
                    self.dispatch('bomb_planting', current.bomb)
                elif current.bomb.state.name == 'Defused':
                    self.dispatch('bomb_defused', current.bomb)
                elif current.bomb.state.name == 'Defusing':
                    self.dispatch('bomb_defusing', current.bomb)
                elif current.bomb.state.name == 'Dropped':
                    self.dispatch('bomb_dropped', current.bomb)
            
            # Check map/round changes
            if current.map.round != previous.map.round:
                self.dispatch('round_changed', {\n                    'current_round': current.map.round,\n                    'previous_round': previous.map.round\n                })
        
        except Exception as e:
            logger.error(f\"Error processing game state: {e}\")
