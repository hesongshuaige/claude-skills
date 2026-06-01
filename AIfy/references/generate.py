#!/usr/bin/env python3
"""
AI落地路径图 HTML 生成脚本
用法：python generate.py --config config.json --output 输出文件.html
或者：python generate.py --biz-name "XX公司" --team-size "15人" ...

config.json 格式：
{
  "biz_name": "企业名/业务名",
  "team_size": "12人",
  "stage": "已有AI工具但不成体系",
  "gen_date": "2026-05-24",
  "biz_type": "教培",
  "flow_nodes": [
    {"name": "获客引流", "priority": 1},
    {"name": "咨询转化", "priority": 1},
    ...共5-8个
  ],
  "matrix_nodes": {
    "sweet": [{"name": "节点名", "biz": "业务描述"}],
    "value": [...],
    "chicken": [...],
    "wait": [...]
  },
  "priorities": [
    {
      "rank": 1,
      "name": "家长咨询自动回复",
      "tags": {"high": true, "struct": true, "time": true},
      "layers": [
        {"label": "业务动作", "value": "..."},
        {"label": "业务流程", "value": "..."},
        {"label": "AI可执行步骤", "value": "..."},
        {"label": "兜底闭环", "value": "..."}
      ]
    }
  ],
  "sop": {
    "node_name": "家长咨询自动回复",
    "items": {
      "demand": "...",
      "trigger": "...",
      "input": "...",
      "process": "...",
      "output": "...",
      "delivery": "...",
      "fallback": "...",
      "human": "...",
      "success": "..."
    },
    "tools": [
      {"name": "轻量版", "tool": "...", "for": "...", "cost": "...", "cycle": "..."},
      {"name": "标准版", "tool": "...", "for": "...", "cost": "...", "cycle": "..."},
      {"name": "完整版", "tool": "...", "for": "...", "cost": "...", "cycle": "..."}
    ],
    "roadmap": [
      {"phase": "AI生成，人审核", "action": "...", "days": "...", "flag": "..."},
      {"phase": "AI执行，异常介入", "action": "...", "days": "...", "flag": "..."},
      {"phase": "AI全自动运行", "action": "...", "days": "...", "flag": "..."}
    ],
    "cost_tool": "...",
    "cost_manual": "...",
    "cost_roi": "...",
    "pits": ["坑1", "坑2", "坑3"]
  },
  "checklist": [
    "整理知识库（FAQ、话术库、案例库）",
    ...
  ],
  "wechat_qr_base64": "data:image/jpeg;base64,..."
}
"""

import json, argparse, sys, os

