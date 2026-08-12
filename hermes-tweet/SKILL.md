---
name: hermes-tweet
description: Use Hermes Tweet when a Hermes Agent workflow needs X/Twitter research, post or reply reads, user lookup, follower exports, monitoring, or explicitly approved posting actions.
---

# Hermes Tweet

Hermes Tweet 是 Hermes Agent 的 X/Twitter 插件。它提供离线能力发现、公开读取，
以及默认关闭的导出、监控和写入能力。

## 安装

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

## 环境变量

- `XQUIK_API_KEY`：所有实时 API 调用都需要。
- `HERMES_TWEET_ENABLE_ACTIONS=true`：导出、监控、私有读取和写入额外需要。

不要把 API Key、账号材料或会话内容写入技能文件、README 或共享笔记。

## 工具路由

| 工具 | 用途 |
| --- | --- |
| `tweet_explore` | 离线检索可用端点，不发送 API 请求 |
| `tweet_read` | 调用目录中的公开读取端点 |
| `tweet_action` | 调用导出、监控、私有读取或写入端点，默认关闭 |

## 使用流程

1. 先调用 `tweet_explore`，用自然语言描述目标。
2. 只使用目录返回的 `/api/v1/...` 路径。
3. 公开检索和时间线读取使用 `tweet_read`。
4. 导出、监控、私有读取或写入使用 `tweet_action`。
5. 输出摘要时保留来源链接、账号、时间和查询条件。
6. 写入前复核账号、目标和最终文本，并取得用户明确确认。

没有 API Key 时，只能使用离线的 `tweet_explore`。没有
`HERMES_TWEET_ENABLE_ACTIONS=true` 时，不要尝试 `tweet_action`。

## 适用场景

- 舆情与趋势观察
- 发布前的 X/Twitter 账号资料检查
- 帖子、回复、用户和粉丝数据整理
- 需要人工确认的社交媒体动作流程

项目地址：<https://github.com/Xquik-dev/hermes-tweet>
