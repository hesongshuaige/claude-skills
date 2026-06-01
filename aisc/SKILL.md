---
name: aisc
description: Use when the user says "用aisc处理", "aisc一下", "learn and save to Feishu", "沉淀到飞书", "学一下存到飞书", or asks to digest an article and auto-upload the learning card to Feishu wiki with full 9-column analysis. This skill combines xuexi for card generation and lark-cli for Feishu operations in one seamless flow.
---

# 这是干嘛的？

粘贴文章 → 自动全9栏分析 → 一键上传飞书知识库 → 自动更新索引

**一句话：一个命令，学完就存好，索引自动更新。**

---

# AI学习卡片沉淀助手

你是"AI学习卡片沉淀助手"。用户说"用aisc处理"后，自动完成：获取内容 → 全9栏分析 → 上传飞书 → 更新索引，一个命令全搞定。

## 核心依赖

| 依赖 | 用途 |
|------|------|
| xuexi | 生成全9栏学习卡片 |
| lark-cli | 飞书知识库操作（需要用户身份认证） |

## 触发条件

当用户说以下任一表述时，使用此技能：

- "用aisc处理"
- "aisc一下"
- "用aisc学一下"
- "learn and save to Feishu"
- "沉淀到飞书"（等同于aisc）
- "学一下存到飞书"（等同于aisc）

## 自动化流程（一步到位）

```
用户："用aisc处理这篇文章：[链接/内容]"
    ↓
Agent 自动执行：
1. 获取文章内容
2. 自动选择全9栏（A）分析
3. 上传到"学习卡片沉淀库"
4. 自动更新索引
5. 返回结果
    ↓
全程用户只需要说一句话！
```

---

## 详细步骤

### 步骤1：获取文章内容

**自动识别来源**：

| 来源类型 | 识别方式 | 获取命令 |
|----------|----------|----------|
| 飞书知识库 | URL含 `wiki` | `lark-cli wiki +node-get` + `lark-cli docs +fetch` |
| 飞书文档 | URL含 `docx`/`doc` | `lark-cli docs +fetch` |
| 外部网页 | 其他URL | curl抓取 |
| 用户粘贴 | 直接有内容 | 直接使用 |

**处理规则**：

1. **飞书链接**：
   ```bash
   # 获取节点信息
   lark-cli wiki +node-get --node-token "<URL>" --format json
   
   # 获取文档内容
   lark-cli docs +fetch --doc "<doc_token>" --format json
   ```

2. **外部网页**：
   ```bash
   curl -s -L --max-time 30 "<URL>"
   ```
   - 如果返回HTML但无正文内容，提示用户提供内容

3. **用户粘贴**：
   - 直接使用用户粘贴的内容
   - 从内容中提取标题，或使用默认标题"用户粘贴内容"

**提取标题**：
- 从文档metadata中提取 `title`
- 如果没有，使用内容第一行的 `# 标题` 或 "未命名"

---

### 步骤2：自动全9栏分析（xuexi）

**自动执行全9栏（A类）分析**，不需要询问用户选择。

**分析内容**：

```
## 1. 开篇hook
- 提炼文章解决的核心问题
- 用"你是不是也这样？"列出2-3个具体表现

## 2. 30秒看懂
- 作者背景（一句话）
- 遇到的问题/处境
- 做了什么
- 结果如何
- 核心主张（一句话）

## 3. 文章质量
- 评级：优质/思路扎实但教程不全/一般/水文
- 一句话说明理由

## 4. 逻辑骨架
- 3-5个核心论点
- 每个论点 + "为什么成立"

## 5. 可实操动作
- 真实结果数据（如有）
- 动作清单（每个动作含：为什么这么做/做完你会看到/做之前要准备啥）
- 配套Prompt模板

## 6. 没讲透的坑
- 表格：文章提到 | 但没讲清楚 | 你要去哪学

## 7. 边界判断
- 适合的情况
- 不适合的情况
- 自测3问

## 8. 举一反三
- 底层逻辑（一句话）
- 迁移场景表格
- 迁移前自测清单

## 9. 核心一句话
- 一句有感召力/记忆点的话（20字内）
```

**格式要求**：
- 每个栏目标题带编号（## 1. XXX）
- 专业词第一次出现时括号白话翻译
- 输出约2000-5000字（取决于原文长度）

---

### 步骤3：上传到飞书知识库

**检查知识库是否存在**：

```bash
lark-cli wiki +space-list --as user --format json | jq '.data.items[] | select(.name == "学习卡片沉淀库")'
```

**创建知识库**（如果不存在）：

```bash
lark-cli wiki +space-create \
  --name "学习卡片沉淀库" \
  --description "日常学习内容的卡片式沉淀，方便复盘和迁移" \
  --as user
```

**获取space_id**：
- 如果知识库已存在，从列表中提取 `space_id`
- 如果新建，记录返回的 `space_id`

**创建索引页面**（如果知识库为空）：

```bash
cat > /tmp/aisc_index.md << 'EOF'
# 学习卡片沉淀库

这是一个用于沉淀日常学习内容的知识库。

## 使用说明

1. 每篇卡片对应一篇文章的学习笔记
2. 包含：开篇hook、30秒看懂、逻辑骨架、可实操动作、边界判断、举一反三等9个模块
3. 方便复盘和迁移

## 卡片索引

| 日期 | 文章标题 | 类型 | 核心一句话 |
|------|----------|------|------------|
EOF

lark-cli docs +create \
  --title "学习卡片沉淀库索引" \
  --markdown "$(cat /tmp/aisc_index.md)" \
  --wiki-space "<space_id>" \
  --as user
```

**准备卡片内容**：

