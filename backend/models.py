from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime, timezone
from uuid import uuid4


class VoteRequest(BaseModel):
    """投票请求模型"""
    option: Literal["double", "single", "alternate"] = Field(
        ...,
        description="休息模式：double=双休, single=单休, alternate=大小周"
    )


class VoteResponse(BaseModel):
    """投票响应模型"""
    success: bool
    message: str


class OptionStats(BaseModel):
    """选项统计模型"""
    count: int
    percentage: float


class TimelineItem(BaseModel):
    """时间线项目模型"""
    timestamp: str
    option: str


class StatsResponse(BaseModel):
    """统计数据响应模型"""
    total: int
    options: dict[str, OptionStats]
    timeline: list[TimelineItem]


class MessageRequest(BaseModel):
    """弹幕请求模型"""
    content: str = Field(..., min_length=1, max_length=200)
    option: Literal["double", "single", "alternate"]


class MessageResponse(BaseModel):
    """弹幕响应模型"""
    success: bool
    message_id: str


class Message(BaseModel):
    """弹幕消息模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    option: str
    likes: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MessagesResponse(BaseModel):
    """弹幕列表响应模型"""
    messages: list[Message]
    total: int


class LikeResponse(BaseModel):
    """点赞响应模型"""
    success: bool
    likes: int