# ========== HTML 模板（CSS部分固定） ==========
CSS = """  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #f5f5f7;
    color: #1d1d1f;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
  .container {
    max-width: 860px;
    margin: 0 auto;
    padding: 20px 16px 60px;
  }
  .header {
    background: linear-gradient(135deg, #1d1d1f 0%, #2c2c2e 100%);
    border-radius: 20px;
    padding: 32px 28px;
    color: #fff;
    margin-bottom: 20px;
  }
  .header .label {
    font-size: 12px;
    font-weight: 500;
    color: #a1a1a6;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 12px;
  }
  .header h1 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
  }
  .header .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 16px;
  }
  .header .meta-item {
    background: rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
    color: #e5e5ea;
  }
  .header .meta-item strong { color: #fff; font-weight: 600; }
  .card {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    border: 0.5px solid rgba(0,0,0,0.06);
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .card-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-title .icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: #fff;
    flex-shrink: 0;
  }
  .section-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px; height: 24px;
    border-radius: 50%;
    background: #e8e8ed;
    color: #6e6e73;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
    flex-shrink: 0;
  }
  /* Flow Chart */
  .flow-wrapper { overflow-x: auto; padding: 8px 0; }
  .flow-chart {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    min-width: 600px;
  }
  .flow-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
  }
  .flow-node {
    background: #f5f5f7;
    border: 1.5px solid #d2d2d7;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    color: #1d1d1f;
    white-space: nowrap;
    position: relative;
    transition: all 0.2s;
  }
  .flow-node.priority-1 { background: #f0ebff; border-color: #512cf1; color: #512cf1; }
  .flow-node.priority-2 { background: #e6f5ef; border-color: #0f6e56; color: #0f6e56; }
  .flow-node.priority-3 { background: #fef3e6; border-color: #993c1d; color: #993c1d; }
  .flow-arrow { color: #aeaeb2; font-size: 16px; flex-shrink: 0; }
  .flow-arrow-down { color: #aeaeb2; font-size: 16px; margin: 6px 0; }
  .flow-badge {
    display: inline-block;
    font-size: 10px;
    padding: 1px 6px;
    border-radius: 4px;
    margin-left: 6px;
    font-weight: 600;
    vertical-align: middle;
  }
  .badge-p1 { background: #512cf1; color: #fff; }
  .badge-p2 { background: #0f6e56; color: #fff; }
  .badge-p3 { background: #993c1d; color: #fff; }
  .flow-loop {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    font-size: 12px;
    color: #8e8e93;
  }
  .flow-loop-line {
    width: 40px; height: 2px;
    background: repeating-linear-gradient(90deg, #aeaeb2 0, #aeaeb2 4px, transparent 4px, transparent 8px);
  }
  /* Matrix */
  .matrix {
    display: grid;
    grid-template-columns: 100px 1fr 1fr;
    grid-template-rows: 36px 1fr 1fr;
    gap: 2px;
    margin: 16px 0;
  }
  .matrix-cell {
    border-radius: 10px;
    padding: 14px;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .matrix-header {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: #8e8e93;
  }
  .matrix-corner { background: transparent; }
  .matrix-sweet { background: #f0ebff; border: 1.5px solid #512cf1; }
  .matrix-value { background: #e6f5ef; border: 1.5px solid #0f6e56; }
  .matrix-chicken { background: #fef3e6; border: 1.5px solid #993c1d; }
  .matrix-wait { background: #f5f5f7; border: 1.5px solid #d2d2d7; }
  .matrix-label {
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 4px;
    letter-spacing: 0.5px;
  }
  .matrix-desc {
    font-size: 11px;
    color: #6e6e73;
    line-height: 1.4;
  }
  .matrix-node {
    display: inline-block;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px;
    background: rgba(0,0,0,0.06);
    font-weight: 500;
  }
  .matrix-axis {
    font-size: 11px;
    color: #aeaeb2;
    text-align: center;
    margin-top: 4px;
  }
  .matrix-row-label {
    writing-mode: horizontal-tb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: #8e8e93;
    text-align: center;
    line-height: 1.4;
    padding: 4px;
  }
  /* Priority Cards */
  .priority-list { display: flex; flex-direction: column; gap: 12px; }
  .priority-card { border-radius: 12px; padding: 18px; border: 1.5px solid; }
  .priority-card.p1 { background: #faf8ff; border-color: #512cf1; }
  .priority-card.p2 { background: #f5fcf9; border-color: #0f6e56; }
  .priority-card.p3 { background: #fffaf5; border-color: #993c1d; }
  .priority-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
  .priority-num {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
  }
  .p1 .priority-num { background: #512cf1; }
  .p2 .priority-num { background: #0f6e56; }
  .p3 .priority-num { background: #993c1d; }
  .priority-name { font-size: 16px; font-weight: 700; }
  .priority-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }
  .tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
  .tag-high { background: #ffe5e5; color: #d32f2f; }
  .tag-struct { background: #e3f2fd; color: #1565c0; }
  .tag-time { background: #fff3e0; color: #e65100; }
  .layer-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 8px;
  }
  .layer-table th {
    text-align: left;
    font-weight: 600;
    color: #8e8e93;
    padding: 6px 8px;
    border-bottom: 1px solid #e8e8ed;
    font-size: 11px;
  }
  .layer-table td {
    padding: 8px;
    vertical-align: top;
    border-bottom: 1px solid #f0f0f2;
    line-height: 1.5;
  }
  .layer-label {
    font-weight: 600;
    color: #1d1d1f;
    white-space: nowrap;
    width: 80px;
  }
  /* SOP */
  .sop-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e8e8ed;
  }
  .sop-num {
    background: #f5f5f7;
    padding: 12px 14px;
    font-size: 14px;
    font-weight: 700;
    color: #6e6e73;
    display: flex;
    align-items: flex-start;
    border-bottom: 1px solid #e8e8ed;
  }
  .sop-num.highlight { color: #d32f2f; background: #fff5f5; }
  .sop-content {
    padding: 12px 14px;
    font-size: 13px;
    border-bottom: 1px solid #e8e8ed;
    display: flex;
    flex-direction: column;
  }
  .sop-label { font-weight: 600; color: #1d1d1f; margin-bottom: 2px; }
  .sop-value { color: #3a3a3c; line-height: 1.5; }
  .sop-grid .sop-num:last-child,
  .sop-grid .sop-content:last-child { border-bottom: none; }
  /* Timeline */
  .timeline { display: flex; gap: 12px; position: relative; }
  .timeline::before {
    content: '';
    position: absolute;
    top: 20px; left: 40px; right: 40px;
    height: 3px;
    background: #e8e8ed;
    border-radius: 2px;
    z-index: 0;
  }
  .timeline-item { flex: 1; position: relative; z-index: 1; }
  .timeline-dot {
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 700;
    color: #fff;
    margin: 0 auto 12px;
    position: relative;
  }
  .timeline-item:nth-child(1) .timeline-dot { background: #512cf1; }
  .timeline-item:nth-child(2) .timeline-dot { background: #0f6e56; }
  .timeline-item:nth-child(3) .timeline-dot { background: #993c1d; }
  .timeline-phase { text-align: center; font-size: 12px; font-weight: 600; margin-bottom: 4px; }
  .timeline-desc { text-align: center; font-size: 11px; color: #6e6e73; line-height: 1.4; padding: 0 4px; }
  .timeline-time { text-align: center; font-size: 11px; color: #aeaeb2; margin-top: 4px; }
  /* Tool Table */
  .tool-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 12px;
  }
  .tool-table th {
    background: #f5f5f7;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    color: #6e6e73;
    border-bottom: 1px solid #e8e8ed;
  }
  .tool-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #f0f0f2;
    vertical-align: top;
  }
  .tool-table tr:last-child td { border-bottom: none; }
  .tool-recommend {
    display: inline-block;
    font-size: 11px;
    padding: 1px 6px;
    border-radius: 4px;
    background: #512cf1;
    color: #fff;
    font-weight: 600;
    margin-left: 4px;
  }
  /* Cost */
  .cost-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
  .cost-item { background: #f5f5f7; border-radius: 10px; padding: 14px; }
  .cost-label { font-size: 11px; color: #8e8e93; font-weight: 600; margin-bottom: 4px; }
  .cost-value { font-size: 20px; font-weight: 700; color: #1d1d1f; }
  .cost-value span { font-size: 13px; font-weight: 400; color: #6e6e73; }
  /* Pitfalls */
  .pitfall-list { list-style: none; padding: 0; }
  .pitfall-list li {
    padding: 10px 14px;
    background: #fffaf5;
    border-left: 3px solid #993c1d;
    border-radius: 0 8px 8px 0;
    margin-bottom: 8px;
    font-size: 13px;
    color: #3a3a3c;
    line-height: 1.5;
  }
  .pitfall-list li strong { color: #993c1d; }
  /* Checklist */
  .checklist { list-style: none; padding: 0; }
  .checklist li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f2;
    font-size: 13px;
  }
  .checklist li:last-child { border-bottom: none; }
  .checklist-box {
    width: 20px; height: 20px;
    border: 2px solid #d2d2d7;
    border-radius: 6px;
    flex-shrink: 0;
    margin-top: 1px;
  }
  .checklist-text { color: #3a3a3c; line-height: 1.5; }
  .checklist-text strong { color: #1d1d1f; }
  /* Rules */
  .rules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; }
  .rule-item { background: #f5f5f7; border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #3a3a3c; line-height: 1.4; }
  .rule-item strong { display: block; font-size: 11px; color: #6e6e73; margin-bottom: 2px; }
  /* Footer */
  .footer { text-align: center; padding: 24px 0; font-size: 11px; color: #aeaeb2; line-height: 1.8; }
  .footer a { color: #512cf1; text-decoration: none; }
  /* Sub-title */
  .sub-title { font-size: 14px; font-weight: 600; color: #1d1d1f; margin: 16px 0 8px; }
  /* CTA Card */
  .cta-card {
    background: linear-gradient(135deg, #1d1d1f 0%, #3a3a3c 100%);
    border-radius: 20px;
    padding: 32px 28px;
    color: #fff;
    margin-bottom: 16px;
    text-align: center;
  }
  .cta-card .cta-badge {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.6);
    margin-bottom: 12px;
  }
  .cta-card h2 {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
  }
  .cta-card .cta-sub {
    font-size: 14px;
    color: rgba(255,255,255,0.7);
    margin-bottom: 20px;
  }
  .cta-card .cta-price {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 4px;
  }
  .cta-card .cta-price-note {
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    margin-bottom: 20px;
  }
  .cta-benefits {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
  }
  .cta-benefit {
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 12px;
    font-size: 12px;
    text-align: left;
    line-height: 1.5;
  }
  .cta-benefit .cta-benefit-title {
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 2px;
  }
  .cta-card .wechat-link {
    display: inline-block;
    margin-top: 16px;
    color: rgba(255,255,255,0.7);
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.3);
    padding-bottom: 2px;
    cursor: pointer;
  }
  .cta-card .cta-bottom {
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    margin-top: 16px;
    line-height: 1.6;
  }
  .cta-card .cta-bottom strong { color: rgba(255,255,255,0.8); }
  /* QR Overlay */
  .qr-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.6);
    z-index: 9999;
  }
  .qr-overlay.active {
    display: flex !important;
    align-items: center;
    justify-content: center;
  }
  .qr-modal {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    max-width: 320px;
    width: 90%;
  }
  .qr-title { font-size: 16px; font-weight: 700; color: #1d1d1f; margin-bottom: 12px; }
  .qr-modal img { width: 200px; height: 200px; object-fit: contain; margin: 0 auto; display: block; }
  .qr-id { font-size: 13px; color: #6e6e73; margin-top: 8px; }
  .qr-close {
    margin-top: 16px;
    padding: 8px 24px;
    background: #f5f5f7;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: #3a3a3c;
    cursor: pointer;
  }
"""

