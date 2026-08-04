# lark-cli（飞书命令行工具）用户授权

> **何时读取：** 只有智能体要访问用户个人有权访问的知识库、文档、云盘、多维表格、日历或邮箱时读取；纯聊天机器人无需用户授权。

## 1. 先分清三层

| 层 | 作用 | 失败时处理 |
|---|---|---|
| 应用 scope（权限范围） | 当前新应用在开放平台被允许调用哪些接口 | 查看 `required_scope` 和 `console_url`，由用户在应用控制台开通并发布。 |
| bot（机器人）身份 | 收发消息，访问机器人有权看到的资源 | 检查机器人能力、应用权限、资源是否分享给机器人。 |
| user（用户）身份 | 代表授权用户访问其个人资源 | 检查用户 consent（同意授权）、令牌状态和显式身份参数。 |

应用 scope 已开不等于用户已 consent；用户已授权也不能绕过应用 scope。权限报错时不得在两种身份间静默降级。

## 2. 是否需要绑定

- 只收发飞书消息：不强制安装或配置 lark-cli；保持 bot-only（仅机器人身份）。
- 访问个人资源：将 lark-cli 绑定到**当前 profile 的当前新应用**，选择 user-default（默认用户身份）。
- 若用户不确定：选择 bot-only；需要个人资源时再明确升级。

绑定前记录但不展示 App ID 值，并核对：Hermes profile 名、飞书应用显示名、lark-cli profile 名三者都指向本次新建实例。禁止绑定旧应用或另一个 profile。

## 3. 先看帮助，再绑定身份策略

每条实际命令执行前，对同一路径运行 `--help`（帮助）：

```text
lark-cli --help
lark-cli config --help
lark-cli config bind --help
lark-cli auth --help
lark-cli auth login --help
lark-cli auth qrcode --help
lark-cli whoami --help
```

用户确认绑定对象与身份后，按本机帮助执行。当前常见形状：

```text
lark-cli --profile <LARK_PROFILE> config bind --source hermes --app-id <NEW_APP_ID> --identity bot-only
lark-cli --profile <LARK_PROFILE> config bind --source hermes --app-id <NEW_APP_ID> --identity user-default
```

`bot-only` 更安全，不能冒充用户；`user-default` 允许用户身份，必须由用户明确同意。若同一应用只调整身份政策，先看 `config strict-mode --help`，不要无故重新绑定。App Secret（应用密钥）若需输入，使用工具支持的标准输入或安全存储，不能放命令参数。

## 4. device-code（设备码）分步授权

适合智能体分回合交互的流程：

1. 用户确认所需资源域和最小 scope（权限范围）。
2. 发起但不阻塞等待，要求结构化结果：

   ```text
   lark-cli --profile <LARK_PROFILE> auth login --no-wait --json --domain <READ_ONLY_DOMAIN>
   ```

3. 从结果读取 verification URL（验证网址）、device code（设备码）和到期信息。**URL 必须作为不透明字符串原样转发，不拼接、不解码重组、不删查询参数。**
4. 如用户需要二维码，先看帮助，再把原 URL 传入：

   ```text
   lark-cli auth qrcode "<EXACT_VERIFICATION_URL>" --output <RELATIVE_QR_PATH>
   ```

5. 用户打开链接或扫码并亲自同意授权；智能体暂停，不假装已完成。
6. 用户确认后，用第一次返回的设备码轮询完成：

   ```text
   lark-cli --profile <LARK_PROFILE> auth login --device-code <EXACT_DEVICE_CODE> --json
   ```

7. 设备码过期就重新发起第 2 步，不复用旧 URL 或旧码。

## 5. 验证身份与授权

先只读检查：

```text
lark-cli --profile <LARK_PROFILE> auth status --json --verify
lark-cli --profile <LARK_PROFILE> whoami --as user
lark-cli --profile <LARK_PROFILE> auth scopes --json
```

用户资源调用必须显式写 `--as user`（以用户身份），即使默认是 user-default 也不能靠隐式行为。具体资源命令先运行其 `--help`，必要时用 `schema`（接口结构查询）检查参数、风险和 scope。

验收顺序：

- [ ] `auth status`（授权状态）显示当前 lark-cli profile 的有效用户令牌。
- [ ] `whoami --as user` 显示当前应用、当前 profile 和用户身份相符；报告时不抄真实标识。
- [ ] 对一个已授权资源执行只读查询，显式 `--as user`。
- [ ] 分别记录知识库与多维表格只读结果。
- [ ] 创建、更新、删除等写操作，只在用户对对象、范围和后果明确批准后执行；先用 `--dry-run`（只预演）时以命令帮助是否支持为准。

## 6. 常见边界

- `console_url`（权限控制台链接）解决应用 scope，不替代用户 consent。
- 再次登录不能修复未开通的应用 scope；提升应用权限也不能自动产生用户令牌。
- 机器人能看见某文档，不代表用户身份授权正确；反之亦然。
- lark-cli 当前 profile、Hermes profile 和新应用任一不一致，都先停止授权并重新核对绑定。
- 不把令牌、设备码结果全文、App ID 或用户 open_id（用户标识）写进仓库、交接和普通日志。
