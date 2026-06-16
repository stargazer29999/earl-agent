"""
Stock Evaluation Plugin for Earl Agent.
Provides the `/stock-evaluation <ticker>` slash command to algorithmically
evaluate stocks based on fundamentals, technicals, and news sentiment,
generating an HTML report.
"""
import logging
from typing import Optional

from .data_fetcher import fetch_all_data
from .evaluator import evaluate_stock
from .report_generator import generate_report

logger = logging.getLogger(__name__)

_HELP_TEXT = """\
/stock-evaluation — Generate an algorithmic stock analysis report

Usage:
  /stock-evaluation <TICKER>

Example:
  /stock-evaluation AAPL
  /stock-evaluation TSLA
"""

def _handle_slash(raw_args: str) -> Optional[str]:
    argv = raw_args.strip().split()
    if not argv or argv[0] in {"help", "-h", "--help"}:
        return _HELP_TEXT

    ticker = argv[0].upper()
    return run_evaluation(ticker)

def run_evaluation(ticker: str) -> str:
    try:
        # 1. Fetch data
        data = fetch_all_data(ticker)
        if not data.get("valid"):
            return f"Failed to fetch data for ticker: {ticker}. Is the symbol correct?"
        
        # 2. Evaluate
        evaluation = evaluate_stock(data)
        
        # 3. Generate Report
        report_path = generate_report(ticker, data, evaluation)
        
        return f"✅ Stock evaluation complete for {ticker}.\nReport saved to: {report_path}"
    except Exception as e:
        logger.exception("Error during stock evaluation for %s", ticker)
        return f"❌ An error occurred while evaluating {ticker}: {e}"

def register(ctx) -> None:
    ctx.register_command(
        "stock-evaluation",
        handler=_handle_slash,
        description="Run algorithmic evaluation for a stock ticker.",
    )
