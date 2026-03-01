# GraphQL Benchmark: pydantic-resolve vs Strawberry

Performance comparison between pydantic-resolve GraphQL and Strawberry GraphQL.

## Quick Start

```bash
# Install dependencies
pip install strawberry-graphql[fastapi] matplotlib jinja2

# Run full benchmark
python benchmark/run_benchmark.py

# Run quick test (10 iterations)
python benchmark/run_benchmark.py --quick
```

## Output

- `benchmark/results/benchmark_report.html` - Interactive HTML report
- `benchmark/results/charts/*.png` - Comparison charts

## Test Scenarios

| Scenario | Description |
|----------|-------------|
| simple_* | Single table queries |
| one_to_one | Task -> Owner relationship |
| one_to_many | Team -> Sprints/Users |
| nested_2_layers | Team -> Sprints -> Stories |
| nested_3_layers | Team -> Sprints -> Stories -> Tasks |
| nested_4_layers | Deep nesting with owners |
| concurrent_* | Parallel request handling |

## Metrics

- **Response Time**: Mean, Median, P95, P99 (ms)
- **Memory Usage**: Peak memory (MB)
- **Throughput**: Requests/second (concurrent tests)

## Implementation Details

### pydantic-resolve
- Uses `GraphQLHandler` from `pydantic_resolve.graphql`
- DataLoader via `aiodataloader`
- Entity-First architecture

### Strawberry
- Uses `strawberry.Schema` with `strawberry.dataloader`
- FastAPI integration via `strawberry.fastapi.GraphQLRouter`
- Field-level resolvers
