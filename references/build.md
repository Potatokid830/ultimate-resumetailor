# 模版与制作流水线：细节

SKILL.md 第 3 节的展开。文中"第 X 节"都指 SKILL.md 里的章节。固定规则（一页写满、板块名、时间、全角标点、文件名、照片等）在主文件里，这里只讲怎么做。

## 文件

- `assets/template_cn.docx`、`assets/template_en.docx`：空白模版，提供页面、字体、样式、项目符号（内容全是占位符，直接用 Word 打开也能手填）。
- `scripts/helpers_cn.py`、`scripts/helpers_en.py`：简历积木 `header()`、`section()`、`entry()`、`sub()`、`bullet()`、`finish()`。
- `scripts/build.py`：一条命令出 docx、pdf、预览图，并跑机筛自检（Windows / macOS / Linux 通用；`build.sh` 只是为旧用法保留的转发脚本）。
- `scripts/ats_check.py`（机筛自检）、`scripts/fit_report.py`（一页排版报告）、`scripts/ats_fix.py`、`scripts/addphoto.py`、`scripts/pdf_tools.py`、`scripts/core.py`。
- `examples/example_cn.py`、`examples/example_en.py`：虚构人物的完整 build 脚本，参考写法用。

## 写 build 脚本

每投一个岗位，就在工作目录下建一个子文件夹（例 `投递/公司_岗位/`），在里面新建 build 脚本（例 `build_公司_岗位.py`）并在里面跑 `build.py`。PDF 默认用 profile 里固定的文件名，几份放在同一个文件夹会互相覆盖。

```python
from helpers_cn import *          # 英文版:from helpers_en import *
body = header(info_line='可到岗:2027.06 起全职(每周 5 天)') + [
    section('教育背景'),
    entry('学校  School', '城市'),
    sub('学位 · 专业', '2023.09 – 2027.06'),
    bullet('**相关课程:**……'),
    section('实习经历'),
    entry('公司 · 部门', '城市'),
    sub('岗位', '2025.07 – 2025.12'),
    bullet('做了什么分析,得出什么判断,提出什么建议,结果是……'),
    ...
]
finish(body)
```

- `header()` 读 `profile.json` 生成姓名和联系方式行（电话、邮箱、LinkedIn、个人网站，空的字段自动跳过；网址显示完整地址，方便机筛读取）。
- 英文版用 `helpers_en`，字体是 Calibri，板块标题自动大写；`header(info_line=...)` 那一行适合写 "Available full-time from …"。
- `bullet()` 里用 `**粗体**`。经历要点里少用"粗体标签:"开头（像套模版），技能栏可以用。

## 出文件

出文件（在工作目录里跑）：

```bash
python <skill>/scripts/build.py build_xx.py 张三_简历_XX版 cn photo              # 中文,带照片
python <skill>/scripts/build.py build_xx.py Zhang_San_Resume_XX en               # 英文,不带照片
python <skill>/scripts/build.py build_xx.py ... --phone "+65 8000 0000"          # 临时换电话(比如投海外岗位)
python <skill>/scripts/build.py build_xx.py ... --jd jd_公司_岗位.txt            # 同时检查 JD 关键词覆盖
```

- `python` 换成本机的命令（macOS / Linux 一般是 `python3`，Windows 是 `python` 或 `py`）；Windows 路径用 `\` 或 `/` 都行，含空格的路径加引号。
- PDF 转换：Windows 依次试 Microsoft Word → WPS → LibreOffice；macOS / Linux 依次试 LibreOffice → Microsoft Word for Mac（Word for Mac 有沙盒，工作目录放在 ~/Documents 或 ~/Desktop 下最稳）。都失败时，让用户用 Word / WPS 打开 docx 另存为 PDF，再单独跑 `python <skill>/scripts/ats_check.py xx.docx xx.pdf`。
- 文本文件（JD 关键词、profile.json）按 UTF-8 读，Windows 记事本存的带 BOM 文件也能读。
- 页数、预览图、PDF 文本检查用 PyMuPDF（`pip install pymupdf`）或 poppler。
- **一页压不下或留白**：先看 `fit_report.py` 的输出（build.py 会自动打印；也可以单独跑 `python <skill>/scripts/fit_report.py xx.pdf --docx xx.docx`）：它报出溢出几行、还能放几行，并列出"短尾行"（某条要点最后一行只有几个字，删掉就少一行）。按短尾行清单删字，不要一点一点试。
- **JD 关键词文件**：每行一个词，`必须:` 开头是硬性要求，同义词用 `/` 隔开（例 `必须:SQL`、`数据分析/data analysis`）。
- **中英合并成一个文档**（第 1 页中文、第 2 页英文）：去掉 w14:paraId；在英文第一段的 pPr 里插入 `<w:pageBreakBefore/>`；不要单独插一个分页段落，否则会多出空白页。
