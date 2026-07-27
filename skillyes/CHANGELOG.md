# skillyes CHANGELOG

## v1.0.0（2026-07-27）— 首个仓库版

提示词出库查找 + 学习教练，跟 skillup（入库）对称。

**核心能力**：
- 6 步流程：调起 / 澄清 / 匹配 / 呈现（贴全文）/ 教学 / 兜底
- 匹配靠飞书索引页 6 字段语义匹配（不翻每条全文，快）
- 学习模块：样例+变式对比（默认 5-8 分钟）+ 真费曼/练习式（可选）+ 脚手架渐隐（`progress.json` 跨次记忆：抄 → 填空 → 独立写）
- 无匹配兜底：坦诚 + 引导 `/skillup` 造一条（找→造闭环）

**工程**：
- 5 平台复制式 `install.sh`（Claude Code / Codex / OpenClaw / Hermes / Agents）
- 去硬编码：`SKILLYES_SPACE_ID` / `SKILLYES_INDEX_TOKEN`（env 或 `~/.config/skillyes.conf`）
- Hermes/OpenClaw 不识别 skills 目录时的 AGENTS.md 注入法见 README
