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
from benchmark.tests.test_queries import PR_QUERIES, SW_QUERIES, TEST_SCENARIOS, CONCURRENCY_LEVELS, CONCURRENT_ITERATIONS


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


async def run_benchmark(quick: bool = False, output_dir: str = "benchmark/results", large: bool = False):
    """Run complete benchmark suite."""
    iterations = 10 if quick else 50
    collector = MetricsCollector()
    all_results: List[BenchmarkResult] = []

    print("=" * 70)
    dataset_label = "LARGE" if large else "SMALL"
    print(f"pydantic-resolve vs Strawberry GraphQL Benchmark ({dataset_label})")
    print("=" * 70)
    print(f"Started at: {datetime.now()}")
    print(f"Iterations per test: {iterations}")
    print()

    # Initialize database
    print("Initializing database...")
    import src.db as db
    await db.init()
    if large:
        await db.prepare_large()
        print("Database initialized (large dataset).\n")
    else:
        await db.prepare()
        print("Database initialized.\n")

    # Warmup
    print("Warming up (priming caches)...")
    for scenario in TEST_SCENARIOS:
        pr_query = PR_QUERIES[scenario]
        sw_query = SW_QUERIES[scenario]
        try:
            await execute_pydantic_resolve(pr_query)
        except Exception as e:
            print(f"  Warning: pydantic-resolve warmup failed for {scenario}: {e}")
        try:
            await execute_strawberry(sw_query)
        except Exception as e:
            print(f"  Warning: Strawberry warmup failed for {scenario}: {e}")
    print("Warmup complete.\n")

    # Run standard test scenarios
    print("Running standard test scenarios...")
    for scenario in TEST_SCENARIOS:
        print(f"\n  Testing: {scenario}")
        pr_query = PR_QUERIES[scenario]
        sw_query = SW_QUERIES[scenario]

        # pydantic-resolve tests
        pr_results = []
        for i in range(iterations):
            result = await collector.measure(
                name=f"pr_{scenario}_{i}",
                implementation="pydantic-resolve",
                query_name=scenario,
                query_func=execute_pydantic_resolve,
                query=pr_query,
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
                query=sw_query,
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

    pr_query = PR_QUERIES["nested_4_layers_with_owners"]
    sw_query = SW_QUERIES["nested_4_layers_with_owners"]
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
                    query=pr_query,
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
                    query=sw_query,
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
        pr_t = concurrency / (pr_benchmark.mean_time_ms / 1000) if pr_benchmark.mean_time_ms > 0 else 0
        sw_t = concurrency / (sw_benchmark.mean_time_ms / 1000) if sw_benchmark.mean_time_ms > 0 else 0

        print(f"\n  Results for {concurrency} concurrent requests:")
        print(f"    pydantic-resolve: {pr_t:.1f} req/s (mean: {pr_benchmark.mean_time_ms:.2f}ms)")
        print(f"    Strawberry:       {sw_t:.1f} req/s (mean: {sw_benchmark.mean_time_ms:.2f}ms)")

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
        "--large",
        action="store_true",
        help="Use large dataset (50 teams, 200 users, 450 stories, 1350 tasks)"
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark/results",
        help="Output directory for results (default: benchmark/results)"
    )
    args = parser.parse_args()

    asyncio.run(run_benchmark(quick=args.quick, output_dir=args.output_dir, large=args.large))


if __name__ == "__main__":
    main()
