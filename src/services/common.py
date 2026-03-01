"""
通用响应类型
用于 mutation 返回简单类型（如 bool）
"""
from pydantic import BaseModel, Field


class BoolResponse(BaseModel):
    """Boolean 响应包装类型"""
    success: bool = Field(description="操作是否成功")

    model_config = {"from_attributes": True}
