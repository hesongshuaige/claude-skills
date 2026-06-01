---
name: pb
description: "Use when the user asks for pb, 排版, 公文排版, 格式化, 生成文档, or 生成Word, and needs arbitrary text formatted into a Word document following GB/T 9704-2012 party/government document standards plus user-specific font, spacing, indentation, table, and margin requirements."
---

# 公文排版技能（pb）

## 核心定位

把任意文本内容排版成**符合党政机关公文格式标准**的Word文档。不是修改内容，只管排版。

## 排版标准（GB/T 9704-2012 + 用户定制）

### 一、纸张与页面

| 项目 | 规格 |
|------|------|
| 纸张 | A4（210mm × 297mm） |
| 上边距 | 3.7cm |
| 下边距 | 3.5cm |
| 左边距 | 2.8cm |
| 右边距 | 2.6cm |
| 每页 | 22行 |
| 每行 | 28个汉字 |

### 二、字体字号（核心）

| 元素 | 中文字体 | 西文字体 | 字号 | 加粗 | 对齐 |
|------|---------|---------|------|------|------|
| **公文标题** | 方正公文小标宋 | Times New Roman | 二号（22pt） | 否 | 居中 |
| **附件标题** | 方正公文小标宋 | Times New Roman | 二号（22pt） | 否 | 居中 |
| **一级标题**（一、二、三、） | 黑体 | Times New Roman | 16.5pt | 否 | 两端对齐 |
| **二级标题**（（一）（二）（三）） | 楷体_GB2312 | Times New Roman | 16.5pt | 是 | 两端对齐 |
| **三级标题**（1. 2. 3.） | 仿宋_GB2312 | Times New Roman | 16.5pt | 是 | 两端对齐 |
| **正文** | 仿宋_GB2312 | Times New Roman | 16.5pt | 否 | 两端对齐 |
| **摘要/落款/来源表** | 仿宋_GB2312 | Times New Roman | 16.5pt | 否 | 按需 |
| **表格表头** | 黑体 | Times New Roman | 16.5pt | 否 | 居中 |
| **表格数据行** | 仿宋_GB2312 | Times New Roman | 16.5pt | 否 | 居中 |
| **保密提示** | 仿宋_GB2312 | Times New Roman | 16.5pt | 是 | 居中 |

### 三、行距

- **全文统一**：固定值28磅
- 包括正文、标题、空行、表格内容，全部固定值28磅
- 不是"1.5倍行距"，不是"单倍行距"，是**固定值28磅**

### 四、缩进规则

| 元素 | 缩进 |
|------|------|
| 正文段落 | 首行缩进2字符 |
| 一级标题 | 首行缩进2字符 |
| 二级标题 | 首行缩进2字符 |
| 三级标题 | 首行缩进2字符 |
| **主送**（XX董事长：） | **顶格不缩进** |
| 公文标题 | 居中，不缩进 |
| 附件标题 | 居中，不缩进 |
| 落款 | 右对齐，不缩进 |
| 表格内容 | 居中，不缩进 |

### 五、附件排版规则

```
附件：XXXXX（方正公文小标宋，二号，居中）
                        ← 空一行（固定值28磅的空行）
（一）XXXXX（楷体，16.5pt，加粗，首行缩进2字符）
XXXXX正文内容（仿宋，16.5pt，首行缩进2字符）← 小标题和正文之间不空行
XXXXX正文内容
（二）XXXXX（楷体，16.5pt，加粗）
XXXXX正文内容← 小标题和正文之间不空行
```

**关键**：只有附件大标题和第一个小标题之间空一行。小标题和紧跟的正文之间**不空行**。

### 六、标点与数字

- **标点**：全部全角（，。：；""）
- **数字**：日期用阿拉伯数字（2026年5月23日）
- **文号括号**：用六角括号〔〕，不是方括号[]

### 七、字体回退方案

