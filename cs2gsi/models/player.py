"""Player model."""

from typing import Optional, Dict, Any, List
from enum import Enum


class PlayerTeam(Enum):
    """Player team enumeration."""
    Undefined = -1
    Spectator = 1
    T = 2
    CT = 3


class PlayerActivity(Enum):
    """Player activity enumeration."""
    Undefined = -1
    Playing = 0
    Menu = 1
    TextInput = 2


class PlayerState:
    """Player state information."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize PlayerState."""
        data = data or {}
        
        self.health = data.get('health', 0)
        self.armor = data.get('armor', 0)
        self.has_helmet = data.get('helmet', False)
        self.has_defuse_kit = data.get('defusekit', False)
        self.flash_amount = data.get('flashed', 0)
        self.smoked_amount = data.get('smoked', 0)
        self.burning_amount = data.get('burning', 0)
        self.money = data.get('money', 0)
        self.round_kills = data.get('round_kills', 0)
        self.round_hs_kills = data.get('round_killhs', 0)
        self.round_total_damage = data.get('round_totaldmg', 0)
        self.equipment_value = data.get('equip_value', 0)


class Weapon:
    """Weapon information."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize Weapon."""
        data = data or {}
        
        self.name = data.get('name', '')
        self.paintkit = data.get('paintkit', '')
        self.weapon_type = data.get('type', '')
        self.ammo_clip = data.get('ammo_clip', 0)
        self.ammo_clip_max = data.get('ammo_clip_max', 0)
        self.ammo_reserve = data.get('ammo_reserve', 0)
        self.state = data.get('state', '')


class MatchStats:
    """Match statistics."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize MatchStats."""
        data = data or {}
        
        self.kills = data.get('kills', 0)
        self.assists = data.get('assists', 0)
        self.deaths = data.get('deaths', 0)
        self.mvps = data.get('mvps', 0)
        self.score = data.get('score', 0)


class Vector3D:
    """3D vector position."""

    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        """Initialize Vector3D."""
        self.x = x
        self.y = y
        self.z = z


class Player:
    """Player information."""

    def __init__(self, data: Optional[Dict[str, Any]] = None, steam_id: str = ''):
        """Initialize Player."""
        data = data or {}
        
        self.steam_id = data.get('steamid', steam_id)
        self.name = data.get('name', '')
        self.clan = data.get('clan', '')
        self.xp_overload_level = data.get('xpoverload', 0)
        self.observer_slot = data.get('observer_slot', 0)
        
        # Parse team
        team_str = data.get('team', 'unassigned')
        if team_str == 'T':
            self.team = PlayerTeam.T
        elif team_str == 'CT':
            self.team = PlayerTeam.CT
        elif team_str == 'spectator':
            self.team = PlayerTeam.Spectator
        else:
            self.team = PlayerTeam.Undefined
        
        # Parse activity
        activity_str = data.get('activity', 'undefined')
        if activity_str == 'playing':
            self.activity = PlayerActivity.Playing
        elif activity_str == 'menu':
            self.activity = PlayerActivity.Menu
        elif activity_str == 'textinput':
            self.activity = PlayerActivity.TextInput
        else:
            self.activity = PlayerActivity.Undefined
        
        self.state = PlayerState(data.get('state', {}))
        
        # Parse weapons
        self.weapons: List[Weapon] = []
        weapons_data = data.get('weapons', {})
        for key, value in weapons_data.items():
            if key.startswith('weapon_'):
                self.weapons.append(Weapon(value))
        
        self.match_stats = MatchStats(data.get('match_stats', {}))
        self.spectation_target = data.get('spectarget', '')
        
        # Parse position
        position_str = data.get('position', '0, 0, 0')
        self.position = self._parse_vector3d(position_str)
        
        # Parse forward direction
        forward_str = data.get('forward', '0, 0, 0')
        self.forward_direction = self._parse_vector3d(forward_str)
    
    @staticmethod
    def _parse_vector3d(pos_str: str) -> Vector3D:
        """Parse a vector3d from string."""
        try:
            coords = [float(x.strip()) for x in pos_str.split(',')]
            if len(coords) >= 3:
                return Vector3D(coords[0], coords[1], coords[2])
        except (ValueError, IndexError):
            pass
        return Vector3D()
    
    def is_valid(self) -> bool:
        """Check if player is valid."""
        return bool(self.steam_id)
