import json
import logging
from typing import Optional, Dict, Any
import uuid

from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

def handle_delegate_to_profile(
    profile_name: str,
    task: str,
    parent_agent=None,
) -> str:
    """Spawns a sub-agent with the specified profile to execute a task."""
    if parent_agent is None:
        return tool_error("parent_agent required")

    logger.info(f"Delegating task to profile: {profile_name}")
    from earl_profiles import ProfileManager
    from run_agent import AIAgent
    manager = ProfileManager()
    profile = manager.get_profile(profile_name)
    if not profile:
        return tool_error(f"Profile '{profile_name}' not found. Available: {list(manager.profiles.keys())}")

    # Initialize subagent inheriting parent's base configuration, but with fresh context
    agent = AIAgent(
        model=parent_agent.model,
        max_iterations=parent_agent.max_iterations,
        save_trajectories=parent_agent.save_trajectories,
    )
    
    # Apply specific profile identity and toolsets
    manager.apply_profile(agent, profile_name)
    
    # Generate unique session ID for the subagent run
    agent.session_id = f"subagent_{profile_name}_{uuid.uuid4().hex[:8]}"
    
    # Run conversation synchronously
    result = agent.run_conversation(task)
    
    # Return formatted JSON result back to the orchestrator (Sun Tzu)
    return json.dumps({
        "profile": profile_name,
        "completed": result["completed"],
        "api_calls": result["api_calls"],
        "final_response": result["final_response"]
    })

registry.register(
    name="delegate_to_profile",
    toolset="delegation",
    schema={
        "type": "function",
        "function": {
            "name": "delegate_to_profile",
            "description": "Delegates a specific task to a specialized profile agent (e.g., archimedes, aristotle). This agent runs autonomously and returns the final result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_name": {
                        "type": "string",
                        "description": "The name of the profile to use (e.g., 'aristotle', 'archimedes', 'medici', 'augustus').",
                    },
                    "task": {
                        "type": "string",
                        "description": "The detailed task or goal for the profile to accomplish.",
                    }
                },
                "required": ["profile_name", "task"],
            },
        },
    },
    handler=handle_delegate_to_profile,
    check_fn=None,
    requires_env=[],
    is_async=False,
    description="Delegates a specific task to a specialized profile agent.",
    emoji="👥",
)