方正公文小标宋在Linux服务器上通常不可用。python-docx中写入字体名称即可，在Windows电脑上打开时会自动渲染。如果用户电脑也没有该字体：
- 回退方案1：方正小标宋简体
- 回退方案2：SimSun（宋体）

---

## python-docx 代码模板（必须严格遵循）

以下是生成公文格式Word文档的标准代码模板，所有排版参数已经锁定，不得修改：

```python
#!/usr/bin/env python3
"""公文排版标准模板 - pb skill"""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# ===== 页面设置 =====
for section in doc.sections:
    section.top_margin = Cm(3.7)
    section.bottom_margin = Cm(3.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

def set_font(run, cn_font, size_pt, bold=False):
    """设置字体：中文用指定字体，西文统一Times New Roman"""
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.font.name = 'Times New Roman'
    r = run._element
    rPr = r.find(qn('w:rPr'))
    if rPr is None:
        rPr = r.makeelement(qn('w:rPr'), {})
        r.insert(0, rPr)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = rPr.makeelement(qn('w:rFonts'), {})
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), cn_font)
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')

def set_line_spacing(paragraph, spacing_pt=28):
    """设置固定行距（全文统一28磅）"""
    pPr = paragraph._element.get_or_add_pPr()
    spacing = pPr.find(qn('w:spacing'))
    if spacing is None:
        spacing = pPr.makeelement(qn('w:spacing'), {})
        pPr.append(spacing)
    spacing.set(qn('w:line'), str(spacing_pt * 20))
    spacing.set(qn('w:lineRule'), 'exact')

def set_first_indent(paragraph, chars=2, font_size_pt=16.5):
    """设置首行缩进2字符"""
    paragraph.paragraph_format.first_line_indent = Pt(font_size_pt * chars)

def add_title(text):
    """公文标题/附件标题：方正公文小标宋，二号(22pt)，居中"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_font(run, '方正公文小标宋', 22)
    set_line_spacing(p, 28)
    return p

def add_heading1(text):
    """一级标题（一、二、三、）：黑体，16.5pt，首行缩进"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '黑体', 16.5)
    set_line_spacing(p, 28)
    set_first_indent(p, 2, 16.5)
    return p

def add_heading2(text):
    """二级标题（（一）（二）（三））：楷体，16.5pt，加粗，首行缩进"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '楷体_GB2312', 16.5, bold=True)
    set_line_spacing(p, 28)
    set_first_indent(p, 2, 16.5)
    return p

def add_heading3(text):
    """三级标题（1. 2. 3.）：仿宋，16.5pt，加粗，首行缩进"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '仿宋_GB2312', 16.5, bold=True)
    set_line_spacing(p, 28)
    set_first_indent(p, 2, 16.5)
    return p

def add_body(text, bold=False):
    """正文：仿宋，16.5pt，首行缩进2字符，两端对齐"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '仿宋_GB2312', 16.5, bold=bold)
    set_line_spacing(p, 28)
    set_first_indent(p, 2, 16.5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def add_recipient(text):
    """主送（如"XX董事长："）：仿宋，16.5pt，顶格不缩进"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, '仿宋_GB2312', 16.5)
    set_line_spacing(p, 28)
    # 不设首行缩进，顶格
    return p

def add_blank_line():
    """空行（固定值28磅）"""
    p = doc.add_paragraph()
    set_line_spacing(p, 28)

def add_table(headers, rows_data):
    """表格：表头黑体居中，数据行仿宋居中"""
    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 表头（黑体）
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_font(run, '黑体', 16.5)
    # 数据行（仿宋）
    for row_idx, row_data in enumerate(rows_data):
        for col_idx, val in enumerate(row_data):
            cell = table.rows[row_idx + 1].cells[col_idx]
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            set_font(run, '仿宋_GB2312', 16.5)
    return table

def add_signature(name, date_text):
    """落款：右对齐"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(name)
    set_font(run, '仿宋_GB2312', 16.5)
    set_line_spacing(p, 28)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run2 = p2.add_run(date_text)
    set_font(run2, '仿宋_GB2312', 16.5)
    set_line_spacing(p2, 28)

def add_confidential():
    """保密提示：居中加粗"""
    p = doc.add_paragraph()
    run = p.add_run('\u3010\u5185\u90e8\u8d44\u6599\u3000\u6ce8\u610f\u4fdd\u5bc6\u3011')
    set_font(run, '仿宋_GB2312', 16.5, bold=True)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_line_spacing(p, 28)

# ===== 生成完成后，确保全文Times New Roman =====
def brush_western_font(doc):
    """最后一步：遍历全文确保西文字体为Times New Roman"""
    for para in doc.paragraphs:
        for run in para.runs:
            r = run._element
            rPr = r.find(qn('w:rPr'))
            if rPr is not None:
                rFonts = rPr.find(qn('w:rFonts'))
                if rFonts is not None:
                    rFonts.set(qn('w:ascii'), 'Times New Roman')
                    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        r = run._element
                        rPr = r.find(qn('w:rPr'))
                        if rPr is not None:
                            rFonts = rPr.find(qn('w:rFonts'))
                            if rFonts is not None:
                                rFonts.set(qn('w:ascii'), 'Times New Roman')
                                rFonts.set(qn('w:hAnsi'), 'Times New Roman')
```

