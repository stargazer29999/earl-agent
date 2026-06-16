import subprocess
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("earl_executor")

class ExecutionWatchdog:
    """Watchdog for command execution in Earl Agent OS.
    
    Provides timeouts, validation, and side-effect checking for terminal commands.
    """
    
    def __init__(self, default_timeout: int = 120):
        self.default_timeout = default_timeout

    def execute_with_watchdog(self, command: str, cwd: str = None, timeout: int = None) -> Dict[str, Any]:
        """Executes a command with a strict timeout and captures all output."""
        eff_timeout = timeout or self.default_timeout
        
        start_time = time.time()
        try:
            # We use shell=True to allow shell builtins, pipes, etc.
            result = subprocess.run(
                command,
                cwd=cwd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=eff_timeout
            )
            elapsed = time.time() - start_time
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "elapsed": elapsed,
                "error": None
            }
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            # Return a clear error format for the model to see
            return {
                "success": False,
                "stdout": e.stdout.decode('utf-8', errors='replace') if e.stdout else "",
                "stderr": e.stderr.decode('utf-8', errors='replace') if e.stderr else "",
                "exit_code": -1,
                "elapsed": elapsed,
                "error": f"Command timed out after {eff_timeout} seconds."
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -2,
                "elapsed": elapsed,
                "error": str(e)
            }

    def validate_side_effects(self, expected_file: str = None) -> bool:
        """Validates if expected side-effects (like file creation) occurred."""
        import os
        if expected_file:
            return os.path.exists(expected_file)
        return True

