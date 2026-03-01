"""Chart generation for benchmark results."""

import os
from typing import List
from benchmark.metrics.collector import BenchmarkResult

# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class ChartGenerator:
    """Generate comparison charts."""

    COLORS = {
        'pydantic-resolve': '#2196F3',  # Blue
        'strawberry': '#4CAF50',         # Green
    }

    def __init__(self, output_dir: str = "benchmark/results/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_response_time_comparison(
        self,
        results: List[BenchmarkResult],
        title: str = "Response Time Comparison"
    ) -> str:
        """Generate response time comparison bar chart."""
        query_names = sorted(set(r.query_name for r in results))

        pr_results = {r.query_name: r for r in results if r.implementation == "pydantic-resolve"}
        sw_results = {r.query_name: r for r in results if r.implementation == "strawberry"}

        x = np.arange(len(query_names))
        width = 0.35

        fig, ax = plt.subplots(figsize=(14, 8))

        pr_values = [pr_results.get(q, BenchmarkResult(
            name="", implementation="", query_name=q, iterations=0,
            mean_time_ms=0, median_time_ms=0, min_time_ms=0, max_time_ms=0,
            std_dev_ms=0, p95_time_ms=0, p99_time_ms=0,
            mean_memory_mb=0, peak_memory_mb=0, mean_db_queries=0
        )).mean_time_ms for q in query_names]
        sw_values = [sw_results.get(q, BenchmarkResult(
            name="", implementation="", query_name=q, iterations=0,
            mean_time_ms=0, median_time_ms=0, min_time_ms=0, max_time_ms=0,
            std_dev_ms=0, p95_time_ms=0, p99_time_ms=0,
            mean_memory_mb=0, peak_memory_mb=0, mean_db_queries=0
        )).mean_time_ms for q in query_names]

        bars1 = ax.bar(x - width/2, pr_values, width,
                       label='pydantic-resolve', color=self.COLORS['pydantic-resolve'])
        bars2 = ax.bar(x + width/2, sw_values, width,
                       label='Strawberry', color=self.COLORS['strawberry'])

        ax.set_xlabel('Query Type')
        ax.set_ylabel('Mean Response Time (ms)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(query_names, rotation=45, ha='right', fontsize=9)
        ax.legend()

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{height:.1f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, "response_time_comparison.png")
        plt.savefig(filepath, dpi=150)
        plt.close()

        return filepath

    def plot_performance_ratio(
        self,
        results: List[BenchmarkResult],
        title: str = "Performance Ratio (pydantic-resolve / Strawberry)"
    ) -> str:
        """Generate performance ratio chart (< 1 means pydantic-resolve is faster)."""
        query_names = sorted(set(r.query_name for r in results))

        pr_results = {r.query_name: r for r in results if r.implementation == "pydantic-resolve"}
        sw_results = {r.query_name: r for r in results if r.implementation == "strawberry"}

        ratios = []
        for q in query_names:
            pr_time = pr_results.get(q)
            sw_time = sw_results.get(q)
            if pr_time and sw_time and sw_time.mean_time_ms > 0:
                ratios.append(pr_time.mean_time_ms / sw_time.mean_time_ms)
            else:
                ratios.append(1.0)

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = ['#4CAF50' if r < 1 else '#F44336' for r in ratios]
        bars = ax.bar(query_names, ratios, color=colors)

        ax.axhline(y=1, color='black', linestyle='--', label='Equal Performance')
        ax.set_xlabel('Query Type')
        ax.set_ylabel('Performance Ratio')
        ax.set_title(title)
        ax.set_xticklabels(query_names, rotation=45, ha='right', fontsize=9)

        # Add value labels
        for bar, ratio in zip(bars, ratios):
            height = bar.get_height()
            ax.annotate(f'{ratio:.2f}x',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, "performance_ratio.png")
        plt.savefig(filepath, dpi=150)
        plt.close()

        return filepath

    def plot_memory_usage(
        self,
        results: List[BenchmarkResult],
        title: str = "Memory Usage Comparison"
    ) -> str:
        """Generate memory usage comparison chart."""
        query_names = sorted(set(r.query_name for r in results))

        pr_results = {r.query_name: r for r in results if r.implementation == "pydantic-resolve"}
        sw_results = {r.query_name: r for r in results if r.implementation == "strawberry"}

        x = np.arange(len(query_names))
        width = 0.35

        fig, ax = plt.subplots(figsize=(14, 8))

        pr_memory = [pr_results.get(q, BenchmarkResult(
            name="", implementation="", query_name=q, iterations=0,
            mean_time_ms=0, median_time_ms=0, min_time_ms=0, max_time_ms=0,
            std_dev_ms=0, p95_time_ms=0, p99_time_ms=0,
            mean_memory_mb=0, peak_memory_mb=0, mean_db_queries=0
        )).mean_memory_mb for q in query_names]
        sw_memory = [sw_results.get(q, BenchmarkResult(
            name="", implementation="", query_name=q, iterations=0,
            mean_time_ms=0, median_time_ms=0, min_time_ms=0, max_time_ms=0,
            std_dev_ms=0, p95_time_ms=0, p99_time_ms=0,
            mean_memory_mb=0, peak_memory_mb=0, mean_db_queries=0
        )).mean_memory_mb for q in query_names]

        bars1 = ax.bar(x - width/2, pr_memory, width,
                       label='pydantic-resolve', color=self.COLORS['pydantic-resolve'])
        bars2 = ax.bar(x + width/2, sw_memory, width,
                       label='Strawberry', color=self.COLORS['strawberry'])

        ax.set_xlabel('Query Type')
        ax.set_ylabel('Mean Memory Usage (MB)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(query_names, rotation=45, ha='right', fontsize=9)
        ax.legend()

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, "memory_usage.png")
        plt.savefig(filepath, dpi=150)
        plt.close()

        return filepath

    def plot_throughput(
        self,
        results: List[BenchmarkResult],
        concurrency_levels: List[int],
        title: str = "Throughput vs Concurrency"
    ) -> str:
        """Generate throughput vs concurrency chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        for impl in ['pydantic-resolve', 'strawberry']:
            impl_results = [r for r in results if r.implementation == impl]
            throughputs = []
            for c in concurrency_levels:
                result = next((r for r in impl_results if r.query_name == f"concurrent_{c}"), None)
                if result and result.mean_time_ms > 0:
                    throughput = c / (result.mean_time_ms / 1000)
                    throughputs.append(throughput)
                else:
                    throughputs.append(0)

            ax.plot(concurrency_levels, throughputs, 'o-',
                   label=impl, color=self.COLORS[impl], linewidth=2, markersize=8)

        ax.set_xlabel('Concurrency Level')
        ax.set_ylabel('Throughput (req/s)')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        filepath = os.path.join(self.output_dir, "throughput.png")
        plt.savefig(filepath, dpi=150)
        plt.close()

        return filepath
