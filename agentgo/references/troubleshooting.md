# AgentGo 故障排查

> **何时读取：** 任一模型、飞书网关、用户授权、上下文加载或跨系统传输步骤失败时读取；先定位失败层，不随机改多处。

任何修复命令执行前，先运行对应本机 `--help`（帮助）。每次只改一项，重测当前层；日志只摘错误类型和变量名，不贴密钥值。

| 现象 | 根因判断 | 最小修复与复测 |
|---|---|---|
| 模型返回 `401` 或 `Missing Authentication`（缺少鉴权） | `providers.<name>.key_env` 与 `.env` 左侧变量名不一致，或变量为空 | 只比较变量名和是否非空，不打印值；修正后重启当前会话，重跑模型直连。 |
| 日志显示回退到意外默认模型/供应商 | 独立 profile 的 `config.yaml` 没有完整 `model/providers`；它不继承全局配置 | 补全本档案配置，核对 `provider` 引用，再直连测试。 |
| `unknown provider`（未知供应商） | `model.provider` 拼写、`custom:` 前缀或 `providers` 映射名不一致 | 逐字核对名称和本机 Hermes 支持格式，不靠猜测新增供应商。 |
| 网关报 App ID 已被占用、两个机器人互踢 | 两个 profile 复用了同一应用，常由 clone（克隆）凭据造成 | 停止新网关，为新 profile 创建独立应用；不得通过重试抢连接。 |
| 扫码链接失效 | 设备码约十分钟过期，或交互注册进程已经退出 | 重新发起；在 `tmux` / `screen` 持久交互终端中保持进程和标准输入，不关闭或重定向 stdin（标准输入）。 |
| SSH 断开后扫码进程退出 | `gateway setup` 是交互流程，却放进关闭标准输入的后台任务 | 先查 `tmux -h` 或 `screen --help`，在持久交互终端里重新运行并保持标准输入；不要使用关闭标准输入的后台方案。 |
| PowerShell 经 SSH 传中文变成 `?` 或乱码 | 中文正文经过命令参数/管道编码转换 | 本地生成 UTF-8 文件，通过 SFTP/SCP（文件上传）传字节；远端按 UTF-8 回读。 |
| 改 `.env`/`config.yaml` 后行为不变 | 当前 profile 网关未重启，或重启了错误档案 | 核对 profile 和服务名，运行本机帮助支持的 `gateway restart`，再看新日志时间。 |
| 群聊不回复 | 规则过滤或事件未到达 | 严格按顺序查：是否 `@` 机器人 → `FEISHU_REQUIRE_MENTION` → `FEISHU_GROUP_POLICY` → 发送者是否在 `FEISHU_ALLOWED_USERS` → 应用事件/权限。 |
| 私聊可用，用户知识库失败 | 把 bot 权限误当 user 授权，或反之 | 先查应用 scope，再查用户 consent 与 `auth status`，最后用显式 `--as user` 做只读测试。 |
| 错误带 `required_scope`/`console_url` | 当前应用缺少 scope，不一定是用户没授权 | 原样交给用户在当前新应用控制台确认；发布后再测。不得自动加权限。 |
| lark-cli 结果属于旧应用或错误身份 | lark-cli profile 绑定了旧 App ID、错误 Hermes profile，或默认身份不符 | 用 `whoami`、配置显示和档案名交叉核对；用户确认后重新绑定当前新应用。 |
| 设备码授权一直失败 | verification URL（验证网址）被聊天客户端截断、转义或自行拼接修改 | 原样转发完整 URL；必要时用工具对原 URL 生成二维码；过期后重新发起。 |
| `auth status` 有令牌但资源仍拒绝 | 应用 scope 未开、资源未共享，或调用没显式 `--as user` | 分开检查应用权限、资源访问权和调用身份；不静默降级成 bot。 |
| `AGENTS.md` 存在但规则未加载 | 文件不在当前 `cwd`，`terminal.cwd` 指错，或用了 `--ignore-rules`/`--safe-mode` | 修正 `terminal.cwd`，把文件放在该目录根部，开新会话复述规则验证。 |
| 验证器报空凭据 | `.env` 中变量存在但值为空、只有空白或无效占位符 | 用户在安全终端重新录入真实值；验证只报告变量名。 |
| dotenv（环境变量文件）值异常 | 引号未闭合、值含空格/`#`、行尾注释被当成值 | 按当前解析器规则加引号；注释放独立行；不要把密钥打印出来诊断。 |
| `terminal.cwd` 不存在 | `<PROFILE_DIR>` 等占位符未替换，或 Linux 路径大小写错误 | 使用本机真实绝对路径，逐级检查目录与大小写；不要写死另一台机器路径。 |
| Windows 首次配置报模型列表错误 | YAML（配置文件）带 UTF-8 BOM（字节顺序标记） | 另存为无 BOM 的 UTF-8，再重启会话。 |
| 日志或聊天出现密钥 | 凭据已泄露，不再可信 | 立即停用相关凭据；在供应商/飞书控制台轮换或吊销；清理含密钥临时日志；更新安全终端中的 `.env`；重启并分层复测。 |

当前 `gateway setup` 是交互命令，不能套用关闭 stdin 的后台方式。只有未来本机 `--help` 明确提供独立的非交互子命令时，该**独立子命令**才可按其帮助使用 `nohup`（后台保持）并关闭 stdin；这条例外永远不能套用到交互式 `gateway setup`。

## 固定排查顺序

1. **入口层：** 核对实际命令路径、profile 和 `--help`。
2. **模型层：** 独立配置、供应商引用、`key_env`、直连短答。
3. **应用层：** 当前新 App ID、机器人能力、应用 scope、websocket（长连接）。
4. **网关层：** 当前 profile 的服务状态、最新日志、App ID 抢占。
5. **消息层：** 出站 → 私聊 → 群聊提醒/策略/白名单。
6. **用户授权层：** lark-cli 绑定 → 应用 scope → 用户 consent → `--as user` 只读。
7. **上下文层：** `terminal.cwd` → `AGENTS.md` 位置 → 新会话实际加载。

## 报告格式

```text
失败层：<模型/应用/网关/消息/用户授权/上下文>
已确认：<不含密钥的事实>
根因：<证据支持的原因或“尚未确认”>
已执行：<一项最小修复>
复测：<通过/失败/未执行>
影响：<后续哪些层仍未验证>
下一步：<需要用户确认或可安全继续的动作>
```

## 下一步与相关资料

- 模型和 profile 错误回到[档案与模型](hermes-profile-and-model.md)。
- 飞书消息错误回到[机器人与网关](feishu-bot-and-permissions.md)。
- 用户资源错误回到[lark-cli 用户授权](lark-user-authorization.md)。
- 修复后运行[只读 profile 验证器](../scripts/validate_agent_profile.py)。