# ========== HTML 生成函数 ==========

def build_flow_chart(nodes):
    """生成业务路径流程图 HTML"""
    n = len(nodes)
    # 第一行：前几个节点
    first_row_count = min(4, n)
    first_row = ""
    for i, node in enumerate(nodes[:first_row_count]):
        p = f' priority-{node.get("priority", 0)}' if node.get("priority") else ''
        badge = ""
        if node.get("priority") == 1:
            badge = '<span class="flow-badge badge-p1">甜点</span>'
        elif node.get("priority") == 2:
            badge = '<span class="flow-badge badge-p2">价值</span>'
        first_row += f'<div class="flow-node{p}">{node["name"]}</div>'
        if i < first_row_count - 1:
            first_row += '<span class="flow-arrow">→</span>'

    # 第二行：剩余节点（下行箭头 + 节点）
    second_row = ""
    if n > first_row_count:
        second_row += '<div class="flow-arrow-down">↓</div>\n      <div class="flow-row">'
        for i, node in enumerate(nodes[first_row_count:]):
            p = f' priority-{node.get("priority", 0)}' if node.get("priority") else ''
            badge = ""
            if node.get("priority") == 1:
                badge = '<span class="flow-badge badge-p1">甜点</span>'
            elif node.get("priority") == 2:
                badge = '<span class="flow-badge badge-p2">价值</span>'
            second_row += f'<div class="flow-node{p}">{node["name"]}{badge}</div>'
            if i < n - first_row_count - 1:
                second_row += '<span class="flow-arrow">→</span>'
        second_row += '</div>'

    # 循环回路
    loop = ""
    if n > 0:
        loop = f'''      <div class="flow-loop">
        <div class="flow-loop-line"></div>
        <span>循环：{nodes[-1]["name"]} → 新一轮{nodes[0]["name"]}</span>
        <div class="flow-loop-line"></div>
      </div>'''

    return f'''    <div class="flow-wrapper">
      <div class="flow-chart">
        <div class="flow-row">
          {first_row}
        </div>
        {second_row}
        {loop}
      </div>
    </div>'''

