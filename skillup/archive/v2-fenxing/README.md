# skillup v2（分型版）

> **v2 分型版**（2026-07-21）。最新版是 v3（仓库根目录）。

## 这个版本的特点

- **A/B 分型**：简单类（单轮，主力）/ 复杂类（多轮诊断，砍单轮简化或劝退做 agent）
- **致命硬伤制**：评审只看致命硬伤（删了打分，实证打分不收敛）
- **4 池**：新媒体运营 / 私募股权 GP-LP / 人事行政 / 财务管理
- **node_token**：新条目链接用 NODE_TOKEN 拼

## 比 v1 多 / 比 v3 少

- 比 v1 多：A/B 分型、4 池（加人事/财务）、评审删打分改硬伤制、node_token、索引 9 类
- 比 v3 少：身份节、writing-skills 方法论、硬伤清单单一来源

适合：想要 A/B 分型但不需要身份节和方法论的人。

## 安装（从仓库根目录）

```bash
bash scripts/install.sh --version v2 --claude    # 或 --codex / --all
```

## 配置

同主 README：`SKILLUP_SPACE_ID` / `SKILLUP_INDEX_TOKEN`（env 或 `~/.config/skillup.conf`），另需 lark-cli + `MINIMAX_API_KEY`。
