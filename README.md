# resume-tailor · 按 JD 定制一页简历的 AI Agent Skill

[English](#english) · 中文

一个简历定制 skill，采用开放的 [Agent Skills](https://agentskills.io) 格式，Claude、ChatGPT / Codex、GitHub Copilot、Cursor、Gemini CLI 等都能用：你给一份 JD，它帮你从**自己的全部真实经历**里挑材料，按目标行业的逻辑改写，做成**一页中文或英文简历**（docx + pdf），并在交付前跑一遍**机筛（ATS / AI 筛简历）自检**和**HR 挑刺**。

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

## 支持哪些 AI 工具

这个 skill 用的是 [Agent Skills](https://agentskills.io) 开放格式（一个文件夹，里面有 `SKILL.md` 和脚本），不只 Claude 能用。按 [agentskills.io 官方名单](https://agentskills.io/clients)，支持这个格式的常见工具有：

- **Claude**：Claude.ai、Claude 桌面版、Claude Code
- **OpenAI**：ChatGPT、Codex
- **GitHub Copilot / VS Code**
- **编程工具**：Cursor、TRAE、Kiro、Roo Code、JetBrains Junie、Amp、OpenCode、Goose、OpenHands、Factory、Tabnine 等
- **Google Gemini CLI**、**Mistral Vibe**、**Letta**、**OpenClaw**

名单在持续增加，以官网为准。不在名单上的 AI 也能用，见下面"其他 AI"。

## 安装

1. 点页面上方绿色的 **Code → Download ZIP**，下载后解压，把文件夹名改成 `resume-tailor`。
2. 把文件夹交给你用的 AI：
   - **Claude.ai / Claude 桌面版**：在 Settings → Capabilities → Skills 上传这个 zip。ChatGPT 等其他应用按 [agentskills.io 名单](https://agentskills.io/clients) 里该应用的 "Setup instructions" 操作。
   - **Claude Code、Codex、Copilot、Cursor、Gemini CLI 等编程工具**：放进它的 skills 文件夹。Claude Code 是 `~/.claude/skills/`；很多工具也认通用位置 `~/.agents/skills/`；各工具的具体位置见 [agentskills.io 名单](https://agentskills.io/clients) 里的 "Setup instructions"。不确定的话，直接对 AI 说"把这个文件夹安装成 skill"，让它帮你放。
   - **其他 AI**（不支持 skill 的）：把文件夹放在 AI 能读到的地方，对它说"读 `resume-tailor/SKILL.md`，按里面的流程帮我改简历"。
3. 对 AI 说："用 resume-tailor 帮我改简历"。

就这样。第一次使用时，AI 会读完 skill，检查你的电脑还缺什么（Python、PDF 转换工具等），征得你同意后帮你装好，再一段段问你的经历，帮你建好个人信息和素材库。你不需要自己敲任何命令。

> 出 docx / pdf 需要 AI 能在你电脑上（或它自己的沙盒里）运行命令。只能聊天、不能运行命令的 AI 也能走完整个流程（资格核查、选材、改写、HR 挑刺），只是最后要你自己把文字贴进 `assets/` 里的空白模版。

## 使用流程

对 AI 说："用 resume-tailor 帮我按这个 JD 改简历"，并贴上 JD。它会按顺序：

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

**resume-tailor** is a resume-tailoring skill in the open [Agent Skills](https://agentskills.io) format. Give it a job description and it picks material from **your entire real experience**, rewrites it in the logic of the target industry, and produces a **one-page resume in English or Chinese** (docx + pdf). Before handing it over, it runs an **ATS / AI-screening self-check** and critiques the draft the way a recruiter would.

The examples above use a fictional person; every school, company and number in them is made up.

### How it differs from "AI, polish my resume"

| Typical AI resume edit | resume-tailor |
|---|---|
| Only looks at the resume you pasted this time | Reviews your **whole experience bank** (`materials.md`) and re-selects for each JD |
| Writes straight away and invents numbers it doesn't have | **Asks before writing**: proposes what goes in, what stays out and why, and waits for your OK; asks for missing details instead of guessing |
| Polishes wording ("responsible for", "assisted with") | **Translates each experience into the target industry's logic**: analysis → judgement → recommendation → result, in the language of banking, tech, consulting and so on |
| Either skips JD skills you lack or claims "expert" | **List now, learn fast**: only skills you can pick up in a day to a week, worded honestly ("familiar with"), each with a **crash-course plan** (learning route, small portfolio project, likely interview questions) |
| No line between framing and fabrication | Clear **red lines**: grades, roles, results and certificates must be real; anything you mark ❌ never appears in any version |
| Ignores layout | Fixed template, **one full page**: no overflow, no empty space at the bottom |
| Done once the text is written | Checks **eligibility** first (graduation year, location, start date, visa), then runs the **ATS self-check** and **JD keyword coverage**, then a recruiter-style critique |

### Supported AI tools

Any agent that supports the Agent Skills format can use it. According to the [official client list](https://agentskills.io/clients), that includes:

- **Claude**: Claude.ai, Claude desktop, Claude Code
- **OpenAI**: ChatGPT, Codex
- **GitHub Copilot / VS Code**
- **Coding agents**: Cursor, TRAE, Kiro, Roo Code, JetBrains Junie, Amp, OpenCode, Goose, OpenHands, Factory, Tabnine and more
- **Others**: Google Gemini CLI, Mistral Vibe, Letta, OpenClaw

The list keeps growing; check the website for the latest. Agents without skill support can still use it (see step 2 below).

### Install

1. Click the green **Code → Download ZIP** button above, unzip it, and rename the folder to `resume-tailor`.
2. Give the folder to your AI:
   - **Claude.ai / Claude desktop**: upload the zip under Settings → Capabilities → Skills. For ChatGPT and other apps, follow that app's "Setup instructions" on the [client list](https://agentskills.io/clients).
   - **Claude Code, Codex, Copilot, Cursor, Gemini CLI and other coding agents**: put the folder in the agent's skills folder. For Claude Code that is `~/.claude/skills/`; many agents also read the shared location `~/.agents/skills/`. If you're not sure, just ask the agent to "install this folder as a skill".
   - **Any other AI** without skill support: put the folder somewhere it can read and say "Read `resume-tailor/SKILL.md` and follow it to tailor my resume".
3. Say: "Use resume-tailor to tailor my resume."

That's it. On first use the AI reads the skill, checks what your computer is missing (Python, a PDF converter and so on), installs it with your permission, and then interviews you to build your profile and experience bank. You don't need to type any commands yourself.

> Producing the docx / pdf requires an AI that can run commands on your computer (or in its own sandbox). A chat-only AI can still run the whole process (eligibility check, selection, rewriting, recruiter critique); you then paste the text into the blank template in `assets/` yourself.

### How a session goes

Say "Use resume-tailor to tailor my resume for this JD" and paste the job description. The AI then:

1. **Checks eligibility**: graduation year, location, start date and duration, visa, GPA cut-offs, application limits. Anything that fails is raised first.
2. **Reviews your whole experience bank** in `materials.md` and picks what fits the JD best.
3. **Asks before writing**: lists what goes in, the angle for each item, and what stays out and why, then waits for your OK.
4. **Asks for missing details**: numbers and feedback only you know; it never guesses.
5. **Aligns skills with the JD**: adds skills you can learn quickly, each with a crash-course plan.
6. **Builds the resume**: one full page, docx + pdf.
7. **Recruiter critique + ATS self-check**: `ats_check.py` checks section headings, contact details, font sizes, margins, tables/text boxes, document properties, PDF text extraction and JD keyword coverage.
8. **Delivers** the files with a short note: what was included, what was left out, which skills to learn, and an honest view of your interview chances.

### Your data

Your personal details live in `profile.json` (name, phone, email, links, optional photo) and your experiences in `materials.md`. Both files, your photo and every generated resume are in `.gitignore`, so they are never committed. Keep personal content out of `SKILL.md`, so the skill itself can be updated and shared safely.

### Folder structure

See the [directory tree above](#目录结构): `SKILL.md` (the workflow), `profile.example.json` and `materials.example.md` (templates you copy), `assets/` (blank Chinese and English templates), `scripts/` (build, ATS check, PDF export) and `examples/` (fictional sample builds).

### License

[MIT](LICENSE)
