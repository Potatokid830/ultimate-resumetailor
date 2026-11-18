# resume-tailor · 按 JD 定制一页简历的 Claude Skill

[English](#english) · 中文

一个给 Claude（Claude Code / Claude.ai Skills）用的简历定制 skill：你给一份 JD，它帮你从**自己的全部真实经历**里挑材料，按目标行业的逻辑改写，做成**一页中文或英文简历**（docx + pdf），并在交付前跑一遍**机筛（ATS / AI 筛简历）自检**和**HR 挑刺**。

<p align="center">
  <img src="docs/example_cn.png" width="45%" alt="中文示例(虚构人物)">
  <img src="docs/example_en.png" width="45%" alt="English example (fictional person)">
</p>
<p align="center"><sub>示例简历里的人物、学校、公司、数字都是虚构的。</sub></p>

## 和"让 AI 帮我改简历"有什么不一样

| 普通 AI 改简历 | resume-tailor |
|---|---|
| 只看你这次贴进来的那版简历 | 先把你的**全部经历素材库**过一遍，按 JD 重新选材 |
| 拿到就写，缺数字就编一个 | **先问再写**：先列"放什么、不放什么、为什么"，你确认后才动手；缺细节就追问，不猜 |
| 润色措辞，"负责""协助""参与" | **按目标行业翻译经历**：分析 → 判断 → 建议 → 结果，用券商 / 互联网 / 咨询各自的语言写 |
| 要么不敢写 JD 技能，要么乱写"精通" | **先写后学**：只写 1 天到 1 周能上手的技能，用词实诚，并附**速成清单**（学习路线、练手项目、面试题） |
| 包装和编造没有边界 | 明确的**红线**：GPA、经历、结果、证书必须真实；你标过 ❌ 的内容任何版本都不写 |
| 不在乎排版 | 固定模版，**一页写满**，不溢出、不留白 |
| 交付就结束 | 先查**资格**（届别、地点、到岗时间、签证），交付前跑 **ATS 自检** + **JD 关键词覆盖**，再站在 HR 角度挑刺 |

## 安装

1. 点页面上方绿色的 **Code → Download ZIP**，下载后解压。
2. 把解压出来的文件夹交给 Claude：
   - **Claude Code**：放进 `~/.claude/skills/`（文件夹名改成 `resume-tailor`）。
   - **Claude.ai / Claude 桌面版**：在 Settings → Capabilities → Skills 里上传这个 zip。
3. 对 Claude 说："用 resume-tailor 帮我改简历"。

就这样。第一次使用时，Claude 会读完 skill，检查你的电脑还缺什么（Python、PDF 转换工具等），征得你同意后帮你装好，再一段段问你的经历，帮你建好个人信息和素材库。你不需要自己敲任何命令。

## 使用流程

对 Claude 说："用 resume-tailor 帮我按这个 JD 改简历"，并贴上 JD。它会按顺序：

1. **资格核查**：届别、地点、到岗时间、签证、成绩门槛、投递数量限制。有不过的先告诉你。
2. **回顾全部经历**：把 `materials.md` 整份过一遍，按 JD 挑出最相关的。
3. **先问再写**：列出"放哪些、每段写什么角度、哪些不放及原因"，等你确认。
4. **缺细节就追问**：只有你知道的数字和反馈，直接问你。
5. **技能对齐 JD**：短期能学会的先写上，附速成清单。
6. **出稿**：一页 docx + pdf，一页写满。
7. **HR 挑刺 + 机筛自检**：`ats_check.py` 检查板块标题、联系方式、字号、页边距、表格/文本框、文档属性、PDF 可解析性和 JD 关键词覆盖。
8. **交付**：附文件，并说明选了什么、没选什么、哪些技能要补、能不能拿面试的坦白评价。

## 目录结构

```
resume-tailor/
├── SKILL.md                 # skill 本体:流程、包装与编造的边界、行业翻译、先写后学、模版规则
├── profile.example.json     # 个人信息配置示例(虚构)→ 复制成 profile.json
├── materials.example.md     # 经历素材库模版 + 填写说明 → 复制成 materials.md
├── assets/
│   ├── template_cn.docx     # 中文空白模版(占位符)
│   └── template_en.docx     # 英文空白模版(占位符)
├── scripts/
│   ├── build.sh             # 一条命令:docx → pdf → 预览图 → 机筛自检
│   ├── core.py              # 读模版和 profile.json,finish() 写文档属性
│   ├── helpers_cn.py        # 中文积木:header / section / entry / sub / bullet
│   ├── helpers_en.py        # 英文积木(Calibri,标题大写)
│   ├── ats_fix.py           # 自动补"预计/Expected"、修页边距
│   ├── ats_check.py         # 机筛自检 + JD 关键词覆盖
│   ├── addphoto.py          # 可选证件照
│   └── pdf_tools.py         # 转 PDF(LibreOffice / Word)、页数、预览图
├── examples/
│   ├── example_cn.py        # 虚构人物中文示例(互联网商分)
│   ├── example_en.py        # 虚构人物英文示例(strategy / business analyst)
│   └── photo_example.jpg    # 占位头像
└── docs/                    # README 用的示例截图和 PDF
```

## 隐私

你的 `profile.json`、`materials.md`、照片和生成的简历都在 `.gitignore` 里。个人内容只放这两份文件，不要写进 `SKILL.md`，这样 skill 可以放心更新和分享。

## License

[MIT](LICENSE)

---

## English

**resume-tailor** is a Claude skill that tailors a **one-page Chinese or English resume** to a specific job description and checks it against ATS / AI screening before handing it over.

What makes it different from asking an AI to "polish my resume":

- **Eligibility check first**: graduation year, location, start date and duration, visa, GPA cut-offs, application limits.
- **Reviews your whole experience bank** (`materials.md`), not just the resume you pasted, and picks what fits the JD.
- **Asks before writing**: proposes what goes in, what stays out and why, and waits for your OK; asks for missing numbers instead of inventing them.
- **Translates experience into the target industry's logic**: analysis → judgement → recommendation → result.
- **"List now, learn fast"** for JD skills you can pick up in a day to a week, worded honestly ("familiar with"), each with a crash-course plan and likely interview questions.
- **Clear line between framing and fabrication**: grades, roles, results and certificates must be real.
- **One full page**, fixed template, docx + pdf, then an **ATS self-check** (section headings, contact info, font sizes, margins, tables/text boxes, document properties, PDF text extraction, JD keyword coverage) and an **HR-style critique**.

Setup: click **Code → Download ZIP**, put the folder in your Claude skills folder (or upload the zip in Claude.ai Settings → Skills), and ask Claude to tailor your resume. On first use Claude checks for missing tools (Python, a PDF converter), installs them with your OK, and interviews you to build your profile and experience bank. The example people, schools, companies and numbers are fictional.
