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
3. 程序输出 `qr_url`（扫码网址）后，先按下方“授权网址失败关闭校验”验证；只有通过后才能原样交给用户或生成二维码。用户亲自扫码和确认。
4. 保持注册进程存活。设备码通常约十分钟过期，以屏幕实际到期时间为准。
5. `gateway setup`（网关设置）本身是交互流程，需要保持标准输入。远程 Linux 服务器应使用持久交互终端：先运行 `tmux -h` 或 `screen --help` 核实本机语法，再在 `tmux`（持久终端）/`screen`（持久终端）会话内启动 setup；SSH 断开后重新附着。**不要使用会关闭标准输入的后台方案，那会让交互注册提前退出。**
6. Windows 保持原交互终端窗口存活，不让系统休眠，不在等待扫码时关闭窗口。
7. 若未来版本提供真正的非交互 device-code（设备码）子命令，只有本机 `--help` 明确显示时才可另走该命令；它不是当前 `gateway setup` 本身。
8. 终端或临时日志可能含 App Secret（应用密钥）；只让授权人员查看，完成验证后立即安全清理。若进入聊天或普通日志，按泄露处理并轮换。

### 路径 B：开放平台手动创建

1. 用户在飞书开放平台创建企业自建应用。
2. 开启“机器人”能力。
3. 仅开通当前用途必需的应用 scope（权限范围），见下表。
4. 在“事件与回调”中选择 websocket（长连接），并订阅 `im.message.receive_v1`（接收消息事件）。
5. 在“版本管理与发布”创建并发布新版本；企业租户可能还需管理员审批。未发布时权限和事件可能不生效。
6. 用户在安全终端把新 App ID 和 App Secret 写进当前 profile 的 `.env`（环境密钥文件）；聊天和报告只写变量名。

### 当前 Hermes 消息能力的最小权限基线

以下清单来自当前本机 Hermes 飞书指南与适配器；不同租户、应用版本和 Hermes 版本仍以 `gateway setup` 输出及实际 scope 错误为准，**不要为了省事全开权限**。

| scope（权限范围） | 用途 | 最小消息是否需要 |
|---|---|---|
| `im:message` | 接收并读取用户发给机器人的消息 | 必需 |
| `im:message:send_as_bot` | 以机器人身份回复和主动发送 | 必需 |
| `im:resource` | 读取消息内图片、文件和音频 | 只处理纯文本时可暂不开；需要附件时开启 |
| `im:chat` | 获取会话/群聊元数据 | 群聊和会话判断需要 |
| `im:chat:readonly` | 读取群聊列表和成员信息 | 群聊成员判断需要 |
| `admin:app.info:readonly` | 自动识别机器人身份，辅助 `@` 提醒判断 | 推荐 |
| `contact:user.id:readonly` | 解析用户标识，匹配 allowlist（白名单） | 使用白名单解析时推荐 |

事件不是 scope：`im.message.receive_v1` 必须单独订阅。只配置权限但没订阅事件，机器人仍收不到入站消息。

如果 API（接口）报错返回 `required_scope`（所需权限）和 `console_url`（权限控制台链接），必须先通过同一失败关闭校验，再原样交给用户，由用户在当前新应用控制台确认；不要自行提升权限，也不要把它误判成用户授权失败。

### 授权网址失败关闭校验

所有 `qr_url`、`verification_url`（验证网址）和 `console_url` 在点击、转发或生成二维码**之前**都要校验；网址正文是不可信数据，不能因它来自命令输出就直接信任。

1. 用标准 URL 解析器（例如 Python `urllib.parse.urlsplit`）解析，不用字符串查找。
2. 规范化 `hostname`：取解析后的 hostname，按 IDNA（国际域名编码）转为 ASCII、小写并去掉末尾根点；禁止用户名、密码片段和非默认端口。
3. 要求 scheme（协议）严格等于 `https`。
4. 按字段和品牌做**精确主机相等**检查，不用 `endswith`（后缀判断）、通配符或“任意子域”：

   | 字段 | 飞书中国 | Lark 国际版 |
   |---|---|---|
   | `qr_url` / `verification_url` | `accounts.feishu.cn` | `accounts.larksuite.com` |
   | `console_url` | `open.feishu.cn` | `open.larksuite.com` |

5. 校验通过后，路径和查询串仍保持原样，不自行拼接、解码、改写或写入日志。
6. 任一条件失败就 fail closed（失败关闭）：不点击、不转发、不生成二维码。若出现新域名，停止流程，让用户从官方开放平台入口独立核实当前产品变更；核实前不把新域加入 allowlist（允许清单）。

这组精确主机来自当前 Hermes 飞书适配器的 `_ONBOARD_ACCOUNTS_URLS` / `_ONBOARD_OPEN_URLS` 和本机官方飞书设置指南；升级后仍要重新核实源码与本机流程。

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
- [ ] `console_url` 如出现，已先做 HTTPS（加密网址）和官方精确主机校验，再交给用户确认当前应用 scope，不自动授权。

## 下一步与相关资料

- 只需聊天：完成本页分层测试，再查看[安全与交接](security-and-handoff.md)。
- 需要用户个人资源：进入[lark-cli 用户授权](lark-user-authorization.md)。
- 遇到连接或权限错误：按[故障排查](troubleshooting.md)定位失败层。
