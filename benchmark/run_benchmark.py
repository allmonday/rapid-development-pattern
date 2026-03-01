#!/usr/bin/env python
"""
pydantic-resolve vs Strawberry GraphQL Performance Benchmark

Usage:
    python benchmark/run_benchmark.py [--quick] [--output-dir DIR]

Options:
    --quick         Run quick test (10 iterations instead of 50)
    --output-dir    Specify output directory for results
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmark.metrics.collector import MetricsCollector, BenchmarkResult, format_comparison
from benchmark.metrics.report import ReportGenerator
from benchmark.tests.test_queries import QUERIES, TEST_SCENARIOS, CONCURRENCY_LEVELS, CONCURRENT_ITERATIONS


async def execute_pydantic_resolve(query: str) -> dict:
    """Execute pydantic-resolve GraphQL query."""
    from src.main import graphql_handler

    result = await graphql_handler.execute(query=query)
    return result


async def execute_strawberry(query: str) -> dict:
    """Execute Strawberry GraphQL query."""
    from benchmark.strawberry_impl.app import execute_query

    result = await execute_query(query)
    return result


async def run_benchmark(quick: bool = False, output_dir: str = "benchmark/results"):
    """Run complete benchmark suite."""
    iterations = 10 if quick else 50
    collector = MetricsCollector()
    all_results: List[BenchmarkResult] = []

    print("=" * 70)
    print("pydantic-resolve vs Strawberry GraphQL Benchmark")
    print("=" * 70)
    print(f"Started at: {datetime.now()}")
    print(f"Iterations per test: {iterations}")
    print()

    # Initialize database
    print("Initializing database...")
    import src.db as db
    await db.init()
    await db.prepare()
    print("Database initialized.\n")

    # Warmup: Execute each scenario once to prime caches
    print("Warming up (priming caches)...")
    for scenario in TEST_SCENARIOS:
        query = QUERIES[scenario]
        try:
            # Warmup pydantic-resolve
            await execute_pydantic_resolve(query)
        except Exception as e:
            print(f"  Warning: pydantic-resolve warmup failed for {scenario}: {e}")
        try:
            # Warmup Strawberry
            await execute_strawberry(query)
        except Exception as e:
            print(f"  Warning: Strawberry warmup failed for {scenario}: {e}")
    print("Warmup complete.\n")

    # Run standard test scenarios
    print("Running standard test scenarios...")
    for scenario in TEST_SCENARIOS:
        print(f"\n  Testing: {scenario}")
        query = QUERIES[scenario]

        # pydantic-resolve tests
        pr_results = []
        for i in range(iterations):
            result = await collector.measure(
                name=f"pr_{scenario}_{i}",
                implementation="pydantic-resolve",
                query_name=scenario,
                query_func=execute_pydantic_resolve,
                query=query,
            )
            pr_results.append(result)
            if (i + 1) % 10 == 0:
                print(f"    pydantic-resolve: {i + 1}/{iterations}")

        # Strawberry tests
        sw_results = []
        for i in range(iterations):
            result = await collector.measure(
                name=f"sw_{scenario}_{i}",
                implementation="strawberry",
                query_name=scenario,
                query_func=execute_strawberry,
                query=query,
            )
            sw_results.append(result)
            if (i + 1) % 10 == 0:
                print(f"    Strawberry: {i + 1}/{iterations}")

        # Aggregate and print results
        pr_benchmark = collector.aggregate("pydantic-resolve", scenario, pr_results)
        sw_benchmark = collector.aggregate("strawberry", scenario, sw_results)

        all_results.append(pr_benchmark)
        all_results.append(sw_benchmark)

        print(format_comparison(pr_benchmark, sw_benchmark))

    # Run concurrent tests
    print("\n" + "=" * 70)
    print("Running concurrent tests...")
    print("=" * 70)

    query = QUERIES["nested_4_layers_with_owners"]
    batches = 5 if quick else CONCURRENT_ITERATIONS

    for concurrency in CONCURRENCY_LEVELS:
        print(f"\n  Concurrency: {concurrency} parallel requests")

        # pydantic-resolve concurrent
        pr_all = []
        for batch in range(batches):
            tasks = [
                collector.measure(
                    name=f"pr_concurrent_{concurrency}_{batch}_{i}",
                    implementation="pydantic-resolve",
                    query_name=f"concurrent_{concurrency}",
                    query_func=execute_pydantic_resolve,
                    query=query,
                )
                for i in range(concurrency)
            ]
            batch_results = await asyncio.gather(*tasks)
            pr_all.extend(batch_results)
            if (batch + 1) % 5 == 0:
                print(f"    pydantic-resolve batch: {batch + 1}/{batches}")

        # Strawberry concurrent
        sw_all = []
        for batch in range(batches):
            tasks = [
                collector.measure(
                    name=f"sw_concurrent_{concurrency}_{batch}_{i}",
                    implementation="strawberry",
                    query_name=f"concurrent_{concurrency}",
                    query_func=execute_strawberry,
                    query=query,
                )
                for i in range(concurrency)
            ]
            batch_results = await asyncio.gather(*tasks)
            sw_all.extend(batch_results)
            if (batch + 1) % 5 == 0:
                print(f"    Strawberry batch: {batch + 1}/{batches}")

        # Aggregate concurrent results
        pr_benchmark = collector.aggregate("pydantic-resolve", f"concurrent_{concurrency}", pr_all)
        sw_benchmark = collector.aggregate("strawberry", f"concurrent_{concurrency}", sw_all)

        all_results.append(pr_benchmark)
        all_results.append(sw_benchmark)

        # Calculate and print throughput
        pr_throughput = concurrency / (pr_benchmark.mean_time_ms / 1000) if pr_benchmark.mean_time_ms > 0 else 0
        sw_throughput = concurrency / (sw_benchmark.mean_time_ms / 1000) if sw_benchmark.mean_time_ms > 0 else 0

        print(f"\n  Results for {concurrency} concurrent requests:")
        print(f"    pydantic-resolve throughput: {pr_throughput:.1f} req/s (mean: {pr_benchmark.mean_time_ms:.2f}ms)")
        print(f"    Strawberry throughput: {sw_throughput:.1f} req/s (mean: {sw_benchmark.mean_time_ms:.2f}ms)")
        if sw_throughput > 0:
            ratio = pr_throughput / sw_throughput
            if ratio > 1:
                print(f"    pydantic-resolve is {ratio:.2f}x faster")
            else:
                print(f"    Strawberry is {1/ratio:.2f}x faster")

    # Generate report
    print("\n" + "=" * 70)
    print("Generating report...")
    print("=" * 70)

    report_gen = ReportGenerator(output_dir)
    report_path = report_gen.generate(
        all_results,
        iterations=iterations,
        concurrency_levels=CONCURRENCY_LEVELS,
    )

    print(f"\nBenchmark completed at: {datetime.now()}")
    print(f"Report saved to: {report_path}")

    # Cleanup
    await db.engine.dispose()

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Run GraphQL benchmark: pydantic-resolve vs Strawberry"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test (10 iterations instead of 50)"
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark/results",
        help="Output directory for results (default: benchmark/results)"
    )
    args = parser.parse_args()

    asyncio.run(run_benchmark(quick=args.quick, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