def build_matrix(matrix_nodes):
    """生成场景筛选矩阵 HTML"""
    def node_spans(nodes):
        return "".join(f'<span class="matrix-node">{n["name"]}</span>' for n in nodes)

    sweet = node_spans(matrix_nodes.get("sweet", []))
    value = node_spans(matrix_nodes.get("value", []))
    chicken = node_spans(matrix_nodes.get("chicken", []))
    wait = node_spans(matrix_nodes.get("wait", []))

    return f'''    <div class="matrix">
      <div class="matrix-cell matrix-corner"></div>
      <div class="matrix-cell matrix-header">结构化（能说清输入输出）</div>
      <div class="matrix-cell matrix-header">非结构化（靠经验判断）</div>

      <div class="matrix-cell matrix-row-label">高频<br>（每周5次以上）</div>
      <div class="matrix-cell matrix-sweet">
        <div class="matrix-label">甜点区 — 第一优先</div>
        <div class="matrix-desc">高频 + 结构化<br>AI最容易见效</div>
        <div style="margin-top:8px">{sweet}</div>
      </div>
      <div class="matrix-cell matrix-chicken">
        <div class="matrix-label">鸡肋区 — AI做不好</div>
        <div class="matrix-desc">高频 + 非结构化<br>不值得投入</div>
        <div style="margin-top:8px">{chicken}</div>
      </div>

      <div class="matrix-cell matrix-row-label">低频<br>（每周少于5次）</div>
      <div class="matrix-cell matrix-value">
        <div class="matrix-label">价值区 — 第二优先</div>
        <div class="matrix-desc">低频 + 结构化<br>重点做</div>
        <div style="margin-top:8px">{value}</div>
      </div>
      <div class="matrix-cell matrix-wait">
        <div class="matrix-label">观望区 — 不急做</div>
        <div class="matrix-desc">低频 + 非结构化<br>等能力提升</div>
        <div style="margin-top:8px">{wait}</div>
      </div>
    </div>
    <div class="matrix-axis">← 结构化程度 →</div>'''

