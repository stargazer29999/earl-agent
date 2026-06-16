import argparse
import sys
import os
import uuid
import logging
from run_agent import AIAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("earl_cron")

def run_cron_job(profile_name: str, task_description: str):
    """
    Runs a specific Earl Agent profile to execute a scheduled task autonomously.
    """
    logger.info(f"Starting cron job for profile: {profile_name}")
    logger.info(f"Task: {task_description}")

    from earl_profiles import ProfileManager
    manager = ProfileManager()
    
    if not manager.get_profile(profile_name):
        logger.error(f"Profile {profile_name} not found. Cannot run cron job.")
        sys.exit(1)

    # Instantiate the agent
    # We use a default fast/local model for cron jobs unless overridden by profile
    agent = AIAgent(
        model="gpt-4o", # Fallback, should be routed
        max_iterations=5,
        save_trajectories=True
    )
    
    # Apply profile
    manager.apply_profile(agent, profile_name)
    
    # Generate unique session ID for the cron job
    agent.session_id = f"cron_{profile_name}_{uuid.uuid4().hex[:8]}"
    
    logger.info("Executing task...")
    result = agent.run_conversation(task_description)
    
    logger.info(f"Task completed: {result['completed']}")
    logger.info(f"Final Response: {result['final_response']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Earl Agent Cron Runner")
    parser.add_argument("--profile", required=True, help="Profile to execute the task (e.g., augustus)")
    parser.add_argument("--task", required=True, help="Description of the task to execute")
    
    args = parser.parse_args()
    run_cron_job(args.profile, args.task)
