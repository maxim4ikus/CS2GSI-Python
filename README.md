
# Counter-Strike 2 GSI Python Library

A Python library to interface with the Game State Integration found in Counter-Strike 2.

## Features

- **HTTP Server**: Listens for Game State Integration updates from CS2
- **Event System**: Subscribe to specific game events (player damage, kills, bomb events, etc.)
- **Easy API**: Similar to the C# library but Pythonic
- **Config Generation**: Automatically generates GSI configuration files

## Installation

```bash
pip install cs2gsi
```

Or from source:

```bash
git clone https://github.com/maxim4ikus/CS2GSI-Python.git
cd CS2GSI-Python
pip install -e .
```

## Quick Start

```python
from cs2gsi import GameStateListener

# Create a listener on port 3000
gsl = GameStateListener(3000)

# Generate GSI config file
if gsl.generate_gsi_config_file('Example'):
    print('GSI config file generated successfully')

# Subscribe to events
@gsl.on_new_game_state
def on_new_game_state(game_state):
    print(f"Player health: {game_state.player.state.health}")

@gsl.on_player_took_damage
def on_player_took_damage(event):
    print(f"{event.player.name} took {event.previous - event.new} damage")

@gsl.on_bomb_planted
def on_bomb_planted(event):
    print("Bomb planted!")

# Start listening
if gsl.start():
    print("Listening on http://localhost:3000/")
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        gsl.stop()
```

## Game State Structure

```
game_state
├── auth
├── provider
├── map
│   ├── name
│   ├── phase
│   ├── round
│   ├── ct_statistics
│   └── t_statistics
├── round
│   ├── phase
│   ├── bomb_state
│   └── winning_team
├── player
│   ├── steam_id
│   ├── name
│   ├── team
│   ├── activity
│   ├── state
│   │   ├── health
│   │   ├── armor
│   │   ├── has_helmet
│   │   ├── money
│   │   ├── round_kills
│   │   └── ...
│   ├── weapons
│   ├── match_stats
│   └── position
├── all_players
├── bomb
├── grenades
└── previously (previous game state)
```

## Available Events

### Game State Events
- `on_new_game_state` - Fired on every game state update
- `on_game_event` - Fired on every game event

### Player Events
- `on_player_took_damage` - Player took damage
- `on_player_died` - Player died
- `on_player_respawned` - Player respawned
- `on_player_got_kill` - Player got a kill
- `on_player_health_changed` - Player health changed
- `on_player_armor_changed` - Player armor changed
- `on_player_money_changed` - Player money changed
- `on_player_weapons_picked_up` - Player picked up weapons
- `on_player_weapons_dropped` - Player dropped weapons
- `on_player_active_weapon_changed` - Player changed active weapon
- `on_player_team_changed` - Player switched teams
- `on_player_activity_changed` - Player activity changed

### Bomb Events
- `on_bomb_updated` - Bomb state updated
- `on_bomb_planted` - Bomb planted
- `on_bomb_planting` - Bomb is being planted
- `on_bomb_defused` - Bomb defused
- `on_bomb_defusing` - Bomb is being defused
- `on_bomb_picked_up` - Bomb picked up
- `on_bomb_dropped` - Bomb dropped
- `on_bomb_exploded` - Bomb exploded

### Map/Round Events
- `on_map_updated` - Map updated
- `on_round_started` - Round started
- `on_round_concluded` - Round concluded
- `on_gamemode_changed` - Game mode changed
- `on_team_score_changed` - Team score changed

### Player Connection Events
- `on_player_connected` - Player connected
- `on_player_disconnected` - Player disconnected

### Kill Feed Events
- `on_kill_feed` - Kill feed updated

## Advanced Usage

### Custom URI

```python
from cs2gsi import GameStateListener

# Listen on custom address
gsl = GameStateListener('http://127.0.0.1:4000/')
```

### Multiple Listeners

```python
from cs2gsi import GameStateListener

# Create multiple listeners on different ports
gsl1 = GameStateListener(3000)
gsl2 = GameStateListener(3001)

gsl1.start()
gsl2.start()
```

### Accessing Current Game State

```python
@gsl.on_new_game_state
def on_new_game_state(game_state):
    # Access all game state information
    print(f"Map: {game_state.map.name}")
    print(f"Round: {game_state.map.round}")
    print(f"Player health: {game_state.player.state.health}")
    print(f"Money: {game_state.player.state.money}")
    
    # Access all players (spectator only)
    for steam_id, player in game_state.all_players.items():
        print(f"{player.name}: {player.state.health} HP")
```

## Requirements

- Python 3.7+
- Windows (for GSI config file generation)

## Configuration File

The library automatically generates a GSI configuration file at:
```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg\gamestate_integration_<name>.cfg
```

You can also manually create the file with the following content:

```
"Example Integration Configuration"
{
    "uri"          "http://localhost:3000/"
    "timeout"      "5.0"
    "buffer"       "0.1"
    "throttle"     "0.1"
    "heartbeat"    "10.0"
    "data"
    {
        "provider"                  "1"
        "tournamentdraft"           "1"
        "map"                       "1"
        "map_round_wins"            "1"
        "round"                     "1"
        "player_id"                 "1"
        "player_state"              "1"
        "player_weapons"            "1"
        "player_match_stats"        "1"
        "player_position"           "1"
        "phase_countdowns"          "1"
        "allplayers_id"             "1"
        "allplayers_state"          "1"
        "allplayers_match_stats"    "1"
        "allplayers_weapons"        "1"
        "allplayers_position"       "1"
        "allgrenades"               "1"
        "bomb"                      "1"
    }
}
```

## License

GPL-3.0

## Acknowledgements

This library is a Python port of the [CounterStrike2GSI](https://github.com/antonpup/CounterStrike2GSI) C# library.
