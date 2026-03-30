"""State persistence service for storing application state without a database.

This service provides a simple JSON-based persistence layer for storing
application state data like timestamps, counters, and other runtime data.
"""

import json
import logging
from xiaoai_media.logger import get_logger
from pathlib import Path
from typing import Any

_log = get_logger()


class StateService:
    """Service for persisting application state to JSON files."""

    def __init__(self, state_dir: Path | None = None):
        """Initialize the state service.
        
        Args:
            state_dir: Directory to store state files. Defaults to ~/.xiaoai_media/state
        """
        if state_dir is None:
            state_dir = Path.home() / ".xiaoai_media" / "state"
        
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self.state_dir / "app_state.json"
        self._state: dict[str, Any] = {}
        self._load_state()
    
    def _load_state(self):
        """Load state from disk."""
        if self._state_file.exists():
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
                _log.info("已加载状态文件: %s", self._state_file)
            except Exception as e:
                _log.error("加载状态文件失败: %s", e)
                self._state = {}
        else:
            _log.info("状态文件不存在，将创建新文件: %s", self._state_file)
            self._state = {}
    
    def _save_state(self):
        """Save state to disk."""
        try:
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            _log.debug("已保存状态到: %s", self._state_file)
        except Exception as e:
            _log.error("保存状态文件失败: %s", e)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state.
        
        Args:
            key: State key
            default: Default value if key doesn't exist
            
        Returns:
            The stored value or default
        """
        return self._state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a value in state and persist to disk.
        
        Args:
            key: State key
            value: Value to store (must be JSON serializable)
        """
        self._state[key] = value
        self._save_state()
    
    def delete(self, key: str):
        """Delete a key from state.
        
        Args:
            key: State key to delete
        """
        if key in self._state:
            del self._state[key]
            self._save_state()
    
    def get_all(self) -> dict[str, Any]:
        """Get all state data.
        
        Returns:
            Dictionary of all state data
        """
        return self._state.copy()
    
    def clear(self):
        """Clear all state data."""
        self._state = {}
        self._save_state()


# Global state service instance
_state_service: StateService | None = None


def get_state_service() -> StateService:
    """Get the global state service instance.
    
    Returns:
        StateService instance
    """
    global _state_service
    if _state_service is None:
        _state_service = StateService()
    return _state_service
