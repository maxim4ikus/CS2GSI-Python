"""Steam utility functions."""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_game_path(app_id: int = 730) -> Optional[str]:
    """Get Counter-Strike 2 installation path.
    
    Args:
        app_id: Steam app ID (730 for CS2)
        
    Returns:
        Path to the game directory, or None if not found
    """
    try:
        # Try common Steam paths on Windows
        common_paths = [
            f"C:\\Program Files\\Steam\\steamapps\\common\\Counter-Strike Global Offensive",
            f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive",
            os.path.expanduser("~\\AppData\\LocalLow\\Valve\\Counter-Strike 2\\"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found CS2 installation at: {path}")
                return path
        
        logger.warning("Counter-Strike 2 installation not found")
        return None
    except Exception as e:
        logger.error(f"Error getting game path: {e}")
        return None
