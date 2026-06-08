"""GraphQL query definitions for benchmark tests."""

# Strawberry uses snake_case root fields (explicitly named via @strawberry.field(name='get_xxx'))
SW_QUERIES = {
    "simple_users": """
        query {
            get_users { id name level }
        }
    """,

    "simple_teams": """
        query {
            get_teams { id name }
        }
    """,

    "simple_sprints": """
        query {
            get_sprints { id name status }
        }
    """,

    "one_to_one_task_owner": """
        query {
            get_tasks { id name owner { id name } }
        }
    """,

    "one_to_many_team_sprints": """
        query {
            get_teams { id name sprints { id name status } }
        }
    """,

    "one_to_many_team_users": """
        query {
            get_teams { id name users { id name level } }
        }
    """,

    "nested_2_layers": """
        query {
            get_teams { id name sprints { id name stories { id name } } }
        }
    """,

    "nested_3_layers": """
        query {
            get_teams {
                id name
                sprints { id name stories { id name tasks { id name estimate } } }
            }
        }
    """,

    "nested_4_layers_with_owners": """
        query {
            get_teams {
                id name
                sprints {
                    id name
                    stories {
                        id name owner { id name }
                        tasks { id name estimate owner { id name } }
                    }
                }
            }
        }
    """,

    "sprint_with_stories_and_tasks": """
        query {
            get_sprints {
                id name status
                stories {
                    id name owner { id name }
                    tasks { id name estimate }
                }
            }
        }
    """,

    # 5-layer: every level resolves a related entity
    "nested_5_layers_full": """
        query {
            get_teams {
                id name
                sprints {
                    id name status
                    stories {
                        id name
                        owner { id name level }
                        tasks {
                            id name estimate
                            owner { id name level }
                        }
                    }
                }
            }
        }
    """,

    # Wide: team with both sprints and users fully expanded
    "wide_team_all_relations": """
        query {
            get_teams {
                id name
                sprints {
                    id name status
                    stories {
                        id name
                        owner { id name level }
                        tasks {
                            id name estimate
                            owner { id name level }
                        }
                    }
                }
                users {
                    id name level
                }
            }
        }
    """,
}

# pydantic-resolve uses camelCase query names + pagination wrapper (items)
PR_QUERIES = {
    "simple_users": """
        query {
            userGetUsers { id name level }
        }
    """,

    "simple_teams": """
        query {
            teamGetTeams { id name }
        }
    """,

    "simple_sprints": """
        query {
            sprintGetSprints { id name status }
        }
    """,

    "one_to_one_task_owner": """
        query {
            taskGetTasks { id name owner { id name level } }
        }
    """,

    "one_to_many_team_sprints": """
        query {
            teamGetTeams { id name sprints { items { id name status } } }
        }
    """,

    "one_to_many_team_users": """
        query {
            teamGetTeams { id name users { items { id name level } } }
        }
    """,

    "nested_2_layers": """
        query {
            teamGetTeams {
                id name
                sprints { items { id name stories { items { id name } } } }
            }
        }
    """,

    "nested_3_layers": """
        query {
            teamGetTeams {
                id name
                sprints {
                    items { id name stories { items { id name tasks { items { id name estimate } } } } }
                }
            }
        }
    """,

    "nested_4_layers_with_owners": """
        query {
            teamGetTeams {
                id name
                sprints {
                    items {
                        id name
                        stories {
                            items {
                                id name owner { id name level }
                                tasks { items { id name estimate owner { id name level } } }
                            }
                        }
                    }
                }
            }
        }
    """,

    "sprint_with_stories_and_tasks": """
        query {
            sprintGetSprints {
                id name status
                stories {
                    items {
                        id name owner { id name level }
                        tasks { items { id name estimate } }
                    }
                }
            }
        }
    """,

    "nested_5_layers_full": """
        query {
            teamGetTeams {
                id name
                sprints {
                    items {
                        id name status
                        stories {
                            items {
                                id name
                                owner { id name level }
                                tasks { items { id name estimate owner { id name level } } }
                            }
                        }
                    }
                }
            }
        }
    """,

    "wide_team_all_relations": """
        query {
            teamGetTeams {
                id name
                sprints {
                    items {
                        id name status
                        stories {
                            items {
                                id name
                                owner { id name level }
                                tasks { items { id name estimate owner { id name level } } }
                            }
                        }
                    }
                }
                users { items { id name level } }
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
    "nested_5_layers_full",
    "wide_team_all_relations",
]

# Concurrent test configuration
CONCURRENCY_LEVELS = [10, 50, 100]
CONCURRENT_ITERATIONS = 20
