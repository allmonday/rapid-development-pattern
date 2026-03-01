"""HTML report generation for benchmark results."""

import os
from datetime import datetime
from typing import List
from jinja2 import Template
from benchmark.metrics.collector import BenchmarkResult
from benchmark.visualization.charts import ChartGenerator


REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Benchmark Report: pydantic-resolve vs Strawberry GraphQL</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            font-size: 14px;
        }
        th, td {
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #2196F3;
            color: white;
            font-weight: 600;
        }
        tr:hover { background: #f9f9f9; }
        tr:nth-child(even) { background: #fafafa; }
        tr:nth-child(even):hover { background: #f5f5f5; }
        .better { color: #4CAF50; font-weight: bold; }
        .worse { color: #F44336; }
        .metric-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .metric-card {
            flex: 1;
            min-width: 200px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .metric-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
        }
        code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <h1>Benchmark Report</h1>
    <p><strong>pydantic-resolve</strong> vs <strong>Strawberry GraphQL</strong> Performance Comparison</p>
    <p>Generated: {{ timestamp }}</p>

    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="metric-group">
            <div class="metric-card">
                <h3>Total Tests</h3>
                <div class="value">{{ total_tests }}</div>
            </div>
            <div class="metric-card">
                <h3>Iterations per Test</h3>
                <div class="value">{{ iterations }}</div>
            </div>
            <div class="metric-card">
                <h3>pydantic-resolve Wins</h3>
                <div class="value">{{ pr_wins }}</div>
            </div>
            <div class="metric-card">
                <h3>Strawberry Wins</h3>
                <div class="value">{{ sw_wins }}</div>
            </div>
        </div>

        <h3>Test Environment</h3>
        <ul>
            <li>Database: SQLite + aiosqlite</li>
            <li>ORM: SQLAlchemy 2.0</li>
            <li>pydantic-resolve DataLoader: aiodataloader</li>
            <li>Strawberry DataLoader: strawberry.dataloader</li>
        </ul>
    </div>

    <h2>Response Time Comparison</h2>
    <div class="chart-container">
        <img src="charts/response_time_comparison.png" alt="Response Time Comparison">
    </div>

    <h2>Performance Ratio</h2>
    <div class="chart-container">
        <img src="charts/performance_ratio.png" alt="Performance Ratio">
        <p><em>Ratio &lt; 1 means pydantic-resolve is faster, &gt; 1 means Strawberry is faster</em></p>
    </div>

    <h2>Memory Usage</h2>
    <div class="chart-container">
        <img src="charts/memory_usage.png" alt="Memory Usage">
    </div>

    {% if has_concurrent %}
    <h2>Throughput vs Concurrency</h2>
    <div class="chart-container">
        <img src="charts/throughput.png" alt="Throughput">
    </div>
    {% endif %}

    <h2>Detailed Results</h2>
    <table>
        <thead>
            <tr>
                <th>Query</th>
                <th>Implementation</th>
                <th>Mean (ms)</th>
                <th>Median (ms)</th>
                <th>P95 (ms)</th>
                <th>P99 (ms)</th>
                <th>Memory (MB)</th>
            </tr>
        </thead>
        <tbody>
            {% for result in results %}
            <tr>
                <td><code>{{ result.query_name }}</code></td>
                <td>{{ result.implementation }}</td>
                <td>{{ "%.2f"|format(result.mean_time_ms) }}</td>
                <td>{{ "%.2f"|format(result.median_time_ms) }}</td>
                <td>{{ "%.2f"|format(result.p95_time_ms) }}</td>
                <td>{{ "%.2f"|format(result.p99_time_ms) }}</td>
                <td>{{ "%.2f"|format(result.mean_memory_mb) }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
        <p>Generated by pydantic-resolve GraphQL Benchmark Tool</p>
    </footer>
</body>
</html>
"""


class ReportGenerator:
    """Generate HTML benchmark reports."""

    def __init__(self, output_dir: str = "benchmark/results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.chart_gen = ChartGenerator(os.path.join(output_dir, "charts"))

    def generate(
        self,
        results: List[BenchmarkResult],
        iterations: int = 50,
        concurrency_levels: List[int] = None
    ) -> str:
        """Generate complete benchmark report."""
        if concurrency_levels is None:
            concurrency_levels = []

        # Generate charts
        print("Generating charts...")
        self.chart_gen.plot_response_time_comparison(results)
        self.chart_gen.plot_performance_ratio(results)
        self.chart_gen.plot_memory_usage(results)

        has_concurrent = any('concurrent' in r.query_name for r in results)
        if has_concurrent and concurrency_levels:
            self.chart_gen.plot_throughput(results, concurrency_levels)

        # Calculate summary stats
        pr_results = [r for r in results if r.implementation == "pydantic-resolve" and 'concurrent' not in r.query_name]
        sw_results = [r for r in results if r.implementation == "strawberry" and 'concurrent' not in r.query_name]

        pr_wins = 0
        sw_wins = 0
        for pr in pr_results:
            sw = next((s for s in sw_results if s.query_name == pr.query_name), None)
            if sw:
                if pr.mean_time_ms < sw.mean_time_ms:
                    pr_wins += 1
                else:
                    sw_wins += 1

        # Generate HTML
        template = Template(REPORT_TEMPLATE)
        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=len(set(r.query_name for r in results if 'concurrent' not in r.query_name)),
            iterations=iterations,
            pr_wins=pr_wins,
            sw_wins=sw_wins,
            results=sorted(results, key=lambda r: (r.query_name, r.implementation)),
            has_concurrent=has_concurrent,
        )

        filepath = os.path.join(self.output_dir, "benchmark_report.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Report saved to: {filepath}")
        return filepath