---

## 使用方式

### 触发方式
`/pb` 后提供需要排版的内容（文本、Markdown、或指示排版某个已有文件）

### 典型用法
1. `/pb 把以下内容排版成公文格式：[内容]`
2. `/pb 对 /tmp/xxx.docx 重新排版，按公文标准`
3. 配合其他skill使用：先 `/cybg` 生成报告内容，再 `/pb` 排版输出

### 执行流程
1. 读取用户提供的内容（文本/文件）
2. 识别文档结构：标题、一级标题、二级标题、正文、表格、落款
3. 使用上述代码模板生成Word文档
4. 生成完成后执行 `brush_western_font(doc)` 刷一遍全文西文字体
5. 保存到 /tmp/ 目录
6. 上传到飞书云空间
7. 向用户输出下载链接

### 排版识别规则

| 文本特征 | 识别为 | 对应排版 |
|---------|--------|---------|
| 文档第一个居中标题 | 公文标题 | 方正公文小标宋 22pt 居中 |
| "附件：XXX" 开头的新页标题 | 附件标题 | 方正公文小标宋 22pt 居中 |
| "一、""二、""三、" 开头 | 一级标题 | 黑体 16.5pt 首行缩进 |
| "（一）""（二）""（三）" 开头 | 二级标题 | 楷体 16.5pt 加粗 首行缩进 |
| "1.""2.""3." 开头 | 三级标题 | 仿宋 16.5pt 加粗 首行缩进 |
| "XX董事长：" 或类似主送 | 主送 | 仿宋 16.5pt 顶格不缩进 |
| "【内部资料　注意保密】" | 保密提示 | 仿宋 16.5pt 加粗 居中 |
| 以 | 或 - 开头的多列对齐文本 | 表格 | 解析为表格，表头黑体，数据仿宋，全部居中 |
| 落款（单位名+日期） | 落款 | 仿宋 16.5pt 右对齐 |
| 其他正文段落 | 正文 | 仿宋 16.5pt 首行缩进2字符 |

---

## 铁律（违反任何一条 = 排版不合格）

1. **行距必须是固定值28磅**，不是1.5倍、不是单倍、不是多倍
2. **西文字体必须是Times New Roman**，不是Calibri、不是Arial
3. **公文标题和附件标题必须用方正公文小标宋**，字号22pt（二号）
4. **其余所有内容字号必须16.5pt**，不是14pt、不是16pt、不是三号
5. **主送顶格不缩进**，正文首行缩进2字符
6. **表格内容全部居中**，表头用黑体，数据行用仿宋
7. **附件小标题和正文之间不空行**，只有附件大标题后空一行
8. **最后必须执行brush_western_font**，确保全文西文字体统一
