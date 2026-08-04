# Hermes profile（隔离档案）与模型配置

> **何时读取：** 新建或修复 Hermes Agent（智能体）的隔离档案、模型供应商、工作目录时读取；飞书接入前必须读完。

## 1. 先探测命令，不猜版本

任何实际命令执行前，先对本机同一路径运行 `--help`（帮助）。候选入口按顺序探测：

| 候选入口 | Linux（主路径） | Windows（兼容路径） |
|---|---|---|
| `PATH`（命令搜索路径）中的程序 | `command -v hermes && hermes --help` | `Get-Command hermes; hermes --help` |
| Hermes 自带虚拟环境 | 先定位安装目录，再运行 `<HERMES_VENV>/bin/python -m hermes_cli.main --help` | 先定位安装目录，再运行 `<HERMES_VENV>\Scripts\python.exe -m hermes_cli.main --help` |
| 用户提供的入口 | `"<HERMES_CMD>" --help` | `& '<HERMES_CMD>' --help` |

不要把示例虚拟环境路径写成唯一入口。确定入口后，本文用 `<HERMES>` 表示它。每到新层级继续检查，例如：

```text
<HERMES> profile --help
<HERMES> profile create --help
<HERMES> gateway --help
```

若本机帮助不支持本文参数，停止并按本机帮助调整，不要试错写配置。

本包 Python（脚本解释器）也必须先探测，不能固定写 `python`：Linux 依次试 `python3` → `python` → Hermes 虚拟环境的 `<HERMES_VENV>/bin/python`；Windows 依次试 `py -3` → `python` → `<HERMES_VENV>\Scripts\python.exe`。每个候选先运行 `--version`，把第一个成功且版本满足脚本要求的完整入口记为 `<PYTHON>`；后文所有本包脚本命令都必须先替换这个占位符。

## 2. 创建真正隔离的 profile（隔离档案）

1. 先列出现状：`<HERMES> profile list`；若同名档案已存在，展示现状，让用户选“修复、补全或停止”，不得覆盖。
2. 让用户确认档案名、显示名、职责和工作目录。
3. 用本机帮助显示的创建形式，例如：

   ```text
   <HERMES> profile create <PROFILE_NAME> --description "<ONE_LINE_ROLE>"
   ```

4. **禁止 `--clone`（克隆）或 `--clone-all`（完整克隆）复制飞书凭据。** 若确需复用非敏感规则，只复制逐项审查过的内容，并新建 `.env`（环境密钥文件）。
5. 创建后只核对结构和变量名，不打印值：

   ```text
   <PROFILE_DIR>/profile.yaml
   <PROFILE_DIR>/config.yaml
   <PROFILE_DIR>/.env
   <PROFILE_DIR>/SOUL.md
   <PROFILE_DIR>/skills/
   <PROFILE_DIR>/sessions/
   <PROFILE_DIR>/memories/
   <PROFILE_DIR>/workspace/
   ```

命名 profile 的选择参数或包装命令因版本而异。先看根帮助与 `profile --help`；只有帮助明确支持时才用 `-p <PROFILE_NAME>`，否则使用该版本生成的档案别名或环境选择方式。

## 3. 独立配置不会自动继承

每个 profile（隔离档案）有自己的 `config.yaml`。不要假定它继承全局模型配置；缺失时可能静默回退到内置供应商。

最小示例（全部是占位符）：

```yaml
model:
  default: <MODEL_NAME>
  provider: custom:<PROVIDER_NAME>
  base_url: https://<PROVIDER_API_HOST>/v1

providers:
  <PROVIDER_NAME>:
    base_url: https://<PROVIDER_API_HOST>/v1
    key_env: <MODEL_API_KEY_ENV_NAME>
    api_mode: chat_completions

terminal:
  cwd: <PROFILE_DIR>/workspace

approvals:
  mode: smart
```

核对表：

- [ ] `model.default` 是当前供应商真实支持的模型名。
- [ ] `model.provider` 的 `custom:<PROVIDER_NAME>` 与 `providers.<PROVIDER_NAME>` 完全对应。
- [ ] 两处 `base_url`（接口根地址）与供应商文档一致。
- [ ] `api_mode`（接口模式）由当前 Hermes 与供应商共同支持。
- [ ] `key_env`（密钥变量名）与 `.env` 左侧变量名逐字一致，包括大小写。
- [ ] `.env` 的密钥由用户在安全终端录入，不在聊天、命令参数或报告中出现。
- [ ] `terminal.cwd` 指向真实存在的 `workspace`（工作目录），占位符已经全部替换。
- [ ] Linux 上执行 `chmod 600 <PROFILE_DIR>/.env`；Windows 用当前用户的文件访问控制限制读取。

不要把 `api_key`（密钥值）直接写进 YAML（配置文件）。dotenv（环境变量文件）里的值如含空格或 `#`，按当前解析器规则正确加引号；行尾注释可能被当成值的一部分，优先独立写注释行。

## 4. 工作目录与上下文

`SOUL.md`（人格文件）在 profile 根目录存在时独立加载；`AGENTS.md`（项目执行规则）只从当前 `cwd`（工作目录）读取。因此：

