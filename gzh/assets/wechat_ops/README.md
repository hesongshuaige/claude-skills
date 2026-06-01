# 诸葛资本公众号每日选题采集

用途：从公开信源抓取公众号候选选题，按诸葛资本三条主线自动判断，写入飞书“02 公众号选题库”。

当前版本是 MVP（最小可用版本）：优先抓官方公开信源，不做全自动发布，不替代人工合规判断。

## 文件说明

- `sources.yml`：信源、重点政策种子、飞书选题库表格信息。
- `topic_collector.py`：采集、筛选、分类、写入飞书的脚本。
- `state/seen_urls.json`：本地去重记录，脚本运行后自动生成。

## 运行方式

## 推荐总控命令

先看当前中台状态，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --audit`

预览完整流水线，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode full`

只跑每日选题采集和评估，并写入飞书：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode daily --write --limit 8 --top 3`

从选题生成一篇文章生产记录，并继续跑策略卡、预审、初稿、合规、送审判断和确认推进包：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode article --write`

继续处理指定“03 单篇文章生产表”的记录，避免视图排序导致串稿：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode review --write --record-id <record_id>`

模拟或执行“投资部确认可写 + 事实已核验”，并自动推进到部长审：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode approve --write --record-id <record_id> --force-draft`

文章正式发布后，登记到“05 发布复盘与内容资产”，并把生产表状态标记为已发布：

`python3 /root/zhuge-corp/wechat_ops/wechat_pipeline.py --mode publish --write --record-id <record_id> --publish-url <公众号文章链接> --read-count 0`

默认不做全自动发布。事实核验、投资部确认、合规修改、部长审和何松终审仍是人工闸口。

预览，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/topic_collector.py --limit 8`

写入飞书：

`python3 /root/zhuge-corp/wechat_ops/topic_collector.py --write --limit 8`

忽略本地去重，重新预览：

`python3 /root/zhuge-corp/wechat_ops/topic_collector.py --ignore-state --limit 8`

## 使用边界

- 脚本只抓公开来源。
- “推荐指数、合规风险、是否需要投资部确认”是初筛，不是最终结论。
- “与诸葛资本相关度、目标价值判断、投资部确认原因、自动推荐动作”用于减少人工筛选成本，但仍需要何松或授权人员终审。
- 正式写稿前必须核验原文，涉及私募基金、项目披露、政治表述、政策口径时必须人工复核。

## 回填已有记录

新增判断字段后，可给旧记录补充判断：

`python3 /root/zhuge-corp/wechat_ops/topic_collector.py --backfill`

如果要覆盖旧判断：

`python3 /root/zhuge-corp/wechat_ops/topic_collector.py --backfill --force-backfill`

## 选题评估

预览今日推荐，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/topic_evaluator.py --top 3`

写入飞书评估结论：

`python3 /root/zhuge-corp/wechat_ops/topic_evaluator.py --write --top 3`

## 资料包生成

预览今日强推选题的资料包，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/topic_package_generator.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/topic_package_generator.py --write`

## 文章策略卡

预览策略卡，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/article_strategy_card_generator.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/article_strategy_card_generator.py --write`

## AI（人工智能）策略预审

预览 AI（人工智能）预审，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/strategy_precheck.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/strategy_precheck.py --write`

## 公众号初稿生成

预览初稿生成，不创建飞书文档：

`python3 /root/zhuge-corp/wechat_ops/article_draft_generator.py`

创建飞书文档并回填初稿链接：

`python3 /root/zhuge-corp/wechat_ops/article_draft_generator.py --write`

## 合规审查

预览合规审查，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/compliance_reviewer.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/compliance_reviewer.py --write`

## 送审推进

预览送审判断，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/review_router.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/review_router.py --write`

## 确认推进包

预览确认推进包，不写入飞书：

`python3 /root/zhuge-corp/wechat_ops/confirmation_packet_generator.py`

写入“03 单篇文章生产表”：

`python3 /root/zhuge-corp/wechat_ops/confirmation_packet_generator.py --write`

## 发布复盘登记

文章已经由人工发布后，预览复盘资产记录：

`python3 /root/zhuge-corp/wechat_ops/publish_asset_registrar.py --record-id <record_id> --url <公众号文章链接>`

写入“05 发布复盘与内容资产”，并把来源文章标记为“已发布”：

`python3 /root/zhuge-corp/wechat_ops/publish_asset_registrar.py --write --record-id <record_id> --url <公众号文章链接>`
