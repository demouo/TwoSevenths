from fastapi import APIRouter, HTTPException
from datetime import datetime

from backend.models import VoteRequest, VoteResponse, StatsResponse, OptionStats, TimelineItem
from backend.database import add_vote, get_vote_stats

router = APIRouter()


@router.post("/vote", response_model=VoteResponse)
async def vote(vote_request: VoteRequest):
    """提交投票"""
    try:
        timestamp = datetime.utcnow().isoformat()
        success = add_vote(vote_request.option, timestamp)

        if success:
            return VoteResponse(success=True, message="投票成功")
        else:
            raise HTTPException(status_code=500, detail="投票失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"投票失败: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计数据"""
    try:
        stats = get_vote_stats()
        total = stats["total"]
        option_counts = stats["option_counts"]

        # 确保所有选项都存在
        all_options = ["double", "single", "alternate"]
        for option in all_options:
            if option not in option_counts:
                option_counts[option] = 0

        # 计算百分比
        options = {}
        for option in all_options:
            count = option_counts[option]
            percentage = (count / total * 100) if total > 0 else 0
            options[option] = OptionStats(count=count, percentage=round(percentage, 2))

        # 构建时间线
        timeline = [
            TimelineItem(timestamp=item["timestamp"], option=item["option"])
            for item in stats["timeline"]
        ]

        return StatsResponse(
            total=total,
            options=options,
            timeline=timeline
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
