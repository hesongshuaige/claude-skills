# 飞书 bot（机器人）与 gateway（消息网关）

> **何时读取：** 模型直连已经通过，准备创建独立飞书应用、配置消息网关或分层验收时读取。

## 1. 前置安全门

- [ ] 用户已明确同意创建或绑定一个**新应用**。
- [ ] 当前 profile（隔离档案）没有复制旧应用凭据。
- [ ] 一份 profile 对应一个 App ID（应用编号）；同一应用不得同时连接两个网关。
- [ ] 已确定中国飞书用 `feishu`、国际版用 `lark`，不得凭地区猜测。
- [ ] 任何命令执行前已运行同入口的 `--help`（帮助）：`<HERMES> gateway --help`、`<HERMES> gateway setup --help`、`<HERMES> send --help`。

## 2. 两条创建路径

### 路径 A：Hermes 扫码创建（优先）

1. 用当前版本的 profile 选择方式运行：

   ```text
   <HERMES> <PROFILE_SELECTOR> gateway setup
   ```

2. 选择 Feishu / Lark（飞书国内版或国际版），再选择扫码自动创建新 bot（机器人）。
3. 把程序输出的授权 URL（网址）原样交给用户，或生成二维码；用户亲自扫码和确认。
4. 保持注册进程存活。设备码通常约十分钟过期，以屏幕实际到期时间为准。
5. 若必须通过断开的 SSH（远程连接）会话等待，在 Linux 上可按本机帮助确认后，用后台进程并同时重定向标准输入、输出和错误；示意：

   ```bash
   nohup <VERIFIED_SETUP_COMMAND> </dev/null >"<TEMP_LOG>" 2>&1 &
   ```

6. 临时日志可能含 App Secret（应用密钥）；只让授权人员查看，完成验证后立即安全删除。若进入聊天或普通日志，按泄露处理并轮换。

### 路径 B：开放平台手动创建

1. 用户在飞书开放平台创建企业自建应用。
2. 开启“机器人”能力。
3. 仅开通当前用途必需的应用 scope（权限范围），并发布/启用组织要求的应用版本。
4. 选择 websocket（长连接）事件接入，无需公网 IP（地址）或 webhook（回调地址）。
5. 用户在安全终端把新 App ID 和 App Secret 写进当前 profile 的 `.env`（环境密钥文件）；聊天和报告只写变量名。

如果 API（接口）报错返回 `required_scope`（所需权限）和 `console_url`（权限控制台链接），原样把 `console_url` 交给用户，由用户在当前新应用控制台确认；不要自行提升权限，也不要把它误判成用户授权失败。

## 3. 最小环境配置

```dotenv
FEISHU_APP_ID=<NEW_APP_ID>
FEISHU_APP_SECRET=<NEW_APP_SECRET>
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
FEISHU_ALLOWED_USERS=<ALLOWED_OPEN_ID_LIST>
FEISHU_GROUP_POLICY=allowlist
FEISHU_REQUIRE_MENTION=true
```

说明：

| 变量 | 决策 |
|---|---|
| `FEISHU_ALLOWED_USERS` | 必配白名单，只放明确授权的人；不要记录真实 open_id（用户标识）到仓库或交接文档。 |
| `FEISHU_GROUP_POLICY` | `disabled`（禁用）、`allowlist`（仅白名单）或经明确批准的 `open`（开放）；纯私聊用 `disabled`。 |
| `FEISHU_REQUIRE_MENTION` | 群聊默认 `true`，必须 `@`（提醒）机器人才响应。 |
| `FEISHU_CONNECTION_MODE` | 使用 `websocket`（长连接）。 |

修改 `.env` 或 `config.yaml` 后必须重启**当前 profile** 的网关。

## 4. 生命周期与日志

对每条命令先看对应 `--help`（帮助），再按顺序执行：

```text
<HERMES> <PROFILE_SELECTOR> gateway install
<HERMES> <PROFILE_SELECTOR> gateway start
<HERMES> <PROFILE_SELECTOR> gateway status
<HERMES> <PROFILE_SELECTOR> gateway restart
```

Linux 优先用户级 systemd（服务管理器），不用 root（超级用户）；如 SSH 注销后服务停止，再评估用户 linger（后台驻留），不要直接改成 root 服务。Windows 使用当前 Hermes 帮助明确支持的本机服务方式；若 `install/start` 不支持，就用前台 `gateway run` 做验收，不虚构持久服务。

日志位置以 `gateway status` 和 `hermes logs --help` 的输出为准。命名 profile 常见为其自身 `logs/gateway.log`，但不得把某个安装路径当成通用事实。成功信号至少包括当前 profile 名、正在连接飞书和 websocket 已连接。

## 5. 分层测试，逐层报告

| 层 | 操作 | 通过标准 |
|---|---|---|
| 1 模型 | 完成直连短答 | 正确模型/供应商返回预期文本。 |
| 2 网关 | `gateway status` 并看日志 | 当前 profile 的飞书长连接已建立。 |
| 3 出站 | 先 `send --help`，再向占位目标发送测试 | 指定用户收到且发送命令成功。 |
| 4 私聊 | 白名单用户给 bot 发消息 | 收到并正常回复。 |
| 5 群聊 | 拉入测试群并按策略 `@` 机器人 | 白名单、群策略和提醒规则都符合配置。 |
| 6 用户资源 | 仅在启用用户身份后进行 | 身份、授权、只读资源分别通过。 |

出站命令形状以本机帮助为准，例如：

```text
<HERMES> <PROFILE_SELECTOR> send --to feishu:<RECIPIENT_OPEN_ID> "Connectivity test"
```

任何一层失败，只报告该层与后续未验证层；不得把“网关在线”说成“私聊、群聊和用户资源都可用”。

## 6. 上线检查

- [ ] 一 profile 一新应用，无 App ID 抢占。
- [ ] 机器人能力已开启，应用权限最小化。
- [ ] websocket 长连接已配置。
- [ ] 白名单、群聊策略、提醒规则符合批准范围。
- [ ] 变更后已重启对应网关。
- [ ] 出站、私聊、群聊结果分层记录。
- [ ] `console_url` 如出现，只交给用户确认当前应用 scope，不自动授权。
