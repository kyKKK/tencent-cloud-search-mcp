# 腾讯云搜索 MCP 服务器 (最终版)

这是一个基于FastMCP框架和腾讯云搜索API的MCP服务器，默认返回JSON格式，专为Claude等大模型优化。

## 🚀 最终版特性

- **📊 JSON优先**: 默认返回结构化JSON数据，便于程序处理
- **🎯 3个核心工具**: 避免LLM选择困难，简化使用体验
- **⚡ 参数驱动**: 一个搜索工具支持所有搜索模式
- **🔧 简化配置**: 去除format参数，减少配置复杂度
- **🧠 LLM友好**: 结构化输出，便于大模型理解和处理

## 🛠️ 可用工具 (3个)

### 1. tencent_search
**统一搜索工具** - 支持基础搜索、站内搜索、时间范围搜索和多模态搜索

**参数:**
- **query** (必需): 搜索查询字符串
- **num** (可选): 返回结果数量，默认10，范围1-50
- **offset** (可选): 结果偏移量，默认0
- **mode** (可选): 搜索模式，0=自然检索(默认)，1=多模态，2=混合
- **site** (可选): 站内搜索域名，例如："github.com"
- **from_time** (可选): 起始时间戳（精确到秒）
- **to_time** (可选): 结束时间戳（精确到秒）

**返回**: JSON格式的搜索结果

### 2. generate_timestamp
**时间戳生成** - 用于时间范围搜索的辅助工具

**参数:**
- **year** (必需): 年份，例如：2024
- **month** (必需): 月份，1-12
- **day** (必需): 日期，1-31
- **hour** (可选): 小时，0-23，默认0
- **minute** (可选): 分钟，0-59，默认0
- **second** (可选): 秒，0-59，默认0

**返回**: JSON格式的时间戳信息

### 3. search_health_check
**健康检查** - 验证API配置和服务状态

**参数:** 无

**返回**: JSON格式的服务状态信息

## 📋 JSON输出格式

### 搜索结果格式
```json
{
  "query": "Python教程",
  "results": [
    {
      "title": "Python官方教程",
      "date": "2024-01-15",
      "url": "https://docs.python.org/3/tutorial/",
      "passage": "Python是一门简单易学的编程语言...",
      "content": "",
      "site": "Python官网",
      "score": 0.95,
      "images": [],
      "favicon": "https://docs.python.org/favicon.ico"
    }
  ],
  "count": 1,
  "msg": "",
  "request_id": "req-123456789"
}
```

### 时间戳格式
```json
{
  "timestamp": 1705248000,
  "datetime": "2024-01-15 00:00:00",
  "timezone": "UTC"
}
```

### 健康检查格式
```json
{
  "status": "healthy",
  "message": "腾讯云搜索服务配置正常",
  "service": "tencent-cloud-search"
}
```

## 💡 使用示例

### 基础搜索
```
请帮我搜索"Python机器学习教程"，返回5条结果
```

### 站内搜索
```
在GitHub搜索"React hooks项目"
```

### 时间范围搜索
```
搜索2023年ChatGPT相关的内容
```

### 多模态搜索
```
搜索"猫咪图片"，需要一些可爱的照片
```

### 复合搜索
```
在GitHub搜索2023年发布的Python机器学习项目，需要10个结果
```

### 时间戳生成辅助
```
帮我生成2024年1月1日0点的时间戳
```

## 📊 优化对比

| 特性 | 原版本 | 最终版本 |
|------|--------|----------|
| 工具数量 | 8个 | 3个 |
| 输出格式 | text/json可选 | JSON默认 |
| 参数复杂度 | format参数 | 简化参数 |
| LLM友好度 | 一般 | 优秀 |
| 选择难度 | 较高 | 很低 |

## 🔧 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 获取腾讯云密钥
访问 [腾讯云API密钥管理页面](https://console.cloud.tencent.com/cam/capi) 获取SecretId和SecretKey。

### 3. 配置Claude Desktop
在Claude Desktop配置文件中添加：

```json
{
  "mcpServers": {
    "tencent-cloud-search": {
      "command": "python",
      "args": ["/project_path/server.py"],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "你的SecretId",
        "TENCENTCLOUD_SECRET_KEY": "你的SecretKey"
      }
    }
  }
}
```

### 4. 启动前检查
```bash
# 使用最终版测试工具
python cli_final.py --timestamp --year 2024 --month 1 --day 15 --pretty
```

## 🧪 测试工具

### 命令行测试 (最终版)
```bash
# 基础搜索
python cli_final.py "Python教程"

# 站内搜索
python cli_final.py "React hooks" -s "github.com" -n 5

# 时间范围搜索
python cli_final.py "ChatGPT" --from-time 1672531200 --to-time 1704067199

# 多模态搜索
python cli_final.py "猫咪图片" -m 1 --pretty

# 时间戳生成
python cli_final.py --timestamp --year 2024 --month 1 --day 15
```

### 格式测试
```bash
# 测试JSON格式解析
python test_format.py
```

## 🎯 设计原则

1. **少而精**: 3个工具，避免选择困难
2. **JSON优先**: 结构化输出，便于程序处理
3. **参数驱动**: 通过参数实现功能变化
4. **LLM友好**: 优化大模型使用体验
5. **向后兼容**: 保留所有原有功能

## 📈 为什么这样设计？

### 对标行业最佳实践
- **Claude官方**: 1-2个核心工具
- **Perplexity**: 3-4个功能工具
- **我们的设计**: 3个工具，符合最佳实践

### 解决LLM选择困难
- **工具越少，选择越简单**
- **参数驱动，功能完整**
- **示例丰富，使用直观**

### JSON格式的优势
- **结构化数据，便于解析**
- **程序友好，易于处理**
- **LLM理解更准确**
- **减少格式转换开销**

最终版本通过减少工具数量、统一JSON格式、简化参数配置，为LLM提供了更友好、更高效的搜索体验。