# skillup — 提示词入库流水线

把提示词背景资料做成飞书知识库文档的流水线：**提取原版 → 写优化版 + 设计要点 → 举一反三 6 个新场景 → 每个场景用 MiniMax-M3 / image-01 实测验证 → 全通过才上传飞书 → 更新索引**。

核心价值：**先验证再交付**。每个新场景提示词都跑真实模型验证，验证不过的标注"未通过验证"但保留，让你看到全貌。

## 触发

用户说 `skillup` / `/skillup` / "把这个提示词入库" 并贴了背景资料时触发。

## 流程

1. **提取**【背景】【原版提示词】【使用场景】
2. **判类型**：学习类（苏格拉底）/ 文案类 / 分析类 / 生图类
3. **写骨架**：背景 + 原版 + 优化版（保留人设、补硬约束）+ 设计要点 + 用法
4. **举一反三**：从配置的场景池里选 6 个场景，各写完整提示词
5. **实测**：文本类 M3 跑 3 轮（开场/答错/答对），生图类 image-01 出图
6. **上传**：跑 `upload.sh` 传飞书 + 更新索引
7. **交付**：文档链接 + 场景清单 + 未通过的场景（如有）

## 配置（必做）

skillup **不绑定任何特定飞书库**。需提供两个值：

**方式 A**：环境变量（写进 `~/.bashrc`）

```bash
export SKILLUP_SPACE_ID="<飞书知识库 space_id>"
export SKILLUP_INDEX_TOKEN="<索引页 file_token>"
```

**方式 B**：`~/.config/skillup.conf`

```
SKILLUP_SPACE_ID=...
SKILLUP_INDEX_TOKEN=...
```

另外需要：

- `lark-cli` 已装并 `lark-cli auth login`（user 身份）
- `MINIMAX_API_KEY` 环境变量，或 `~/.secrets/mm.env`（文件格式 `export MINIMAX_API_KEY=...`）

## 场景池（可替换）

默认两池 = 新媒体运营 + 私募股权 GP/LP（作者自用领域）。

**换成你的行业**：编辑 `REFERENCE.md §一`，把两个池表整表替换成你行业的全链路场景（关键是要覆盖你业务从 0 到变现/交付的每个环节），其他流程不变。

## 安装

```bash
# 安装到所有已检测到的平台（Claude Code / Codex / OpenClaw / Hermes / Agents）
bash install.sh --all

# 或仅装一个
bash install.sh --claude
```

详见 `SKILL.md` 和 `REFERENCE.md`。

## 兼容性

通过 Claude Code、Codex、OpenClaw、Hermes、Agents 五平台验证。

## 许可

MIT
