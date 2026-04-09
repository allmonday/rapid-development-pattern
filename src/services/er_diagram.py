from pydantic_resolve import base_entity

BaseEntity = base_entity()
diagram = None
AutoLoad = None

def initialize():
    """在所有 entity schema 注册后调用，构建 diagram 并合并 ORM 关系。"""
    global diagram, AutoLoad

    from pydantic_resolve.integration.sqlalchemy import build_relationship
    from pydantic_resolve.integration.mapping import Mapping
    import src.db as db
    import src.services.user.model as user_orm
    import src.services.team.model as team_orm
    import src.services.sprint.model as sprint_orm
    import src.services.story.model as story_orm
    import src.services.task.model as task_orm
    import src.services.user.schema as user_dto
    import src.services.team.schema as team_dto
    import src.services.sprint.schema as sprint_dto
    import src.services.story.schema as story_dto
    import src.services.task.schema as task_dto

    diagram = BaseEntity.get_diagram()

    orm_entities = build_relationship(
        mappings=[
            Mapping(entity=user_dto.User, orm=user_orm.User),
            Mapping(entity=team_dto.Team, orm=team_orm.Team),
            Mapping(entity=sprint_dto.Sprint, orm=sprint_orm.Sprint),
            Mapping(entity=story_dto.Story, orm=story_orm.Story),
            Mapping(entity=task_dto.Task, orm=task_orm.Task),
        ],
        session_factory=db.async_session,
    )

    diagram = diagram.add_relationship(orm_entities)
    AutoLoad = diagram.create_auto_load()
