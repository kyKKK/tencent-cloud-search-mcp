#!/usr/bin/env python3

"""
Tencent Cloud Search MCP Server (Final Version)
使用FastMCP框架实现腾讯云搜索API的MCP服务器
"""

import json
import logging
import os
from typing import Optional

from fastmcp import FastMCP
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.wsa.v20250508 import models, wsa_client

# 配置日志 - 支持环境变量控制日志级别
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tencent-cloud-search")

# 创建FastMCP服务器实例
mcp = FastMCP("tencent-cloud-search")


def get_tencent_credentials() -> credential.Credential:
    """获取腾讯云认证信息"""
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")

    if not secret_id or not secret_key:
        raise ValueError(
            "请设置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY\n"
            "密钥获取地址: https://console.cloud.tencent.com/cam/capi"
        )

    return credential.Credential(secret_id, secret_key)


def create_wsa_client() -> wsa_client.WsaClient:
    """创建腾讯云WSA客户端"""
    try:
        cred = get_tencent_credentials()

        # 配置HTTP选项
        httpProfile = HttpProfile()
        httpProfile.endpoint = "wsa.tencentcloudapi.com"

        # 配置客户端选项
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 创建客户端
        client = wsa_client.WsaClient(cred, "", clientProfile)
        return client

    except Exception as e:
        logger.error(f"创建腾讯云客户端失败: {e}")
        raise


def format_search_results_json(result_data: dict, query: str) -> str:
    """
    格式化搜索结果为JSON格式，优化大模型读取体验
    根据腾讯云官方文档格式解析结果
    """

    # 检查是否有结果 - 根据官方文档，结果在Pages字段中
    if "Pages" not in result_data or not result_data["Pages"]:
        no_results = {"query": query, "results": [], "count": 0, "message": "未找到相关结果"}
        return json.dumps(no_results, ensure_ascii=False, indent=2)

    # 解析Pages数组中的JSON字符串
    pages_data = result_data["Pages"]
    parsed_results = []

    for page_str in pages_data:
        try:
            # 解析每个页面的JSON字符串
            page_data = json.loads(page_str)

            # 根据官方文档字段提取信息
            result_item = {
                "title": page_data.get("title", ""),
                "date": page_data.get("date", ""),
                "url": page_data.get("url", ""),
                "passage": page_data.get("passage", ""),
                "content": page_data.get("content", ""),  # 尊享版字段
                "site": page_data.get("site", ""),
                "score": page_data.get("score", 0),
                "images": page_data.get("images", []),
                "favicon": page_data.get("favicon", ""),
            }
            parsed_results.append(result_item)
        except json.JSONDecodeError as e:
            logger.warning(f"解析页面数据失败: {e}, 原始数据: {page_str}")
            continue

    if not parsed_results:
        no_results = {"query": query, "results": [], "count": 0, "message": "所有结果解析失败"}
        return json.dumps(no_results, ensure_ascii=False, indent=2)

    # JSON格式 - 返回完整的官方格式数据
    structured_data = {"query": query, "results": parsed_results, "count": len(parsed_results)}

    # 添加其他官方字段
    if "Msg" in result_data:
        structured_data["msg"] = result_data["Msg"]
    if "RequestId" in result_data:
        structured_data["request_id"] = result_data["RequestId"]

    return json.dumps(structured_data, ensure_ascii=False, indent=2)


async def perform_search(
    query: str,
    num: int = 10,
    offset: int = 0,
    mode: int = 0,
    site: Optional[str] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
) -> str:
    """
    核心搜索功能，支持所有腾讯云搜索API参数，默认返回JSON格式

    Args:
        query: 搜索查询字符串
        num: 返回结果数量，默认10，最大50
        offset: 结果偏移量，默认0
        mode: 搜索模式，0=自然检索(默认)，1=多模态VR，2=混合结果
        site: 站内搜索域名（可选）
        from_time: 起始时间戳（可选）
        to_time: 结束时间戳（可选）

    Returns:
        JSON格式的搜索结果字符串
    """
    logger.debug("开始搜索请求: query='%s', num=%d, offset=%d, mode=%d, site=%s", query, num, offset, mode, site)

    try:
        if not query.strip():
            logger.warning("搜索查询为空")
            raise ValueError("搜索查询不能为空")

        # 验证模式参数
        if mode not in [0, 1, 2]:
            logger.warning("无效的搜索模式: %s", mode)
            raise ValueError("搜索模式必须是 0、1 或 2")

        logger.debug("创建腾讯云客户端...")
        # 创建腾讯云客户端
        client = create_wsa_client()

        # 构建请求参数
        request_params = {"Query": query, "Num": min(num, 50), "Offset": offset, "Mode": mode}  # 确保不超过API限制

        # 添加可选参数（仅在有效模式下添加）
        if mode == 0 or mode == 2:  # 自然检索模式
            if site:
                request_params["Site"] = site
                logger.debug("添加站内搜索过滤: %s", site)
            if from_time:
                request_params["FromTime"] = from_time
                logger.debug("添加起始时间过滤: %s", from_time)
            if to_time:
                request_params["ToTime"] = to_time
                logger.debug("添加结束时间过滤: %s", to_time)

        logger.debug("请求参数: %s", request_params)

        logger.debug("发送搜索请求...")
        # 创建请求对象
        req = models.SearchProRequest()
        req.from_json_string(json.dumps(request_params))

        # 发送请求
        resp = client.SearchPro(req)
        result_json = resp.to_json_string()
        logger.debug("收到API响应")

        # 解析结果
        result_data = json.loads(result_json)
        pages_count = len(result_data.get("Pages", []))
        logger.info("搜索完成: '%s' -> %d 条结果", query[:50], pages_count)

        # 使用JSON格式输出
        formatted_output = format_search_results_json(result_data, query)

        return formatted_output

    except TencentCloudSDKException as e:
        error_msg = f"腾讯云API错误: {e}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"搜索过程中发生错误: {e}"
        logger.error(error_msg)
        raise


