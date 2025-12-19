from fastapi import APIRouter, HTTPException, Query
from uuid import uuid4

from backend.models import (
    MessageRequest,
    MessageResponse,
    Message,
    MessagesResponse,
    LikeResponse
)
from backend.database import add_message, get_messages, like_message

router = APIRouter()


@router.post("/messages", response_model=MessageResponse)
async def create_message(message_request: MessageRequest):
    """发送弹幕"""
    try:
        # TODO: LLM内容审核
        # is_approved = await moderate_content(message_request.content)
        # if not is_approved:
        #     raise HTTPException(status_code=400, detail="内容审核未通过")

        # 创建新消息
        new_message = Message(
            content=message_request.content,
            option=message_request.option
        )

        # 保存到数据库
        success = add_message(
            new_message.id,
            new_message.content,
            new_message.option,
            new_message.timestamp
        )

        if success:
            return MessageResponse(success=True, message_id=new_message.id)
        else:
            raise HTTPException(status_code=500, detail="发送弹幕失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送弹幕失败: {str(e)}")


@router.get("/messages", response_model=MessagesResponse)
async def get_messages_list(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """获取弹幕列表"""
    try:
        messages_data, total = get_messages(limit, offset)

        # 转换为Message对象
        messages = [Message(**msg) for msg in messages_data]

        return MessagesResponse(
            messages=messages,
            total=total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取弹幕失败: {str(e)}")


@router.post("/messages/{message_id}/like", response_model=LikeResponse)
async def like_message_endpoint(message_id: str):
    """点赞弹幕"""
    try:
        likes = like_message(message_id)

        if likes is None:
            raise HTTPException(status_code=404, detail="弹幕不存在")

        return LikeResponse(success=True, likes=likes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"点赞失败: {str(e)}")
