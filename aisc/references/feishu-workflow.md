# Feishu/Lark Workflow

Use this file only when the user requested saving or uploading.

## Preconditions

- Confirm content has passed the quality gate.
- Confirm an upload-capable Feishu/Lark tool or `lark-cli` is available.
- If authentication is missing, produce the card locally and ask the user to authenticate before retrying upload.

## Defaults

- Knowledge base: `学习卡片沉淀库`
- Index page: `学习卡片沉淀库索引`
- Card title format: `【卡片】{source_title}`
- If source title is missing, use a concise title inferred from the content and mark source title as `未提供` in the card.

## Create or Locate Knowledge Base

Use available Feishu/Lark wiki capabilities to locate `学习卡片沉淀库`. If it does not exist and the user asked for automatic persistence, create it.

With `lark-cli`, typical operations are:

```bash
lark-cli wiki +space-list --as user --format json
lark-cli wiki +space-create --name "学习卡片沉淀库" --description "日常学习内容的卡片式沉淀，方便复盘和迁移。" --as user
```

## Create or Locate Index

The index should contain:

```markdown
# 学习卡片沉淀库索引

| 日期 | 标题 | 来源类型 | 内容分类 | 入库建议 | 核心一句话 | 链接 |
|------|------|----------|----------|----------|------------|------|
```

If the index does not exist, create it in the knowledge base.

## Upload Card

Create a new document from the final Markdown card in the knowledge base.

With `lark-cli`, the shape is:

```bash
lark-cli docs +create --title "【卡片】{source_title}" --markdown "{card_markdown}" --wiki-space "{space_id}" --as user
```

Adapt command names to the available Lark/Feishu tools. Do not claim upload success until a URL or document identifier is returned.

## Update Index

Append one row:

```markdown
| YYYY-MM-DD | 【卡片】标题 | 来源类型 | 内容分类 | 入库建议 | 核心一句话 | 卡片链接 |
```

If index update fails after card upload, return the card link and this row for manual insertion.

## Failure Response

Return:

```markdown
上传状态：成功 / 部分成功 / 失败
知识库：链接或未创建
索引：链接、未更新原因或手动追加行
卡片：链接或本地卡片正文
下一步：具体操作
```
