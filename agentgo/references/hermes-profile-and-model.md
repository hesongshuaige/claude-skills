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

## 5. 网关前的模型直连测试

先查看一次性调用帮助：`<HERMES> --help`。再用当前版本支持的 profile 选择方式执行短测试，例如：

```text
<HERMES> <PROFILE_SELECTOR> -z "Reply with exactly: OK"
```

通过标准：

- [ ] 进程退出成功，只返回预期短答。
- [ ] 日志所示模型与供应商等于本档案配置。
- [ ] 没有 `401`（鉴权失败）、未知供应商或默认模型回退。
- [ ] 输出和日志没有密钥值。

失败就停止飞书和 gateway（消息网关）步骤，先修复模型。连接上飞书不等于智能体可用。
