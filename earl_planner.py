import uuid
import time
import logging
from typing import List, Dict, Any, Optional

from hermes_state import SessionDB

logger = logging.getLogger("earl_planner")

class PlanManager:
    """Persistent plan storage and tracking for Earl Agent OS."""

    def __init__(self, db: SessionDB):
        self.db = db

    def _get_connection(self):
        # We use the internal _get_connection from SessionDB
        return self.db._get_connection()

    def create_plan(self, session_id: str, title: str, steps: List[str]) -> str:
        """Creates a new plan and stores it in the database."""
        plan_id = str(uuid.uuid4())
        now = time.time()
        
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO plans (id, session_id, title, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (plan_id, session_id, title, 'draft', now, now)
            )
            for i, step_desc in enumerate(steps, start=1):
                step_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO plan_steps (id, plan_id, step_number, description, status, started_at, completed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (step_id, plan_id, i, step_desc, 'pending', None, None)
                )
        return plan_id

    def approve_plan(self, plan_id: str):
        """Marks a plan as approved and executing."""
        with self._get_connection() as conn:
            conn.execute("UPDATE plans SET status = 'executing', updated_at = ? WHERE id = ?", (time.time(), plan_id))

    def update_step_status(self, plan_id: str, step_number: int, status: str, result: str = None):
        """Updates the status of a specific plan step."""
        now = time.time()
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE plan_steps SET status = ?, result = ?, completed_at = ? WHERE plan_id = ? AND step_number = ?",
                (status, result, now if status in ('done', 'failed', 'skipped') else None, plan_id, step_number)
            )
            conn.execute("UPDATE plans SET updated_at = ? WHERE id = ?", (now, plan_id))

    def get_active_plan(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the active (executing or draft) plan for a session."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, status FROM plans WHERE session_id = ? AND status IN ('draft', 'executing') ORDER BY created_at DESC LIMIT 1",
                (session_id,)
            )
            plan_row = cursor.fetchone()
            if not plan_row:
                return None
                
            plan_id, title, status = plan_row
            
            cursor = conn.execute(
                "SELECT id, step_number, description, status, result FROM plan_steps WHERE plan_id = ? ORDER BY step_number ASC",
                (plan_id,)
            )
            steps = [
                {
                    "id": row[0],
                    "step_number": row[1],
                    "description": row[2],
                    "status": row[3],
                    "result": row[4]
                }
                for row in cursor.fetchall()
            ]
            
            return {
                "id": plan_id,
                "title": title,
                "status": status,
                "steps": steps
            }

    def complete_plan(self, plan_id: str, success: bool = True):
        """Marks the plan as completed or failed."""
        status = 'completed' if success else 'failed'
        with self._get_connection() as conn:
            conn.execute("UPDATE plans SET status = ?, updated_at = ? WHERE id = ?", (status, time.time(), plan_id))

    def get_plan_context(self, session_id: str) -> str:
        """Generates a markdown string of the current plan to inject into the system prompt."""
        plan = self.get_active_plan(session_id)
        if not plan:
            return ""
            
        output = [f"\n═══════════════════════════════════"]
        output.append(f"ACTIVE PLAN: {plan['title']} ({plan['status'].upper()})")
        output.append(f"═══════════════════════════════════")
        
        for step in plan['steps']:
            status_icon = "⬜"
            if step['status'] == 'done':
                status_icon = "✅"
            elif step['status'] == 'active':
                status_icon = "🔄"
            elif step['status'] == 'failed':
                status_icon = "❌"
            elif step['status'] == 'skipped':
                status_icon = "⏭️"
                
            output.append(f"{status_icon} {step['step_number']}. {step['description']}")
            
        output.append(f"═══════════════════════════════════\n")
        return "\n".join(output)