async def perform_generate_timestamp(
    year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0
) -> str:
    """
    生成Unix时间戳的核心功能

    Args:
        year: 年份，例如：2024
        month: 月份，1-12，例如：1
        day: 日期，1-31，例如：15
        hour: 小时，0-23，默认0
        minute: 分钟，0-59，默认0
        second: 秒，0-59，默认0

    Returns:
        Unix时间戳字符串
    """
    try:
        import datetime

        # 创建datetime对象
        dt = datetime.datetime(year, month, day, hour, minute, second)
        # 转换为时间戳
        timestamp = int(dt.timestamp())

        # 返回JSON格式的时间戳信息
        timestamp_info = {"timestamp": timestamp, "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"), "timezone": "UTC"}
        return json.dumps(timestamp_info, ensure_ascii=False, indent=2)

    except ValueError as e:
        error_info = {"error": "日期时间无效", "message": str(e), "hint": "请检查输入的年月日时分秒是否正确"}
        return json.dumps(error_info, ensure_ascii=False, indent=2)
    except Exception as e:
        error_info = {"error": "生成时间戳失败", "message": str(e)}
        return json.dumps(error_info, ensure_ascii=False, indent=2)


@mcp.tool()
async def tencent_search(
    query: str,
    num: int = 10,
    offset: int = 0,
    mode: int = 0,
    site: Optional[str] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
) -> str:
    """
    腾讯云搜索 - 统一的网络搜索工具，返回JSON格式的结构化结果

    Args:
        query: 搜索查询字符串，例如："Python教程"、"今天北京的天气"
        num: 返回结果数量，默认10，范围1-50
        offset: 结果偏移量，默认0，用于分页
        mode: 搜索模式，默认0：
              0=自然检索(推荐)，适合常规文字搜索
              1=多模态VR，适合图片、视频搜索
              2=混合结果，结合自然检索和多模态
        site: 站内搜索域名（可选），例如："github.com"、"zhihu.com"，用于在特定网站内搜索
        from_time: 起始时间戳（可选），精确到秒，用于过滤特定时期的内容
        to_time: 结束时间戳（可选），精确到秒，用于过滤特定时期的内容

    Returns:
        JSON格式的搜索结果，包含query、results、count等字段

    Examples:
        # 基础搜索
        tencent_search("Python机器学习教程", num=5)

        # 站内搜索
        tencent_search("React hooks", site="github.com", num=5)

        # 时间范围搜索（需要先使用generate_timestamp生成时间戳）
        tencent_search("ChatGPT发展", from_time=1672531200, to_time=1704067199)

        # 多模态搜索（图片、视频）
        tencent_search("猫咪图片", mode=1, num=5)

        # 复合搜索：在GitHub搜索2023年的Python项目
        tencent_search(
            query="Python机器学习",
            site="github.com",
            from_time=1672531200,  # 2023-01-01
            to_time=1704067199,    # 2023-12-31
            num=10
        )

    Tips:
        - 默认返回JSON格式，便于程序处理和分析
        - 使用站内搜索时，mode=0（自然检索）效果最佳
        - 时间搜索需要提供Unix时间戳，可使用generate_timestamp工具生成
        - 多模态搜索适合查找图片、壁纸、视频等内容
        - 混合模式(mode=2)提供最全面的结果
    """
    return await perform_search(
        query=query, num=num, offset=offset, mode=mode, site=site, from_time=from_time, to_time=to_time
    )


@mcp.tool()
async def generate_timestamp(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> str:
    """
    生成Unix时间戳 - 用于时间范围搜索的辅助工具，返回JSON格式

    Args:
        year: 年份，例如：2024
        month: 月份，1-12，例如：1
        day: 日期，1-31，例如：15
        hour: 小时，0-23，默认0
        minute: 分钟，0-59，默认0
        second: 秒，0-59，默认0

    Returns:
        JSON格式的时间戳信息

    Example:
        # 生成2024年1月15日的时间戳
        generate_timestamp(2024, 1, 15)

        # 生成2023年12月31日23:59:59的时间戳
        generate_timestamp(2023, 12, 31, 23, 59, 59)
    """
    return await perform_generate_timestamp(year, month, day, hour, minute, second)


@mcp.tool()
async def search_health_check() -> str:
    """
    检查腾讯云搜索服务状态和配置

    Returns:
        服务状态信息
    """
    try:
        # 尝试创建客户端来验证认证信息
        create_wsa_client()
        status_info = {
            "status": "healthy",
            "message": "腾讯云搜索服务配置正常，可以开始使用搜索功能",
            "service": "tencent-cloud-search",
        }
        return json.dumps(status_info, ensure_ascii=False, indent=2)
    except ValueError as e:
        error_info = {
            "status": "error",
            "error_type": "configuration",
            "message": str(e),
            "service": "tencent-cloud-search",
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)
    except Exception as e:
        error_info = {
            "status": "error",
            "error_type": "service",
            "message": f"服务检查失败: {e}",
            "service": "tencent-cloud-search",
        }
        return json.dumps(error_info, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # FastMCP自动处理服务器启动
    mcp.run()