def build_priority_cards(priorities):
    """生成AI提效机会清单 HTML"""
    cards = ""
    rank_labels = {1: "第一优先", 2: "第二优先", 3: "第三优先（可做，优先级稍低）"}
    rank_classes = {1: "p1", 2: "p2", 3: "p3"}

    for p in priorities:
        rank = p["rank"]
        tags_html = ""
        if p.get("tags"):
            if p["tags"].get("high"):
                tags_html += '<span class="tag tag-high">🔥高频</span>'
            if p["tags"].get("struct"):
                tags_html += '<span class="tag tag-struct">📋可结构化</span>'
            if p["tags"].get("time"):
                tags_html += '<span class="tag tag-time">⏱耗时</span>'

        layers_html = ""
        if p.get("layers"):
            layers_html = '''        <table class="layer-table">
          <tr><th>层级</th><th>内容</th></tr>
'''
            layer_names = ["业务动作", "业务流程", "AI可执行步骤", "兜底闭环"]
            for i, layer in enumerate(p["layers"]):
                ln = layer_names[i] if i < len(layer_names) else f"层{i+1}"
                layers_html += f'          <tr><td class="layer-label">{ln}</td><td>{layer["value"]}</td></tr>\n'
            layers_html += '        </table>'

        cards += f'''      <div class="priority-card {rank_classes.get(rank, "p1")}">
        <div class="priority-header">
          <div class="priority-num">{rank}</div>
          <div class="priority-name">{p["name"]}</div>
          <div class="priority-tags">{tags_html}</div>
        </div>
        <div style="font-size:13px; color:#3a3a3c;">
          <strong>← {rank_labels.get(rank, "")}</strong>
          {layers_html}
        </div>
      </div>
'''
    return f'''    <div class="priority-list">
{cards}
    </div>'''

