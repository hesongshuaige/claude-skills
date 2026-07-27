---
name: skillyes
description: Use when 用户说 /skillyes / "帮我找个提示词" / "不知道用啥提示词" / "这个该用哪个提示词"，要从飞书「AI提示词工程库」找一个对症的提示词拿来即用。也用于想学这类问题的提示词框架（脚手架渐隐·跨次记忆）。不用于把提示词入库（那是 skillup）；不用于替用户执行提示词（只给+教，不替跑）。
---

# skillyes — 提示词出库查找 + 学习教练

## 何时用 / 何时不用
- **用**：遇到问题不知道用哪个提示词，想从飞书库找对症的拿来即用 + 学这类框架。
- **不用**：要把提示词入库 → `/skillup`；要替你执行提示词（只给+教，不替跑）。

## 流程（6 步）
1. **调起**：用户 `/skillyes` 或"帮我找个提示词" + 贴问题。
2. **澄清**：问题太模糊（场景/任务/输出不明）→ 反问 1 句（给 2-3 候选意图）。反问 1 次仍模糊 → 按最可能类别给 1 条 + 标注"按我猜的"。
3. **匹配**：跑 `scripts/fetch_index.sh` 拉索引页全文 → 读条目 6 字段 + 9 类标签 → 提取用户问题意图（场景+任务类型）→ **先定 9 类之一**（跨类按主要动词定主类，次类带延伸）→ 类内按 6 字段（关键词/干啥/什么时候用）语义打分 → top1 最佳 + top2-3 同类。
4. **呈现（拿来即用）**：①最佳名 + 一句话理由 ②**提示词全文**（⚠️ node_token **不能**直接 fetch：先 `wiki +node-list --space-id "$SKILLYES_SPACE_ID" --page-all` 查该条 obj_token，再 `markdown +fetch`，细则见 REFERENCE §五）③飞书链接 `https://my.feishu.cn/wiki/{node_token}` ④一行"同类还有 X、Y"。
5. **教学（默认样例+变式对比）**：拆骨架（角色/任务/约束/输出格式）→ 抽「这类通用模板」→ 拉 2-3 同类标「不变的本质 vs 可变的皮」→ 1 组「烂问法 vs 好问法」对比 → 按 `progress.json` 阶段给抄/填空/独立写 → 末尾问"想深入吗"→ 同意则升级真费曼/练习式。细则见 REFERENCE §三。
6. **兜底**：无匹配 → 坦诚"库里没对症的"→ 推最接近 1 条 → 问"要不要 `/skillup` 造一条？"。

## progress.json（跨次记忆）
- 路径：与本 SKILL.md 同目录的 `progress.json`（首次教学后创建）。
- 阶段判定：同类被**呈现给用户**（第 4 步）的次数 = 阶段（封顶 3）；跳过教学也算接触。
- 每次第 4 步呈现后，更新该类阶段 + 最近日期。schema 见 REFERENCE §四。

## 飞书库（配置 env/conf，不硬编码）
- space_id = `$SKILLYES_SPACE_ID`、索引页 file_token = `$SKILLYES_INDEX_TOKEN`（fetch 索引页用）—— 两值从环境变量或 `~/.config/skillyes.conf` 读，未配则 `scripts/fetch_index.sh` 报错退出（配置见 README）。
- ⚠️ 单条提示词的 node_token 从索引页该条 🔗链接里抽；fetch 单条全文用该条的 obj_token（=file_token），**别拿 node_token 去 fetch**。

## 失败兜底
- 飞书 CLI 连不上：明说 → 凭对库的记忆给方向性建议 → 标"待联网验证"。
- 多条同分：取关键词重合度最高；并列给 2 条让用户选。

## 不可违背的硬要求
1. 匹配前先 `export PATH="$HOME/.npm-global/bin:$PATH"`（lark-cli 在这，非交互 shell 默认找不到）。
2. 第 4 步**必贴全文**（用户痛点就是"不想翻飞书"）。
3. 教学模块默认样例+变式对比（5-8 分钟）；真费曼/练习式是**可选升级**，用户明说要才切。
4. `progress.json` 每次第 4 步后**必更新**（跨次记忆的命脉）。
5. 无匹配必走"引导 skillup"（闭环），不硬推不合适的。

## 本 skill 文件
- SKILL.md（本文件）/ REFERENCE.md（§一 9类速查 + §二 匹配打分 + §三 学习法详解 + §四 progress schema + §五 lark-cli/token坑）/ scripts/fetch_index.sh / progress.json（运行时生成）
- 配置：`$SKILLYES_SPACE_ID` / `$SKILLYES_INDEX_TOKEN`（env 或 `~/.config/skillyes.conf`，见 README）
