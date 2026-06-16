import os
import yaml
import logging
from typing import Dict, Any, List

logger = logging.getLogger("earl_profiles")

class ProfileManager:
    """Manages Earl Agent profiles (Souls)."""
    
    def __init__(self, profiles_dir: str = None):
        if not profiles_dir:
            from pathlib import Path
            self.profiles_dir = Path.home() / ".earl" / "profiles"
        else:
            from pathlib import Path
            self.profiles_dir = Path(profiles_dir)
            
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        """Loads all YAML profiles from the profiles directory."""
        if not self.profiles_dir.exists():
            return

        for filename in os.listdir(self.profiles_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                filepath = self.profiles_dir / filename
                try:
                    with open(filepath, 'r') as f:
                        profile_data = yaml.safe_load(f)
                        if "name" in profile_data:
                            self.profiles[profile_data["name"]] = profile_data
                except Exception as e:
                    logger.error(f"Failed to load profile {filename}: {e}")

    def get_profile(self, name: str) -> Dict[str, Any]:
        """Returns a profile by name."""
        return self.profiles.get(name)

    def apply_profile(self, agent: Any, profile_name: str):
        """Applies a profile to the given agent instance."""
        profile = self.get_profile(profile_name)
        if not profile:
            logger.warning(f"Profile {profile_name} not found. Using defaults.")
            return

        agent.log_prefix = f"[{profile.get('display_name', profile_name)}] "
        
        # Inject profile system prompt
        if "system_prompt" in profile:
            agent.load_soul_identity = False # Disable default Hermes soul
            agent._profile_system_prompt = profile["system_prompt"]
            
        # Register specific toolsets
        if "toolsets" in profile:
            # Rebuild tools based on profile toolsets
            from run_agent import _load_tools_from_toolsets
            # This is a naive injection; in reality, we'd need to re-init the tool manager
            try:
                tools = _load_tools_from_toolsets(profile["toolsets"].split(","))
                if tools:
                    agent.tools = tools
                    agent.valid_tool_names = {t["function"]["name"] for t in tools}
            except Exception as e:
                logger.error(f"Failed to load toolsets for profile {profile_name}: {e}")
