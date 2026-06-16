import logging
from typing import Dict, Any, List

logger = logging.getLogger("earl_orchestrator")

class Orchestrator:
    """
    Acts as the middleman between the User and the specialized Earl Agent profiles.
    
    Responsibilities:
    1. Receive user requests.
    2. Consult Sun Tzu (Strategist) to formulate a plan if it's a complex goal.
    3. Delegate execution to specific profiles (Archimedes, Augustus, etc.).
    4. Compile the results and respond to the user.
    """
    
    def __init__(self, agent_factory, state_db):
        self.agent_factory = agent_factory
        self.state_db = state_db
        from earl_profiles import ProfileManager
        self.profile_manager = ProfileManager()
        
    def handle_request(self, user_message: str, current_session_id: str) -> str:
        """
        Main entry point for user requests handled by the orchestrator.
        """
        logger.info(f"Orchestrator received request for session {current_session_id}")
        
        # 1. Ask Sun Tzu to evaluate the request and create a plan
        sun_tzu = self._spawn_agent("sun-tzu", current_session_id)
        
        # We pass a specific system prompt to Sun Tzu for orchestration
        orchestration_prompt = (
            "You are the Orchestrator. The user has made a request. "
            "Analyze it. If it is simple, fulfill it. "
            "If it requires a plan, create one and then delegate the tasks to the appropriate profiles "
            "(Augustus, Archimedes, Aristotle, Medici). "
            "You have tools to spawn agents and delegate tasks."
        )
        
        # For this PoC, we let Sun Tzu handle the conversation loop directly,
        # assuming Sun Tzu has been given the `delegate_task` tool.
        # Ideally we'd hook into the existing conversation loop.
        
        result = sun_tzu.chat(user_message)
        return result
        
    def _spawn_agent(self, profile_name: str, session_id: str):
        """Spawns an agent instance with the specified profile."""
        # Create a new agent instance using the factory (e.g., run_agent.main logic)
        agent = self.agent_factory()
        agent.session_id = session_id
        
        # Apply the profile
        self.profile_manager.apply_profile(agent, profile_name)
        return agent
