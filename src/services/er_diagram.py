from pydantic_resolve import base_entity

BaseEntity = base_entity()
diagram = BaseEntity.get_diagram()
AutoLoad = diagram.create_auto_load()

