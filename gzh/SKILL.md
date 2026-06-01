---
name: gzh
description: "Use when the user wants to one-click run, audit, trigger, continue, approve, or register publication review for the Zhuge Capital WeChat operations command center, including daily topic collection, article production, review routing, confirmation progress, and post-publication asset tracking."
---

# gzh 公众号运营中台总控

## Purpose

Use gzh as the single Agent entrypoint for `/root/zhuge-corp/wechat_ops/wechat_pipeline.py`.

The goal is to let the user say simple phrases such as “运行诸葛公众号中台”“跑每日选题流程”“把强推选题生成文章”，while the Agent chooses the correct command, preserves compliance gates, and reports the result clearly.

## Scope

Use this skill for:

- Checking the current Feishu knowledge base and Base status.
- Running daily topic collection and evaluation.
- Turning a recommended topic into an article production record.
- Continuing one specific article through strategy, precheck, draft, compliance, routing, and confirmation packet.
- Applying a user-stated investment/fact confirmation and continuing review.
- Registering an already manually published article into the review and content asset table.

Do not use this skill for:

- Publishing directly to WeChat Official Account.
- Bypassing fact verification, investment department confirmation, compliance review, minister review, or He Song final review.
- Inventing company facts, project details, investment decisions, performance, returns, or cooperation commitments.
- Rebuilding the pipeline from scratch unless the local scripts are missing or broken.

## Page-Only Quick Start

If an Agent can only read the Feishu skill page and cannot download the attachment yet:

1. For “运行中台 / 看状态 / 审计”, run audit only:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --audit
   ```

2. For “跑每日选题流程”, write daily topic collection and evaluation:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode daily --write --limit 8 --top 3
   ```

3. For “把强推选题生成文章”, run article production:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode article --write
   ```

4. For “继续处理这篇”, require `record_id`:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode review --write --record-id <record_id>
   ```

