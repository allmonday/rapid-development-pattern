"""Performance metrics collector for GraphQL benchmark."""

import time
import tracemalloc
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from statistics import mean, median, stdev
import json


@dataclass
class MetricResult:
    """Single test result."""
    name: str
    implementation: str  # "pydantic-resolve" | "strawberry"
    query_name: str

    # Time metrics (milliseconds)
    total_time_ms: float
    resolve_time_ms: float
    db_query_time_ms: float = 0.0

    # Memory metrics (bytes)
    memory_peak_bytes: int = 0
    memory_delta_bytes: int = 0

    # Database metrics
    db_query_count: int = 0

    # Response data
    response_size_bytes: int = 0
    success: bool = True
    error: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Aggregated test results."""
    name: str
    implementation: str
    query_name: str
    iterations: int

    # Time statistics (milliseconds)
    mean_time_ms: float
    median_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    p95_time_ms: float
    p99_time_ms: float

    # Memory statistics (MB)
    mean_memory_mb: float
    peak_memory_mb: float

    # Database statistics
    mean_db_queries: float

    # Raw data
    raw_results: List[MetricResult] = field(default_factory=list)


class MetricsCollector:
    """Performance metrics collector."""

    def __init__(self):
        self.results: List[MetricResult] = []

    async def measure(
        self,
        name: str,
        implementation: str,
        query_name: str,
        query_func: Callable,
        *args,
        **kwargs
    ) -> MetricResult:
        """Execute a single measurement."""

        # Start memory tracking
        tracemalloc.start()
        start_time = time.perf_counter()

        try:
            result = await query_func(*args, **kwargs)
            success = True
            error = None
            response_size = len(json.dumps(result, default=str).encode('utf-8'))
        except Exception as e:
            success = False
            error = str(e)
            result = None
            response_size = 0

        end_time = time.perf_counter()

        # Get memory peak
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        metric = MetricResult(
            name=name,
            implementation=implementation,
            query_name=query_name,
            total_time_ms=(end_time - start_time) * 1000,
            resolve_time_ms=(end_time - start_time) * 1000,
            memory_peak_bytes=peak,
            memory_delta_bytes=current,
            response_size_bytes=response_size,
            success=success,
            error=error,
        )

        self.results.append(metric)
        return metric

    def aggregate(
        self,
        implementation: str,
        query_name: str,
        results: List[MetricResult]
    ) -> BenchmarkResult:
        """Aggregate multiple measurements."""

        successful_results = [r for r in results if r.success]
        if not successful_results:
            return BenchmarkResult(
                name=f"{implementation}_{query_name}",
                implementation=implementation,
                query_name=query_name,
                iterations=len(results),
                mean_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                p95_time_ms=0,
                p99_time_ms=0,
                mean_memory_mb=0,
                peak_memory_mb=0,
                mean_db_queries=0,
                raw_results=results,
            )

        times = [r.total_time_ms for r in successful_results]
        memories = [r.memory_peak_bytes / (1024 * 1024) for r in successful_results]

        sorted_times = sorted(times)
        n = len(sorted_times)

        return BenchmarkResult(
            name=f"{implementation}_{query_name}",
            implementation=implementation,
            query_name=query_name,
            iterations=len(results),
            mean_time_ms=mean(times),
            median_time_ms=median(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            std_dev_ms=stdev(times) if len(times) > 1 else 0,
            p95_time_ms=sorted_times[int(n * 0.95)] if n > 0 else 0,
            p99_time_ms=sorted_times[int(n * 0.99)] if n > 0 else 0,
            mean_memory_mb=mean(memories) if memories else 0,
            peak_memory_mb=max(memories) if memories else 0,
            mean_db_queries=mean([r.db_query_count for r in successful_results]),
            raw_results=results,
        )

    def clear(self):
        """Clear all results."""
        self.results = []


def format_comparison(pr_result: BenchmarkResult, sw_result: BenchmarkResult) -> str:
    """Format comparison output."""
    lines = [
        f"\n{'='*70}",
        f"Query: {pr_result.query_name}",
        f"{'='*70}",
        f"{'Metric':<30} {'pydantic-resolve':<20} {'Strawberry':<20}",
        f"{'-'*70}",
        f"{'Mean Time (ms)':<30} {pr_result.mean_time_ms:<20.2f} {sw_result.mean_time_ms:<20.2f}",
        f"{'Median Time (ms)':<30} {pr_result.median_time_ms:<20.2f} {sw_result.median_time_ms:<20.2f}",
        f"{'P95 Time (ms)':<30} {pr_result.p95_time_ms:<20.2f} {sw_result.p95_time_ms:<20.2f}",
        f"{'P99 Time (ms)':<30} {pr_result.p99_time_ms:<20.2f} {sw_result.p99_time_ms:<20.2f}",
        f"{'Mean Memory (MB)':<30} {pr_result.mean_memory_mb:<20.2f} {sw_result.mean_memory_mb:<20.2f}",
        f"{'Peak Memory (MB)':<30} {pr_result.peak_memory_mb:<20.2f} {sw_result.peak_memory_mb:<20.2f}",
    ]

    # Add performance ratio
    if sw_result.mean_time_ms > 0:
        ratio = pr_result.mean_time_ms / sw_result.mean_time_ms
        if ratio < 1:
            lines.append(f"{'Performance Ratio':<30} pydantic-resolve is {1/ratio:.2f}x faster")
        else:
            lines.append(f"{'Performance Ratio':<30} Strawberry is {ratio:.2f}x faster")

    return "\n".join(lines)
