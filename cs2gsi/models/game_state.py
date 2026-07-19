"""GameState model."""

from typing import Optional, Dict, Any
from .player import Player
from .map import Map
from .round import Round
from .bomb import Bomb
from .auth import Auth
from .provider import Provider


class GameState:
    """Represents the complete game state from CS2 GSI."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize GameState.
        
        Args:
            data: Dictionary containing game state JSON data
        """
        data = data or {}
        
        self.auth = Auth(data.get('auth', {}))
        self.provider = Provider(data.get('provider', {}))
        self.map = Map(data.get('map', {}))
        self.round = Round(data.get('round', {}))
        self.player = Player(data.get('player', {}))
        self.bomb = Bomb(data.get('bomb', {}))
        self.all_players = data.get('allplayers', {})
        self.grenades = data.get('grenades', {})
        self.phase_countdowns = data.get('phase_countdowns', {})
        self.tournament_draft = data.get('tournamentdraft', {})
        
        # Previous state
        self._previously_data = data.get('previously', {})
    
    @property
    def previously(self) -> 'GameState':
        """Get the previous game state."""
        return GameState(self._previously_data)
    
    def is_valid(self) -> bool:
        """Check if the game state is valid."""
        return bool(self.provider.name)