5. For “投资部已确认 / 事实已核验”, require `record_id`:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode approve --write --record-id <record_id> --force-draft
   ```

6. For “文章已发布 / 登记复盘”, require `record_id` and real WeChat URL:

   ```bash
   python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode publish --write --record-id <record_id> --publish-url <url>
   ```

If `/root/zhuge-corp/wechat_ops` is missing, download and install the attachment, then use `assets/wechat_ops/wechat_pipeline.py`.

## Resources

| Resource | Role |
|---|---|
| `/root/zhuge-corp/wechat_ops/wechat_pipeline.py` | Main controller on He Song's current machine. Use this first when it exists. |
| `assets/wechat_ops/wechat_pipeline.py` | Bundled reproducible controller snapshot for other agents/environments after installing this skill. |
| `assets/policies/` | Bundled policy and regional resource indexes used by the material package generator. |
| `/root/zhuge-corp/wechat_ops/README.md` | Command reference if behavior is unclear. |
| `/root/zhuge-corp/wechat_ops/publish_asset_registrar.py` | Post-publication asset registration, usually called through the controller. |
| Feishu Base `02 公众号选题库` | Topic candidates and evaluation results. |
| Feishu Base `03 单篇文章生产表` | Per-article production, confirmation, review, and draft tracking. |
| Feishu Base `05 发布复盘与内容资产` | Published article review, reusable assets, and lead follow-up. |

## Prerequisites

- Python 3 is available.
- `lark-cli` is installed and authenticated as `user`.
- The Agent can execute shell commands on the machine where `/root/zhuge-corp/wechat_ops` exists.
- If `/root/zhuge-corp/wechat_ops` does not exist, the Agent has installed this full skill package and can use the bundled controller under `assets/wechat_ops`.
- Python packages used by the bundled scripts are available: `requests`, `PyYAML`, `beautifulsoup4`.
- If `lark-cli` reports missing permissions, stop and follow the auth/scope hint instead of rewriting the workflow.

## Runtime Path Resolution

Prefer this path on He Song's active machine:

```bash
/root/zhuge-corp/wechat_ops/wechat_pipeline.py
```

If that path is missing, locate the installed skill directory and use the bundled snapshot:

```bash
<skill_dir>/assets/wechat_ops/wechat_pipeline.py
```

For example:

```bash
python3 <skill_dir>/assets/wechat_ops/wechat_pipeline.py --audit
```

The bundled snapshot contains the same controller scripts, `sources.yml`, local policy indexes, and an empty `state/seen_urls.json`. It still requires live Feishu access through `lark-cli --as user`.

## Safety Gates

Before any write command, confirm the user intent is explicit enough.

Explicit write intent includes phrases such as:

- “跑每日流程”
- “写入”
- “执行”
- “生成文章”
- “继续处理这篇”
- “投资部已确认”
- “事实已核验”
- “登记复盘”

If the user only says “运行中台”“看一下”“现在怎么样”， run audit only.

Never auto-cross these gates:

- `投资部确认=待确认`
- `事实核验状态=未核验/部分核验/有疑点`
- `合规结论=未审查/不建议发`
- `送审判断=暂不送审/退回重写`
- Missing real WeChat article URL for publication registration

If a write command reports a compliance or confirmation block, stop and explain the next human action.

## Routing

Choose exactly one action per user request.

In commands below, `PIPELINE` means the resolved controller path:

```bash
PIPELINE="/root/zhuge-corp/wechat_ops/wechat_pipeline.py"
test -f "$PIPELINE" || PIPELINE="<skill_dir>/assets/wechat_ops/wechat_pipeline.py"
```

| User intent | Action | Command |
|---|---|---|
| “看状态”“审计”“现在怎么样”“运行中台” | `audit` | `python3 "$PIPELINE" --audit` |
| “跑每日流程”“采集今天选题”“更新选题库” | `daily` | `python3 "$PIPELINE" --mode daily --write --limit 8 --top 3` |
| “生成一篇文章”“强推选题转文章”“跑文章流程” | `article` | `python3 "$PIPELINE" --mode article --write` |
| “继续处理这篇”“推进 record-id xxx” | `review` | `python3 "$PIPELINE" --mode review --write --record-id <record_id>` |
| “投资部已确认”“事实已核验”“可以写了” | `approve` | `python3 "$PIPELINE" --mode approve --write --record-id <record_id> --force-draft` |
| “文章已发布”“发布链接是 xxx”“登记复盘” | `publish` | `python3 "$PIPELINE" --mode publish --write --record-id <record_id> --publish-url <url>` |

## Workflow

1. Classify the request using the routing table.
2. If the action needs `record_id` or `publish-url` and the user did not provide it, run audit first and ask for the missing value.
3. Execute the selected controller command.
4. If a command is still running, wait for it to finish before replying.
5. Run audit after successful write actions when it helps confirm state changes.
6. Report the result in Chinese, focused on current status, generated article, blocking point, and next action.

## Missing Information

For `review` or `approve` without `record_id`:

- Run audit.
- Show the candidate article titles and record IDs from `blocked_or_waiting` or active article rows.
- Ask the user which record to process.

For `publish` without a URL:

- Do not write.
- Ask for the real WeChat article link.
- Optionally run dry-run only if useful.

For ambiguous “一键运行”:

- Default to audit.
- Then recommend the next single action:
  - If there is a `今日强推` topic and no new article needed, recommend `article`.
  - If articles are blocked, identify the human confirmation needed.
  - If an article is already published but asset table is empty, ask for the publication URL.

## Verification

Use the lightest verification that proves the action worked:

- After `audit`: ensure JSON includes `"ok": true`.
- After `daily`: check topic counts and recommendation statuses.
- After `article`: capture the new or processed article title and `article_record_id`.
- After `review` or `approve`: check `送审判断`, `审稿状态`, `合规结论`, and any blocking fields.
- After `publish`: check `05 发布复盘与内容资产` has the asset entry and the source article is marked `已发布`.

## Pressure Scenarios

- Normal: user says “跑每日选题流程”. Run `daily`, then report topic counts and whether a strong recommendation exists.
- Ambiguous: user says “运行中台”. Run audit only, then recommend one next action.
- Missing input: user says “继续处理这篇” without `record_id`. Run audit and ask which article to process.
- Safety boundary: user says “直接发布公众号”. Refuse direct publishing and explain that this skill only prepares, reviews, routes, and registers after manual publication.
- Compliance block: a script returns `暂不送审` or `待确认`. Do not force progress; identify the required human confirmation.

## Report Format

Keep the final response concise:

```text
已运行：<action>
是否写入飞书：是/否
结果：<文章/选题/复盘状态>
当前卡点：<没有/具体卡点>
下一步：<一个最重要动作>
```

If `lark-cli` returns an update notice, mention it after the workflow result, but do not let it interrupt the requested task.
