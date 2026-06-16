import os
import datetime
from jinja2 import Template

TEMPLATE_STR = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Stock Evaluation: {{ ticker }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f4f7f6; color: #333; }
        .container { max-width: 900px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .recommendation { font-size: 24px; font-weight: bold; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center; }
        .rec-Strong\\.Buy { background-color: #d4edda; color: #155724; }
        .rec-Buy { background-color: #cce5ff; color: #004085; }
        .rec-Hold { background-color: #fff3cd; color: #856404; }
        .rec-Sell { background-color: #f8d7da; color: #721c24; }
        .rec-Strong\\.Sell { background-color: #f8d7da; color: #721c24; border: 2px solid #f5c6cb; }
        .section { margin-top: 30px; }
        .section h2 { color: #34495e; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; }
        .news-item { margin-bottom: 10px; padding: 10px; background: #fdfdfd; border-left: 4px solid #3498db; }
        .notes { background: #e9ecef; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Stock Evaluation: {{ ticker }} ({{ date }})</h1>
        
        <div class="recommendation rec-{{ evaluation.recommendation | replace(' ', '.') }}">
            Recommendation: {{ evaluation.recommendation }}
        </div>
        
        <div class="section notes">
            <h2>Evaluation Notes</h2>
            <ul>
                {% for note in evaluation.notes %}
                <li>{{ note }}</li>
                {% endfor %}
                {% if not evaluation.notes %}
                <li>No specific notes generated.</li>
                {% endif %}
            </ul>
        </div>
        
        <div class="section">
            <h2>Fundamentals</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Current Price</td><td>${{ fundamentals.current_price }}</td></tr>
                <tr><td>P/E Ratio</td><td>{{ fundamentals.pe_ratio }}</td></tr>
                <tr><td>P/B Ratio</td><td>{{ fundamentals.pb_ratio }}</td></tr>
                <tr><td>Debt to Equity</td><td>{{ fundamentals.debt_to_equity }}</td></tr>
                <tr><td>Return on Equity</td><td>{{ fundamentals.roe }}</td></tr>
                <tr><td>52-Week Range</td><td>${{ fundamentals.fifty_two_week_low }} - ${{ fundamentals.fifty_two_week_high }}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>Recent News</h2>
            {% for item in news %}
            <div class="news-item">
                <a href="{{ item.link }}" target="_blank"><strong>{{ item.title }}</strong></a><br>
                <small>{{ item.published }}</small>
            </div>
            {% endfor %}
            {% if not news %}
            <p>No recent news found.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def generate_report(ticker: str, data: dict, evaluation: dict) -> str:
    """Generates the HTML report and saves it to STOCK evaluation directory."""
    out_dir = "STOCK evaluation"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    template = Template(TEMPLATE_STR)
    html_content = template.render(
        ticker=ticker,
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        fundamentals=data.get("fundamentals", {}),
        news=data.get("news", []),
        evaluation=evaluation
    )
    
    filename = f"{ticker}_evaluation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(out_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return filepath
