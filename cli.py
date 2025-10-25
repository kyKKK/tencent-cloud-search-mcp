#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终版命令行测试工具 - 默认JSON格式，简化参数
"""

import os
import sys
import json
import asyncio
import argparse
from server import perform_search, perform_generate_timestamp


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="腾讯云搜索最终版命令行测试工具")
    parser.add_argument("query", nargs='?', help="搜索查询字符串（使用--timestamp时可选）")
    parser.add_argument("-n", "--num", type=int, default=5, help="返回结果数量 (默认5)")
    parser.add_argument("-o", "--offset", type=int, default=0, help="结果偏移量 (默认0)")
    parser.add_argument("-m", "--mode", type=int, choices=[0, 1, 2], default=0, help="搜索模式: 0=自然检索, 1=多模态, 2=混合 (默认0)")
    parser.add_argument("-s", "--site", help="站内搜索域名，例如: github.com")
    parser.add_argument("--from-time", type=int, help="起始时间戳 (精确到秒)")
    parser.add_argument("--to-time", type=int, help="结束时间戳 (精确到秒)")
    parser.add_argument("--timestamp", action="store_true", help="测试时间戳生成工具")
    parser.add_argument("--year", type=int, help="生成时间戳用的年份")
    parser.add_argument("--month", type=int, help="生成时间戳用的月份")
    parser.add_argument("--day", type=int, help="生成时间戳用的日期")
    parser.add_argument("--pretty", action="store_true", help="美化JSON输出")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")

    args = parser.parse_args()

    # 设置调试模式
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"

    # 时间戳生成功能
    if args.timestamp:
        if not all([args.year, args.month, args.day]):
            print("❌ 生成时间戳需要提供 --year --month --day 参数")
            sys.exit(1)

        try:
            result = await perform_generate_timestamp(args.year, args.month, args.day)
            print("🕐 时间戳生成结果:")
            result_json = json.loads(result)
            print(json.dumps(result_json, ensure_ascii=False, indent=2))
            return
        except Exception as e:
            print(f"❌ 时间戳生成失败: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    # 检查查询参数
    if not args.query:
        print("❌ 错误: 请提供搜索查询字符串")
        print("使用 -h 查看帮助信息")
        print("\n📝 最终版使用示例:")
        print("  基础搜索: python cli_final.py 'Python教程'")
        print("  站内搜索: python cli_final.py 'React hooks' -s github.com")
        print("  时间搜索: python cli_final.py 'ChatGPT' --from-time 1672531200")
        print("  多模态: python cli_final.py '猫咪图片' -m 1")
        print("  时间戳: python cli_final.py --timestamp --year 2024 --month 1 --day 15")
        sys.exit(1)

    # 检查环境变量
    if not os.getenv("TENCENTCLOUD_SECRET_ID") or not os.getenv("TENCENTCLOUD_SECRET_KEY"):
        print("❌ 错误: 请设置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY")
        print("示例:")
        print("export TENCENTCLOUD_SECRET_ID='你的SecretId'")
        print("export TENCENTCLOUD_SECRET_KEY='你的SecretKey'")
        sys.exit(1)

    try:
        print(f"🔍 搜索中: {args.query}")

        # 显示参数信息
        param_info = [f"数量={args.num}", f"偏移={args.offset}", f"模式={args.mode}"]
        if args.site:
            param_info.append(f"站点={args.site}")
        if args.from_time:
            param_info.append(f"起始时间={args.from_time}")
        if args.to_time:
            param_info.append(f"结束时间={args.to_time}")

        print(f"📊 参数: {', '.join(param_info)}")
        print("-" * 60)

        # 使用统一搜索工具
        result = await perform_search(
            query=args.query,
            num=args.num,
            offset=args.offset,
            mode=args.mode,
            site=args.site,
            from_time=args.from_time,
            to_time=args.to_time
        )

        # 输出JSON结果
        result_json = json.loads(result)
        if args.pretty:
            print(json.dumps(result_json, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result_json, ensure_ascii=False))

        print("\n" + "-" * 60)
        print("💡 最终版本特点:")
        print("  ✅ 默认JSON格式，便于程序处理")
        print("  ✅ 简化参数，减少配置复杂度")
        print("  ✅ 结构化输出，LLM友好")
        print("  ✅ 3个核心工具，避免选择困难")

    except KeyboardInterrupt:
        print("\n⚠️  搜索被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())