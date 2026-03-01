"""GraphQL query definitions for benchmark tests."""

QUERIES = {
    # Simple queries: single table
    "simple_users": """
        query {
            get_users {
                id
                name
                level
            }
        }
    """,

    "simple_teams": """
        query {
            get_teams {
                id
                name
            }
        }
    """,

    "simple_sprints": """
        query {
            get_sprints {
                id
                name
                status
            }
        }
    """,

    # 1:1 relationship: Task -> Owner
    "one_to_one_task_owner": """
        query {
            get_tasks {
                id
                name
                owner {
                    id
                    name
                }
            }
        }
    """,

    # 1:N relationship: Team -> Sprints
    "one_to_many_team_sprints": """
        query {
            get_teams {
                id
                name
                sprints {
                    id
                    name
                    status
                }
            }
        }
    """,

    # 1:N relationship: Team -> Users
    "one_to_many_team_users": """
        query {
            get_teams {
                id
                name
                users {
                    id
                    name
                    level
                }
            }
        }
    """,

    # 2-layer nested: Team -> Sprints -> Stories
    "nested_2_layers": """
        query {
            get_teams {
                id
                name
                sprints {
                    id
                    name
                    stories {
                        id
                        name
                    }
                }
            }
        }
    """,

    # 3-layer nested: Team -> Sprints -> Stories -> Tasks
    "nested_3_layers": """
        query {
            get_teams {
                id
                name
                sprints {
                    id
                    name
                    stories {
                        id
                        name
                        tasks {
                            id
                            name
                            estimate
                        }
                    }
                }
            }
        }
    """,

    # 4-layer deep nested (most complex)
    "nested_4_layers_with_owners": """
        query {
            get_teams {
                id
                name
                sprints {
                    id
                    name
                    stories {
                        id
                        name
                        owner {
                            id
                            name
                        }
                        tasks {
                            id
                            name
                            estimate
                            owner {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }
    """,

    # Sprint-centric query
    "sprint_with_stories_and_tasks": """
        query {
            get_sprints {
                id
                name
                status
                stories {
                    id
                    name
                    owner {
                        id
                        name
                    }
                    tasks {
                        id
                        name
                        estimate
                    }
                }
            }
        }
    """,
}

# Test scenarios configuration
TEST_SCENARIOS = [
    "simple_users",
    "simple_teams",
    "simple_sprints",
    "one_to_one_task_owner",
    "one_to_many_team_sprints",
    "one_to_many_team_users",
    "nested_2_layers",
    "nested_3_layers",
    "nested_4_layers_with_owners",
    "sprint_with_stories_and_tasks",
]

# Concurrent test configuration
CONCURRENCY_LEVELS = [10, 50, 100]
CONCURRENT_ITERATIONS = 20  # Number of batches for concurrent tests
