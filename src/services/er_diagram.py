from pydantic_resolve import base_entity

BaseEntity = base_entity()
diagram = None


def _create_page_many_to_many_loader(
    *,
    source_orm_kls,
    target_orm_kls,
    target_dto_kls,
    secondary_table,
    secondary_local_col_name,
    secondary_remote_col_name,
    target_match_col_name,
    sort_field: str = "id",
    pk_col_name: str = "id",
    session_factory,
    filters=None,
):
    """Create a paginated loader for many-to-many relationships."""
    from collections import defaultdict
    from aiodataloader import DataLoader
    from pydantic_resolve.graphql.pagination.types import PageArgs, Pagination

    class _Loader(DataLoader):
        async def batch_load_fn(self, keys):
            from sqlalchemy import select, func

            if not keys:
                return []

            first_cmd = keys[0]
            page_args: PageArgs = first_cmd.page_args
            fk_values = [cmd.fk_value for cmd in keys]

            effective_limit = page_args.effective_limit
            start = page_args.offset + 1
            end = start + effective_limit

            async with self.session_factory() as session:
                # Join secondary table to get target keys with row numbering
                secondary_local = getattr(self.secondary_table.c, self.secondary_local_col_name)
                secondary_remote = getattr(self.secondary_table.c, self.secondary_remote_col_name)
                target_col = getattr(self.target_orm_kls, self.target_match_col_name)
                sort_col = getattr(self.target_orm_kls, self.sort_field)
                pk_col = getattr(self.target_orm_kls, self.pk_col_name)

                rn_label = "_pr_rn"
                tc_label = "_pr_tc"

                row_num_col = func.row_number().over(
                    partition_by=secondary_local,
                    order_by=[sort_col, pk_col],
                ).label(rn_label)

                total_count_col = func.count().over(
                    partition_by=secondary_local,
                ).label(tc_label)

                inner = select(
                    secondary_local,
                    secondary_remote,
                    row_num_col,
                    total_count_col,
                ).where(secondary_local.in_(fk_values))
                subq = inner.subquery()

                rn_col = subq.c[rn_label]
                tc_col = subq.c[tc_label]
                local_col_sub = subq.c[self.secondary_local_col_name]
                remote_col_sub = subq.c[self.secondary_remote_col_name]

                outer = select(subq).where(rn_col.between(start, end)).order_by(
                    local_col_sub, rn_col,
                )
                rows = (await session.execute(outer)).all()

                # Collect target keys for this page
                target_keys = list({row._mapping[self.secondary_remote_col_name] for row in rows})
                if not target_keys:
                    # Still need counts for parents with no results in this range
                    missing_fks = [cmd.fk_value for cmd in keys]
                    count_q = (
                        select(secondary_local, func.count().label(tc_label))
                        .where(secondary_local.in_(missing_fks))
                        .group_by(secondary_local)
                    )
                    total_counts = {}
                    for row in (await session.execute(count_q)).all():
                        total_counts[row[0]] = row[1]

                    return [
                        {"items": [], "pagination": Pagination(has_more=False, total_count=total_counts.get(cmd.fk_value, 0))}
                        for cmd in keys
                    ]

                # Fetch actual target objects
                target_stmt = select(self.target_orm_kls).where(target_col.in_(target_keys))
                target_rows = (await session.scalars(target_stmt)).all()
                target_map = {getattr(r, self.target_match_col_name): r for r in target_rows}

                # Group results by source fk
                grouped = defaultdict(list)
                total_counts = {}
                for row in rows:
                    mapping = row._mapping
                    fk_val = mapping[self.secondary_local_col_name]
                    remote_val = mapping[self.secondary_remote_col_name]
                    rn = mapping[rn_label]
                    tc = mapping[tc_label]
                    total_counts[fk_val] = tc
                    target_obj = target_map.get(remote_val)
                    if target_obj is not None:
                        grouped[fk_val].append((target_obj, rn))

                # Fallback for parents with no rows in this page range
                missing_fks = [cmd.fk_value for cmd in keys if cmd.fk_value not in total_counts]
                if missing_fks:
                    count_q = (
                        select(secondary_local, func.count().label(tc_label))
                        .where(secondary_local.in_(missing_fks))
                        .group_by(secondary_local)
                    )
                    for row in (await session.execute(count_q)).all():
                        total_counts[row[0]] = row[1]

                results = []
                for cmd in keys:
                    page_rows = [r for r, _ in grouped.get(cmd.fk_value, [])][:effective_limit]
                    tc = total_counts.get(cmd.fk_value, 0)
                    results.append({
                        "items": page_rows,
                        "pagination": Pagination(
                            has_more=tc >= end if cmd.fk_value in total_counts else False,
                            total_count=tc,
                        ),
                    })
                return results

    _Loader.target_orm_kls = target_orm_kls
    _Loader.target_dto_kls = target_dto_kls
    _Loader.secondary_table = secondary_table
    _Loader.secondary_local_col_name = secondary_local_col_name
    _Loader.secondary_remote_col_name = secondary_remote_col_name
    _Loader.target_match_col_name = target_match_col_name
    _Loader.sort_field = sort_field
    _Loader.pk_col_name = pk_col_name
    _Loader.session_factory = staticmethod(session_factory)
    _Loader.filters = filters

    return _Loader