def build_sop_card(sop):
    """生成SOP九要素卡 HTML"""
    items = sop["items"]
    highlights = ["⑦", "⑧", "⑨"]
    highlight_keys = ["fallback", "human", "success"]
    sop_rows = ""
    sop_labels = ["① 业务需求", "② 触发条件", "③ 输入数据", "④ 处理逻辑", "⑤ 输出结果", "⑥ 交付方式", "⑦ 异常兜底", "⑧ 人工介入点", "⑨ 成功/失败标准"]
    sop_item_keys = ["demand", "trigger", "input", "process", "output", "delivery", "fallback", "human", "success"]

    for i, key in enumerate(sop_item_keys):
        num = sop_labels[i]
        val = items.get(key, "")
        hl = ' highlight' if key in highlight_keys else ''
        sop_rows += f'''      <div class="sop-num{hl}">{num.split()[0]}</div>
      <div class="sop-content">
        <div class="sop-label">{num}</div>
        <div class="sop-value">{val}</div>
      </div>
'''

    # 工具选择表
    tools_html = """      <table class="tool-table">
        <tr><th>方案</th><th>工具</th><th>适合谁</th><th>成本</th><th>周期</th></tr>
"""
    for t in sop.get("tools", []):
        rec = '<span class="tool-recommend">推荐</span>' if t.get("recommend") else ''
        tools_html += f"""        <tr>
          <td><strong>{t["name"]}</strong></td>
          <td>{t["tool"]}{rec}</td>
          <td>{t["for"]}</td>
          <td>{t["cost"]}</td>
          <td>{t["cycle"]}</td>
        </tr>
"""
    tools_html += "      </table>"

    # 渐进落地路线图
    roadmap_html = """    <div class="timeline">"""
    for r in sop.get("roadmap", []):
        roadmap_html += f"""
      <div class="timeline-item">
        <div class="timeline-dot">●</div>
        <div class="timeline-phase">{r["phase"]}</div>
        <div class="timeline-desc">{r["action"]}</div>
        <div class="timeline-time">{r["time"]}</div>
      </div>"""
    roadmap_html += "\n    </div>"

    # 成本预估
    cost_html = f'''    <div class="cost-grid">
      <div class="cost-item">
        <div class="cost-label">工具成本</div>
        <div class="cost-value">{sop.get("cost_tool", "约XXX元/月")}</div>
      </div>
      <div class="cost-item">
        <div class="cost-label">人工成本</div>
        <div class="cost-value">{sop.get("cost_manual", "需投入X天熟悉")}</div>
      </div>
      <div class="cost-item">
        <div class="cost-label">ROI测算</div>
        <div class="cost-value">{sop.get("cost_roi", "X个月收回成本")}</div>
      </div>
      <div class="cost-item">
        <div class="cost-label">每天节省时间</div>
        <div class="cost-value">{sop.get("cost_save", "X小时")}</div>
      </div>
    </div>'''

    # 常见坑
    pits_html = """    <div class="sub-title">常见坑（基于{{BIZ_TYPE}}真实案例）</div>
    <ul class="pitfall-list">"""
    for pit in sop.get("pits", []):
        pits_html += f"\n      <li>{pit}</li>"
    pits_html += "\n    </ul>"

    return f'''    <div class="sop-grid">
{sop_rows}
    </div>

    <div class="sub-title">🛠 工具选择（按难度从低到高）</div>
{tools_html}

    <div class="sub-title">⏱ 渐进落地路线图</div>
{roadmap_html}

    <div class="sub-title">💰 成本预估</div>
{cost_html}

{pits_html}'''

def build_checklist(checklist):
    """生成落地检查清单 HTML"""
    items = ""
    for item in checklist:
        items += f'''      <li>
        <div class="checklist-box"></div>
        <div class="checklist-text">{item}</div>
      </li>
'''
    return f'''    <ul class="checklist">
{items}
    </ul>'''

def build_rules():
    """生成判定规则说明 HTML（固定内容）"""
    return """    <div class="rules-grid">
      <div class="rule-item">
        <strong>场景筛选矩阵</strong>
        高频 + 结构化 = 甜点区（第一优先）；低频 + 结构化 = 价值区（第二优先）；高频 + 非结构化 = 鸡肋区；低频 + 非结构化 = 观望区
      </div>
      <div class="rule-item">
        <strong>四层拆解法</strong>
        第一层：业务动作（老板说的话）→ 第二层：业务流程（人怎么做）→ 第三层：AI可执行步骤（触发/输入/处理/输出/交付）→ 第四层：兜底闭环（出问题时怎么办）
      </div>
      <div class="rule-item">
        <strong>SOP九要素</strong>
        ①业务需求 ②触发条件 ③输入数据 ④处理逻辑 ⑤输出结果 ⑥交付方式 ⑦异常兜底（红） ⑧人工介入点（红） ⑨成功标准（红）—— 后三个最容易漏
      </div>
      <div class="rule-item">
        <strong>渐进三阶段</strong>
        第一阶段：AI生成，人审核再发（人=决策者）→ 第二阶段：AI执行，异常时人介入（人=监督者）→ 第三阶段：AI全自动，人只看结果（人=审计者）
      </div>
    </div>"""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