1. 创建 `<PROFILE_DIR>/workspace`。
2. 把 `AGENTS.md`、`README.md`、`PROJECT.md` 放入该目录。
3. 把 `terminal.cwd` 设置为该目录的绝对路径；路径可因机器变化，不能保留 `<PROFILE_DIR>` 或大小写错误的占位符。
4. 启动后回读当前工作目录验证，而不是凭文件存在推断已加载。

Linux 路径区分大小写，通常使用 `/`；Windows 盘符路径可用正斜杠以减少转义。Windows 向 Linux 传中文内容时，使用 UTF-8（通用中文编码）文件上传，不把正文塞进 PowerShell（命令行）到 SSH（远程连接）的参数。

## 5. 网关前的模型测试：这是人工受控风险门

> **醒目警告：`-z` / `--oneshot`（一次性执行）会自动绕过命令审批。** 当前 Hermes 帮助和 `hermes_cli/oneshot.py`（一次性执行源码）还确认：普通 `-z` 会照常加载当前目录规则、身份、记忆、技能和工具。因此绝不能在普通 profile、业务 workspace 或含不可信规则的 cwd 中把裸 `-z` 称为“安全测试”。

先用只读验证器的模型阶段核对 profile 配置，不读取密钥值。实际语法已经由脚本 `--help` 核实：

```text
<PYTHON> <AGENTGO_DIR>/scripts/validate_agent_profile.py --stage model <PROFILE_DIR>
```

`--stage model` 是创建飞书应用前的前门，只检查档案、模型供应商、`key_env`（密钥变量名）和工作目录等模型阶段条件，不要求尚未生成的模板文件或飞书变量。四个模板生成且飞书配置完成后，再运行完整验收：

```text
<PYTHON> <AGENTGO_DIR>/scripts/validate_agent_profile.py --stage full <PROFILE_DIR>
```

省略 `--stage` 默认也是 `full`（完整阶段）；不要在模板和飞书尚未完成时用默认/full 的预期失败替代模型前门。完整阶段还会扫描 `SOUL.md`、`AGENTS.md`、`README.md`、`PROJECT.md` 四份上下文文件中的凭据、持有者令牌和私钥残留，并要求 `FEISHU_ALLOWED_USERS` 非空；这些错误不能用交接说明豁免。

再查看 `<HERMES> --help`、`<HERMES> chat --help` 和 `<HERMES> tools list --help`。推荐做法是**人工守在交互终端**，进入新建的空白临时 cwd，显式指定模型与供应商，并使用：

- `--safe-mode`：禁用用户配置、`AGENTS.md`/`SOUL.md`、记忆、预加载技能、插件和 MCP（外部工具协议）；它会忽略 profile 模型配置，所以必须显式传 `--model` 与 `--provider`。
- `--toolsets safe`：当前源码仅含只读网页/视觉和图片生成能力，不含终端、文件写入或代码执行；执行前仍要用本机工具列表复核。
- 不带 `-z`、`--quiet`、`--yolo` 或 `--accept-hooks`；在交互会话中手工输入 `Reply with exactly: OK` 并观察全过程。

命令形状经当前帮助核实如下；`<PROFILE_SELECTOR>` 仍以本机帮助为准：

```text
<HERMES> <PROFILE_SELECTOR> chat --safe-mode --toolsets safe --model <MODEL_NAME> --provider <PROVIDER_NAME>
```

Linux 用 `mktemp -d` 创建空目录并从该目录启动；Windows 用 `New-Item -ItemType Directory` 创建空临时目录并 `Push-Location` 进入。测试前确认目录为空、目标是新建 profile，且没有 skills（技能）、hooks（钩子）或业务文件。`--safe-mode` 会忽略用户配置但仍可读取环境凭据；密钥必须来自当前 profile 的安全环境，不能出现在参数里。

若使用 `custom:<PROVIDER_NAME>`（自定义供应商），`--safe-mode` 会连同其配置映射一起忽略，可能无法解析供应商。此时不要为了让测试跑通而退回裸 `-z`：改在新建空 profile、空 cwd、无 skills/hooks 的人工交互终端中使用 `--ignore-rules --toolsets safe`，先核对实际工具列表不含终端、文件写入、代码执行和 MCP 工具，再输入短答。该路径不能完全消除启动侧自定义项，必须在报告中标为“人工受控风险门”，不能声称完全隔离。

只有无人值守环境确有必要时，才可在同样的空 cwd、`--safe-mode --toolsets safe --model ... --provider ...` 隔离组合后使用 `-z`；仍须把它标为“审批已绕过”的受控风险测试，并由操作者确认 safe 工具集的本机实际内容。无法复核工具集合时，不得使用 `-z`，改用上面的人工交互门。

通过标准：

- [ ] 进程退出成功，只返回预期短答。
- [ ] 日志所示模型与供应商等于本档案配置。
- [ ] 没有 `401`（鉴权失败）、未知供应商或默认模型回退。
- [ ] 输出和日志没有密钥值。

失败就停止飞书和 gateway（消息网关）步骤，先修复模型。连接上飞书不等于智能体可用。

## 下一步与相关资料

- 模型和 profile 通过后，进入[飞书机器人与消息网关](feishu-bot-and-permissions.md)。
- 生成工作目录文件时读取[上下文文件与提示词](context-files-and-prompts.md)。
- 正式验收前运行[只读 profile 验证器](../scripts/validate_agent_profile.py)。
- 授权网址必须运行[飞书授权网址验证器](../scripts/validate_feishu_url.py)，不能靠人工目测。
