import re
from enum import Enum
from typing import Dict, Any, List

class ModelTier(str, Enum):
    FRONTIER = "frontier"
    LOCAL_STRONG = "local"
    LOCAL_FAST = "fast"

class TaskRouter:
    """
    Intelligent task routing for Earl Agent OS.
    Analyzes the complexity of a task and routes it to the appropriate model tier
    based on predefined heuristics and profile configurations.
    """
    
    def __init__(self, config: Dict[str, Any], default_tier: str = "frontier"):
        self.config = config.get("routing", {})
        self.enabled = self.config.get("enabled", True)
        self.default_tier = ModelTier(self.config.get("default_tier", default_tier))
        self._compile_rules()

    def _compile_rules(self):
        """Compiles regex patterns for classification rules."""
        self.rules = []
        for rule in self.config.get("rules", []):
            if "pattern" in rule:
                self.rules.append({
                    "type": "pattern",
                    "pattern": re.compile(rule["pattern"], re.IGNORECASE),
                    "tier": ModelTier(rule["tier"])
                })
            elif "task_type" in rule:
                self.rules.append({
                    "type": "task_type",
                    "task_type": rule["task_type"],
                    "tier": ModelTier(rule["tier"])
                })

    def classify(self, message: str, profile_name: str = "sun-tzu", context_length: int = 0) -> ModelTier:
        """
        Classifies the incoming task and returns the recommended ModelTier.
        """
        if not self.enabled:
            return self.default_tier

        # 1. Profile overrides
        profile_defaults = self.config.get("profile_defaults", {})
        if profile_name in profile_defaults:
            # If the profile strictly requires a tier, return it immediately
            return ModelTier(profile_defaults[profile_name])

        # 2. Complexity heuristics
        # Very long context implies complex reasoning or large data processing
        if context_length > 10000:
            return ModelTier.FRONTIER
            
        # 3. Rule matching
        for rule in self.rules:
            if rule["type"] == "pattern" and rule["pattern"].search(message):
                return rule["tier"]
                
        return self.default_tier

    def get_model_config(self, tier: ModelTier) -> Dict[str, Any]:
        """Returns the provider and model configuration for the given tier."""
        tier_config = self.config.get(tier.value, {})
        if not tier_config:
            # Fallback if tier is not configured
            return {"provider": "openai", "model": "gpt-4o"}
            
        return {
            "provider": tier_config.get("provider", "openai"),
            "model": tier_config.get("model", "gpt-4o"),
            "base_url": tier_config.get("base_url"),
            "api_key": tier_config.get("api_key"),
            "api_mode": tier_config.get("api_mode", "chat_completions"),
            "max_context": tier_config.get("max_context", 128000)
        }

    def inject_router_config(self, agent: Any, tier: ModelTier):
        """Injects the selected model configuration into the agent instance."""
        model_cfg = self.get_model_config(tier)
        agent.provider = model_cfg["provider"]
        agent.model = model_cfg["model"]
        if model_cfg["base_url"]:
            agent.base_url = model_cfg["base_url"]
        if model_cfg["api_mode"]:
            agent.api_mode = model_cfg["api_mode"]
        
        # We don't overwrite api_key here directly unless necessary, 
        # as the provider adapters usually fetch it from env or keychain.