QR_FILE = os.path.join(SCRIPT_DIR, "wechat_qr_base64.txt")

def load_wechat_qr():
    """读取微信二维码base64数据"""
    if os.path.exists(QR_FILE):
        with open(QR_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def generate_html(cfg):
    """根据配置生成完整HTML"""
    # 自动加载微信二维码（配置中无需填写）
    wechat_qr = cfg.get("wechat_qr_base64", "")
    if not wechat_qr:
        wechat_qr = load_wechat_qr()
        if not wechat_qr:
            wechat_qr = ""  # 留空，不嵌入二维码

    biz = cfg["biz_name"]
    team = cfg["team_size"]
    stage = cfg["stage"]
    gdate = cfg.get("gen_date", "2026-05-24")
    biz_type = cfg.get("biz_type", "")
    wechat_qr = cfg.get("wechat_qr_base64", "")

    # 1. Header
    header = f'''  <div class="header">
    <div class="label">NEXT STAGE · AI落地路径图</div>
    <h1>{biz} · AI落地诊断报告</h1>
    <div class="meta">
      <div class="meta-item"><strong>团队规模：</strong>{team}</div>
      <div class="meta-item"><strong>适用阶段：</strong>{stage}</div>
      <div class="meta-item"><strong>生成时间：</strong>{gdate}</div>
    </div>
  </div>'''

    # 2. 业务路径流程图
    flow = build_flow_chart(cfg.get("flow_nodes", []))

    # 3. 场景筛选矩阵
    matrix = build_matrix(cfg.get("matrix_nodes", {}))

    # 4. AI提效机会清单
    priorities = build_priority_cards(cfg.get("priorities", []))

    # 5. SOP九要素卡
    sop_html = build_sop_card(cfg.get("sop", {}))

    # 6. 工具选择+成本（已包含在 sop_html 中）
    # 7. 渐进落地路线图（已包含在 sop_html 中）
    # 8. 落地检查清单
    checklist_html = build_checklist(cfg.get("checklist", []))

    # 9. 判定规则说明
    rules_html = build_rules()

    # 10. CTA 卡片
    cta = f'''  <div class="cta-card">
    <div class="cta-badge">NEXT STAGE</div>
    <h2>自己摸索不如跟一群人在做</h2>
    <div class="cta-sub">加入NEXT STAGE社群，拿到的不只是方案，还有落地过程中的每一步支持。</div>
    <div class="cta-price">¥2,680</div>
    <div class="cta-price-note">一次性入群，长期有效</div>
    <div class="cta-benefits">
      <div class="cta-benefit">
        <div class="cta-benefit-title">💬 1对1落地指导</div>
        <div>入群即赠送1次1对1指导，帮你把这份路径图变成实际行动方案</div>
      </div>
      <div class="cta-benefit">
        <div class="cta-benefit-title">🔗 定制开发匹配</div>
        <div>社群帮你匹配靠谱的开发资源，价格低于市面20-30%</div>
      </div>
      <div class="cta-benefit">
        <div class="cta-benefit-title">📋 企业级案例分享</div>
        <div>每月分享其他企业真实AI落地案例（含踩坑记录和效果数据）</div>
      </div>
      <div class="cta-benefit">
        <div class="cta-benefit-title">🔍 新工具测评解读</div>
        <div>每周筛选新出的AI工具，直接告诉你适不适合你的行业</div>
      </div>
    </div>
    <a href="javascript:void(0)" class="wechat-link" onclick="document.getElementById('qr-overlay').classList.add('active')">微信：小挣青年（备注「AI落地」）</a>
    <div class="cta-bottom">
      <strong>算一笔账：</strong>自己摸索AI落地，平均踩3-5个坑，每个坑1-2周 + 选工具试工具的时间。<br>
      <strong>2680元 =</strong> 跳过别人的弯路 + 找到对的人帮你做 + 持续知道该做什么、不该做什么。
    </div>
  </div>'''

    # 微信二维码弹窗
    qr_overlay = f'''  <div class="qr-overlay" id="qr-overlay" onclick="if(event.target===this)this.classList.remove('active')">
    <div class="qr-modal">
      <div class="qr-title">扫码添加微信</div>
      <img id="qr-img" src="{wechat_qr}" alt="微信二维码">
      <div class="qr-id">微信号：小挣青年</div>
      <button class="qr-close" onclick="document.getElementById('qr-overlay').classList.remove('active')">关闭</button>
    </div>
  </div>'''

    # Footer
    footer = f'''  <div class="footer">
    <div>由「AI落地翻译官」生成 · NEXT STAGE</div>
    <div style="font-style:italic; color:#aeaeb2; margin-top:2px;">少踩坑，快落地。</div>
    <div style="margin-top:4px;">本路径图基于对话分析生成，具体执行请根据实际情况调整</div>
  </div>'''

    # 组装完整HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI落地路径图 - {biz}</title>
<style>
{CSS}
</style>
</head>
<body>
  <div class="container">
    <!-- ====== 1. Header ====== -->
{header}
    <!-- ====== 2. 业务路径流程图 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">2</span>
        <span class="icon" style="background:#512cf1;">🗺</span>
        业务路径流程图
      </div>
{flow}
    </div>

    <!-- ====== 3. 场景筛选矩阵 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">3</span>
        <span class="icon" style="background:#0f6e56;">▦</span>
        场景筛选矩阵
      </div>
{matrix}
    </div>

    <!-- ====== 4. AI提效机会清单 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">4</span>
        <span class="icon" style="background:#993c1d;">⚡</span>
        AI提效机会清单
      </div>
{priorities}
    </div>

    <!-- ====== 5. SOP九要素卡 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">5</span>
        <span class="icon" style="background:#512cf1;">📋</span>
        SOP九要素卡（第一优先节点）
      </div>
{sop_html}
    </div>

    <!-- ====== 8. 落地检查清单 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">8</span>
        <span class="icon" style="background:#0f6e56;">✔</span>
        落地检查清单
      </div>
{checklist_html}
    </div>

    <!-- ====== 9. 判定规则说明 ====== -->
    <div class="card">
      <div class="card-title">
        <span class="section-num">9</span>
        <span class="icon" style="background:#6e6e73;">⚙</span>
        判定规则说明
      </div>
{rules_html}
    </div>

    <!-- ====== 10. 下一步行动 ====== -->
{cta}

{qr_overlay}

    <!-- ====== Footer ====== -->
{footer}
  </div>
</body>
</html>"""

    # 替换业务类型占位符
    html = html.replace("{{BIZ_TYPE}}", biz_type)

    return html


def main():
    parser = argparse.ArgumentParser(description="生成AI落地路径图HTML")
    parser.add_argument("--config", help="JSON配置文件路径")
    parser.add_argument("--output", required=True, help="输出HTML文件路径")
    # 也支持直接传参（简化模式）
    parser.add_argument("--biz-name", help="企业名/业务名")
    parser.add_argument("--team-size", default="", help="团队规模")
    parser.add_argument("--stage", default="", help="适用阶段")
    parser.add_argument("--gen-date", default="", help="生成日期")
    args = parser.parse_args()

    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    elif args.biz_name:
        # 简化模式：只填基本信息，其余用默认值
        print("⚠️ 简化模式：请通过 --config 传入完整JSON配置以获得完整HTML")
        cfg = {
            "biz_name": args.biz_name,
            "team_size": args.team_size,
            "stage": args.stage,
            "gen_date": args.gen_date or "2026-05-24",
            "biz_type": "",
            "flow_nodes": [],
            "matrix_nodes": {},
            "priorities": [],
            "sop": {},
            "checklist": [],
            "wechat_qr_base64": ""
        }
    else:
        print("错误：请指定 --config 或 --biz-name")
        sys.exit(1)

    html = generate_html(cfg)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    fsize = len(html.encode("utf-8")) // 1024
    print(f"✅ 已生成：{args.output}（{fsize} KB）")

if __name__ == "__main__":
    main()
