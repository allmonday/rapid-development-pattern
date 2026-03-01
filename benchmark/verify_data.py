"""Verify data consistency between implementations."""
import asyncio
import json
import sys
sys.path.insert(0, '.')

import src.db as db
from src.main import graphql_handler
from benchmark.strawberry_impl.app import execute_query


import benchmark.tests.test_queries as tq


async def main():
    await db.init()
    await db.prepare()

    query = tq.QUERIES['nested_3_layers']

    print("Testing query:")
    print(query.strip())

    pr_result = await graphql_handler.execute(query=query)
    sw_result = await execute_query(query)

    pr_teams = pr_result.get('data', {}).get('get_teams', [])
    sw_teams = sw_result.get('data', {}).get('get_teams', [])

    pr_stories = []
    sw_stories = []
    for team in pr_teams:
        pr_stories.extend(team.get('sprints', []))
    for team in sw_teams:
        sw_stories.extend(team.get('sprints', []))

    pr_tasks = []
    sw_tasks = []
    for team in pr_teams:
        for sprint in team.get('sprints', []):
            for story in sprint.get('stories', []):
                pr_tasks.extend(story.get('tasks', []))
    for team in sw_teams:
        for sprint in team.get('sprints', []):
            for story in sprint.get('stories', []):
                sw_tasks.extend(story.get('tasks', []))

    print(f"\npydantic-resolve: {len(pr_teams)} teams, {len(pr_stories)} stories, {len(pr_tasks)} tasks")
    print(f"Strawberry:      {len(sw_teams)} teams, {len(sw_stories)} stories, {len(sw_tasks)} tasks")
    print(f"\nData match: {pr_tasks == sw_tasks}")

    await db.engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
