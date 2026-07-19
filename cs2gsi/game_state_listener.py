"""Main Game State Listener class."""

import json
import logging
import os
import re
import threading
from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from typing import Callable, Optional

from .models.game_state import GameState
from .event_dispatcher import EventDispatcher
from .utils.steam_utils import get_game_path

logger = logging.getLogger(__name__)


class GameStateListener:
    \"\"\"Listens for Game State Integration updates from Counter-Strike 2.\"\"\"

    def __init__(self, port: int = 3000, uri: Optional[str] = None):
        \"\"\"Initialize the Game State Listener.
        
        Args:
            port: Port to listen on (default 3000)
            uri: Custom URI to listen on (e.g., 'http://127.0.0.1:4000/')
        \"\"\"
        if uri:
            if not uri.endswith('/'):
                uri += '/'
            parsed = urlparse(uri)
            match = re.search(r':(\\d+)', uri)
            if not match:
                raise ValueError(f\"Invalid URI: {uri}\")
            self._port = int(match.group(1))
            self._uri = uri
        else:
            self._port = port
            self._uri = f\"http://localhost:{port}/\"
        
        self._is_running = False
        self._current_game_state = GameState()
        self._previous_game_state = GameState()
        self._dispatcher = EventDispatcher()
        self._server = None
        self._server_thread = None
        self._lock = threading.Lock()
    
    @property
    def port(self) -> int:
        \"\"\"Get the port being listened to.\"\"\"
        return self._port
    
    @property
    def uri(self) -> str:
        \"\"\"Get the URI being listened to.\"\"\"
        return self._uri
    
    @property
    def running(self) -> bool:
        \"\"\"Check if the listener is running.\"\"\"
        return self._is_running
    
    @property
    def current_game_state(self) -> GameState:
        \"\"\"Get the current game state.\"\"\"
        with self._lock:
            return self._current_game_state
    
    @property
    def previous_game_state(self) -> GameState:
        \"\"\"Get the previous game state.\"\"\"
        with self._lock:
            return self._previous_game_state
    
    def start(self) -> bool:
        \"\"\"Start listening for game state updates.
        
        Returns:
            True if started successfully, False otherwise
        \"\"\"
        if self._is_running:
            return False
        
        try:
            handler_class = self._create_request_handler()
            self._server = HTTPServer(('0.0.0.0', self._port), handler_class)
            self._is_running = True
            
            self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._server_thread.start()
            
            logger.info(f\"Game State Listener started on {self._uri}\")
            return True
        except Exception as e:
            logger.error(f\"Failed to start Game State Listener: {e}\")
            self._is_running = False
            return False
    
    def stop(self) -> None:
        \"\"\"Stop listening for game state updates.\"\"\"
        if self._is_running and self._server:
            self._is_running = False
            self._server.shutdown()
            self._server.server_close()
            logger.info(\"Game State Listener stopped\")
    
    def _create_request_handler(self):
        \"\"\"Create a request handler for the HTTP server.\"\"\"
        listener = self
        
        class GSIRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                
                try:
                    data = json.loads(body)
                    game_state = GameState(data)
                    
                    with listener._lock:
                        listener._previous_game_state = listener._current_game_state
                        listener._current_game_state = game_state
                    
                    # Dispatch events
                    listener._dispatcher.process_game_state(game_state, listener._previous_game_state)
                    
                except Exception as e:
                    logger.error(f\"Error processing game state: {e}\")
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{\"status\": \"ok\"}')
            
            def log_message(self, format, *args):
                \"\"\"Suppress default logging.\"\"\"
                pass
        
        return GSIRequestHandler
    
    def generate_gsi_config_file(self, name: str) -> bool:
        \"\"\"Generate a GSI configuration file.
        
        Args:
            name: Name of the integration
            
        Returns:
            True if successful, False otherwise
        \"\"\"
        try:
            # Get Counter-Strike 2 installation path
            game_path = get_game_path()
            if not game_path:
                logger.error(\"Could not find Counter-Strike 2 installation path\")
                return False
            
            config_dir = os.path.join(game_path, 'game', 'csgo', 'cfg')
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, f'gamestate_integration_{name}.cfg')
            
            config_content = f'''\"Example Integration Configuration\"
{{
    \"uri\"          \"{self._uri}\"
    \"timeout\"      \"5.0\"
    \"buffer\"       \"0.1\"
    \"throttle\"     \"0.1\"
    \"heartbeat\"    \"10.0\"
    \"data\"
    {{
        \"provider\"                  \"1\"
        \"tournamentdraft\"           \"1\"
        \"map\"                       \"1\"
        \"map_round_wins\"            \"1\"
        \"round\"                     \"1\"
        \"player_id\"                 \"1\"
        \"player_state\"              \"1\"
        \"player_weapons\"            \"1\"
        \"player_match_stats\"        \"1\"
        \"player_position\"           \"1\"
        \"phase_countdowns\"          \"1\"
        \"allplayers_id\"             \"1\"
        \"allplayers_state\"          \"1\"
        \"allplayers_match_stats\"    \"1\"
        \"allplayers_weapons\"        \"1\"
        \"allplayers_position\"       \"1\"
        \"allgrenades\"               \"1\"
        \"bomb\"                      \"1\"
    }}
}}
'''
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            logger.info(f\"GSI config file generated at {config_file}\")
            return True
        except Exception as e:
            logger.error(f\"Failed to generate GSI config file: {e}\")
            return False
    
    # Event decorators
    def on_new_game_state(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to new game state events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('new_game_state', func)
        return wrapper
    
    def on_player_took_damage(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to player damage events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('player_took_damage', func)
        return wrapper
    
    def on_player_died(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to player death events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('player_died', func)
        return wrapper
    
    def on_player_armor_changed(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to player armor change events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('player_armor_changed', func)
        return wrapper
    
    def on_player_money_changed(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to player money change events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('player_money_changed', func)
        return wrapper
    
    def on_bomb_planted(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to bomb planted events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('bomb_planted', func)
        return wrapper
    
    def on_bomb_planting(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to bomb planting events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('bomb_planting', func)
        return wrapper
    
    def on_bomb_defused(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to bomb defused events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('bomb_defused', func)
        return wrapper
    
    def on_bomb_defusing(self, func: Callable) -> Callable:
        \"\"\"Decorator to subscribe to bomb defusing events.\"\"\"
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        self._dispatcher.subscribe('bomb_defusing', func)
        return wrapper
