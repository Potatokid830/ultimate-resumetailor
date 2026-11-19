# 首次使用：检查和安装依赖

SKILL.md「首次使用」第 1 步的展开。文中"第 X 节"都指 SKILL.md 里的章节。底线：缺什么先说清楚要装什么、为什么，**征得用户同意后再装**；不要让用户自己敲命令。

- **先确认系统**（Windows / macOS / Linux），下面的命令按系统选。所有脚本都是 Python，**三个系统都能用，不需要 bash、zip**。
- **Python 3.8+**（必需）。下文的 `python` 指本机能用的那个命令：macOS / Linux 一般是 `python3`；Windows 一般是 `python` 或 `py`。
  - Windows 按这个顺序来：
    1. **先查有没有**：依次试 `py --version`、`python --version`。只有输出 `Python 3.x` 才算有。`python` 打开了 Microsoft Store、什么都不输出，或报"找不到"，都是 Windows 自带的假入口，**不算装了**。
    2. **没有就装**（先征得同意）：有 winget 时用 `winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements`（装在用户目录，一般不需要管理员权限；如果还是弹出权限确认框，告诉用户点"是"）。
    3. **没有 winget**（老版本 Windows 10、公司电脑常见，`winget --version` 报错）：引导用户到 python.org 下载 Windows 安装包，安装第一页**勾选"Add python.exe to PATH"**，再点 Install Now；装完告诉你一声。
    4. **装完当前终端可能还找不到**：Windows 只在新开的终端里刷新 PATH，所以装完立刻跑 `python` 报"找不到"不代表没装好。按顺序试：`py --version` → 完整路径 `"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" --version`（PowerShell 里写 `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" --version`）→ 让用户重启这个 AI 工具或终端后再试。找到能用的命令后，本次后面都用它（包括 `-m pip install`）。
    5. 都不行（公司电脑禁止安装等）：告诉用户原因，改走不出文件的方式：照常完成选材、改写、HR 挑刺、速查卡和网申纯文本，最后由用户把文字贴进 `assets/` 里的空白模版，用 Word / WPS 另存为 PDF。
  - macOS：一般自带 `python3`；没有就从 python.org 安装，或 `brew install python`。
- PyMuPDF（**要装**：页数、底部留白检查、预览图、PDF 文本检查都靠它；没有它只能退回 poppler，很多检查会跳过）：`python -m pip install --user pymupdf`。
- PDF 转换（有一个就行）：
  - Windows：装了 Microsoft Word 就直接用（脚本通过 PowerShell 调用 Word 导出，不弹窗）；只有 WPS 时会尝试用 WPS；都不行就装 LibreOffice（`winget install -e --id TheDocumentFoundation.LibreOffice --accept-package-agreements --accept-source-agreements`，或到 libreoffice.org 下载；装完不用改 PATH，脚本会到 Program Files 里找）。
  - macOS：已装 Microsoft Word 就直接用；否则装 LibreOffice（有 Homebrew 时 `brew install --cask libreoffice`，没有就到 libreoffice.org 下载）。
  - Linux / Claude.ai 沙盒：用 LibreOffice（`soffice`），沙盒里一般已有。
- 装完跑一次示例，确认能出一页 PDF：在一个工作文件夹里运行 `python <skill>/scripts/build.py <skill>/examples/example_cn.py 示例 cn`。
