#!/usr/bin/env python3
\"\"\"Example usage of the CS2 GSI library.\"\"\"

import time
from cs2gsi import GameStateListener


def main():
    \"\"\"Run the example.\"\"\"
    # Create listener on port 3000
    gsl = GameStateListener(3000)
    
    # Generate GSI config file
    if gsl.generate_gsi_config_file('Example'):
        print('✓ GSI config file generated successfully')
    else:
        print('✗ Failed to generate GSI config file')
    
    # Subscribe to events
    @gsl.on_new_game_state
    def on_new_game_state(game_state):
        if game_state.is_valid():
            print(f\"Map: {game_state.map.name}, \"
                  f\"Player: {game_state.player.name}, \"
                  f\"Health: {game_state.player.state.health}, \"
                  f\"Money: {game_state.player.state.money}\")
    
    @gsl.on_player_took_damage
    def on_player_took_damage(event):
        damage = event['previous'] - event['new']
        print(f\"💥 {event['player'].name} took {damage} damage! \"
              f\"Health: {event['new']}\")
    
    @gsl.on_player_died
    def on_player_died(event):
        print(f\"💀 {event['player'].name} died!\")
    
    @gsl.on_bomb_planted
    def on_bomb_planted(bomb):
        print(f\"💣 Bomb planted!\")
    
    @gsl.on_bomb_defused
    def on_bomb_defused(bomb):
        print(f\"✓ Bomb defused!\")
    
    # Start listening
    if gsl.start():
        print(f\"✓ Listening on {gsl.uri}\")
        print(\"Waiting for game state updates... (Press Ctrl+C to quit)\\n\")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(\"\\nShutting down...\")
            gsl.stop()
            print(\"✓ Stopped\")
    else:
        print(\"✗ Failed to start listener\")


if __name__ == '__main__':
    main()