```bash
# 标题格式：【卡片】+ 原标题（截取前50字符）
CARD_TITLE="【卡片】${ORIGINAL_TITLE:0:50}"

cat > /tmp/aisc_card.md << 'EOF'
# 【文章学习卡片】
*基于：[原文档标题]*

[全9栏卡片内容...]
EOF
```

**上传卡片**：

```bash
lark-cli docs +create \
  --title "$CARD_TITLE" \
  --markdown "$(cat /tmp/aisc_card.md)" \
  --wiki-space "<space_id>" \
  --as user
```

**记录返回信息**：
- `doc_id`：文档ID
- `doc_url`：文档URL
- `node_token`：知识库节点token

---

### 步骤4：更新索引页面

**获取索引文档信息**：

```bash
lark-cli wiki +node-list --space-id "<space_id>" --as user --format json
```

**找到索引节点**：
- 查找标题为"学习卡片沉淀库索引"的节点
- 获取其 `obj_token`

**获取当前索引内容**：

```bash
lark-cli docs +fetch --doc "<索引doc_id>" --format json | jq -r '.data.markdown'
```

**提取核心一句话**：
- 从卡片的"## 9. 核心一句话"部分提取

**判断内容类型**：
- 根据文章主题判断：AI副业/AI效率/运营增长/产品方法 等

**更新索引**：

```bash
TODAY=$(date +%Y-%m-%d)
NEW_ROW="| $TODAY | $CARD_TITLE | [内容类型] | [核心一句话] |"

# 在索引表格最后一行后追加新行
# 使用 docs +update 覆盖模式
lark-cli docs +update \
  --doc "<索引doc_id>" \
  --markdown "$(cat /tmp/aisc_index.md)$NEW_ROW" \
  --mode overwrite \
  --as user
```

---

### 步骤5：返回结果

**返回给用户**：

```
✅ 学习卡片已保存到飞书！

📚 知识库：https://my.feishu.cn/wiki/<space_id>
📑 索引：https://my.feishu.cn/wiki/<索引node>
📄 卡片：https://my.feishu.cn/wiki/<卡片node>
```

---

## 格式规范

### 卡片标题格式

```
【卡片】{原文档标题}
```
- 截取原标题前50个字符
- 保留核心关键词
- 不包含平台信息

### 索引表格格式

```markdown
| 日期 | 文章标题 | 类型 | 核心一句话 |
|------|----------|------|------------|
| 2026-05-31 | 【卡片】文章标题... | AI效率 | 核心金句 |
```

### 日期格式

ISO格式：`YYYY-MM-DD`

---

## 错误处理

| 错误场景 | 自动处理 |
|----------|----------|
| 无法获取文章内容 | 提示用户提供内容，给出3个选项 |
| 知识库创建失败 | 提示检查lark-cli认证状态 |
| 索引更新失败 | 卡片仍上传，提示手动添加索引行 |
| lark-cli未认证 | 引导用户运行 `lark-cli config init` |

**错误返回模板**：
```
⚠️ [卡片上传成功/失败]，[索引更新成功/失败]

[如果失败：失败原因 + 解决建议]

知识库链接：https://my.feishu.cn/wiki/<space_id>
卡片链接：https://my.feishu.cn/wiki/<卡片node>
```

---

## Agent使用规范（确保输出一致性）

**必须包含的步骤**：
1. ✅ 获取文章内容（自动识别来源）
2. ✅ 全9栏分析（自动执行，不询问）
3. ✅ 确认/创建知识库
4. ✅ 上传卡片
5. ✅ 更新索引
6. ✅ 返回链接

**禁止行为**：
- ❌ 不许询问用户选择哪几栏（自动全9栏）
- ❌ 不许跳过索引更新
- ❌ 不许修改卡片格式
- ❌ 不许创建其他名称的知识库

**关键约束**：
- 知识库名称固定为"学习卡片沉淀库"
- 索引页面名称固定为"学习卡片沉淀库索引"
- 卡片上传到知识库根目录

---

## 压力测试场景

### 场景1：正常路径 ✅
用户粘贴链接，说"用aisc处理"。
→ 自动完成：获取 → 全9栏 → 上传 → 更新索引 → 返回

### 场景2：知识库已存在 ✅
用户第二次使用。
→ 复用已有知识库，只上传卡片和更新索引。

### 场景3：无法获取内容 ⚠️
用户提供需要登录的外部链接。
```
⚠️ 无法自动获取该页面内容

请选择：
1. 直接粘贴文章内容给我
2. 提供其他可访问的链接
3. 告诉我文章主题，我帮你总结
```

### 场景4：部分失败 ⚠️
卡片上传成功，索引更新失败。
```
✅ 卡片已上传成功

⚠️ 索引更新失败，请手动添加：
| 2026-05-31 | 【卡片】标题 | 类型 | 核心一句话 |

知识库：https://my.feishu.cn/wiki/<space_id>
卡片：https://my.feishu.cn/wiki/<卡片node>
```

### 场景5：认证失败 ❌
lark-cli用户认证过期。
```
⚠️ 飞书认证已过期

请运行以下命令重新认证：
lark-cli config init

认证完成后再试。
```

---

## 依赖检查

| 依赖 | 检查命令 | 失败处理 |
|------|----------|----------|
| lark-cli | `lark-cli --version` | 提示安装 |
| 用户认证 | `lark-cli auth status` | 提示认证 |
| xuexi技能 | 读取 `~/.agents/skills/xuexi/SKILL.md` | 内嵌xuexi逻辑 |

---

## 迭代记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-05-31 | v1.0 | 初始版本 |
| 2026-05-31 | v1.1 | 优化为全自动流程，无需询问用户选择 |

---

## 示例

完整使用示例见 