def initialize():
    """在所有 entity schema 注册后调用，构建 diagram 并合并 ORM 关系。"""
    global diagram

    from sqlalchemy import inspect as sa_inspect
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

    # Patch page_loader for MANYTOMANY relationships (not auto-generated by pydantic-resolve)
    from sqlalchemy.orm import MANYTOMANY
    for entity_cfg in diagram.entities:
        source_orm = {
            user_dto.User: user_orm.User,
            team_dto.Team: team_orm.Team,
            sprint_dto.Sprint: sprint_orm.Sprint,
            story_dto.Story: story_orm.Story,
            task_dto.Task: task_orm.Task,
        }.get(entity_cfg.kls)
        if source_orm is None:
            continue

        mapper = sa_inspect(source_orm)
        orm_rel_map = {r.key: r for r in mapper.relationships}

        for rel in entity_cfg.relationships:
            if not rel.is_list_relationship or rel.page_loader is not None:
                continue

            orm_rel = orm_rel_map.get(rel.name)
            if orm_rel is None or orm_rel.direction is not MANYTOMANY:
                continue

            target_orm = orm_rel.mapper.class_
            target_dto = {
                user_orm.User: user_dto.User,
                team_orm.Team: team_dto.Team,
                sprint_orm.Sprint: sprint_dto.Sprint,
                story_orm.Story: story_dto.Story,
                task_orm.Task: task_dto.Task,
            }.get(target_orm)
            if target_dto is None:
                continue

            target_mapper = sa_inspect(target_orm)
            pk_col_name = target_mapper.primary_key[0].name

            order_by = orm_rel.order_by
            sort_field = "id"
            if order_by and order_by is not False:
                if hasattr(order_by, "key"):
                    sort_field = order_by.key
                elif isinstance(order_by, (list, tuple)) and len(order_by) > 0:
                    sort_field = order_by[0].key if hasattr(order_by[0], "key") else "id"

            source_col = list(orm_rel.synchronize_pairs)[0][0]
            _, secondary_local = list(orm_rel.synchronize_pairs)[0]
            _, secondary_remote = list(orm_rel.secondary_synchronize_pairs)[0]
            target_col = list(orm_rel.secondary_synchronize_pairs)[0][0]

            rel.page_loader = _create_page_many_to_many_loader(
                source_orm_kls=source_orm,
                target_orm_kls=target_orm,
                target_dto_kls=target_dto,
                secondary_table=orm_rel.secondary,
                secondary_local_col_name=secondary_local.key,
                secondary_remote_col_name=secondary_remote.key,
                target_match_col_name=target_col.key,
                sort_field=sort_field,
                pk_col_name=pk_col_name,
                session_factory=db.async_session,
            )
            rel.sort_field = sort_field
