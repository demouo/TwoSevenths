"""
内容审核服务
TODO: 集成LLM进行内容审核
"""


async def moderate_content(content: str) -> bool:
    """
    使用LLM审核内容

    Args:
        content: 待审核的内容

    Returns:
        bool: True表示审核通过，False表示审核不通过
    """
    # TODO: 实现LLM内容审核
    # 1. 调用LLM API
    # 2. 检查是否包含违规内容
    # 3. 返回审核结果

    # 临时：暂时全部通过
    return True
