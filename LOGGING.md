# 日志级别最佳实践

## 📊 当前日志级别设计

### 日志级别使用原则

**DEBUG** - 调试信息
- 详细的参数信息
- API请求参数
- 中间处理步骤
- 仅在开发或故障排查时使用

**INFO** - 重要信息
- 搜索开始和完成
- 关键操作结果
- 业务流程里程碑
- 生产环境默认级别

**WARNING** - 警告信息
- 参数验证失败
- 非致命错误
- 配置问题
- 需要注意但不影响功能的情况

**ERROR** - 错误信息
- API调用失败
- 异常处理
- 严重错误
- 需要立即关注的问题

## 🔧 优化后的日志输出

### 生产环境 (INFO级别)
```
2024-01-15 10:30:15 - tencent-cloud-search - INFO - 搜索完成: 'Python机器学习教程' -> 10 条结果
2024-01-15 10:30:20 - tencent-cloud-search - INFO - 搜索完成: 'React hooks' -> 5 条结果
```

### 调试环境 (DEBUG级别)
```
2024-01-15 10:30:15 - tencent-cloud-search - DEBUG - 开始搜索请求: query='Python机器学习教程', num=10, offset=0, format=text, mode=0, site=None
2024-01-15 10:30:15 - tencent-cloud-search - DEBUG - 创建腾讯云客户端...
2024-01-15 10:30:15 - tencent-cloud-search - DEBUG - 请求参数: {'Query': 'Python机器学习教程', 'Num': 10, 'Offset': 0, 'Mode': 0}
2024-01-15 10:30:15 - tencent-cloud-search - DEBUG - 发送搜索请求...
2024-01-15 10:30:16 - tencent-cloud-search - DEBUG - 收到API响应
2024-01-15 10:30:16 - tencent-cloud-search - INFO - 搜索完成: 'Python机器学习教程' -> 10 条结果
2024-01-15 10:30:16 - tencent-cloud-search - DEBUG - 结果格式化完成，格式: text
```

## 🎯 日志设计原则

### 1. 适当的粒度
- **避免过度日志**: 不要记录每个步骤的详细信息
- **关键信息优先**: 重要的业务事件使用INFO级别
- **调试信息分离**: 详细调试信息使用DEBUG级别

### 2. 有意义的信息
- **上下文相关**: 日志消息包含足够的上下文信息
- **可操作性**: 错误日志提供解决问题的线索
- **一致性**: 使用统一的格式和术语

### 3. 性能考虑
- **避免敏感信息**: 不要记录密码、密钥等敏感数据
- **控制输出量**: 避免大量重复或无意义的日志
- **异步记录**: 在高并发场景下考虑异步日志记录

## 🔍 日志配置示例

### 开发环境
```bash
export LOG_LEVEL=DEBUG
```

### 生产环境
```bash
export LOG_LEVEL=INFO
```

### Claude Desktop配置
```json
{
  "mcpServers": {
    "tencent-cloud-search": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "your-secret-id",
        "TENCENTCLOUD_SECRET_KEY": "your-secret-key",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 📈 监控和分析

### 关键指标
- 搜索请求频率
- 平均响应时间
- 错误率
- 结果数量分布

### 日志分析
- 使用ELK Stack或类似工具分析日志
- 设置告警规则监控异常情况
- 定期审查日志质量和相关性

## 🚀 持续改进

### 定期审查
- 检查日志级别是否合理
- 优化日志消息的清晰度
- 移除不再需要的调试日志

### 反馈循环
- 根据运维反馈调整日志策略
- 基于故障排查经验补充关键日志点
- 保持日志文档的更新