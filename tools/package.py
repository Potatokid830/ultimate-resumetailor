#!/usr/bin/env python3
"""把这个 skill 打包成能直接上传的 zip。

    python tools/package.py                               # WorkBuddy:dist/ultimate-resume-tailor-workbuddy-<版本>.zip
    python tools/package.py --name resume-tailor-ats      # WorkBuddy 上名字被占时换一个
    python tools/package.py --version 1.1.0 --author 你的名字
    python tools/package.py --target claude               # Claude.ai / 桌面版:dist/resume-tailor-claude.zip

为什么单独打包,而不是直接压缩文件夹:
- 只打包 git 跟踪的文件(git ls-files),你本地的 profile.json、materials.md、照片、
  生成的简历和 .notes.md 都不会被带进去。
- WorkBuddy 要求 SKILL.md 在 zip 根目录(不能多套一层文件夹),并读取 display_name、
  description_zh / description_en、category、version、author 等字段。这些字段只写进
  zip 里的 SKILL.md,仓库里的 SKILL.md 保持 Agent Skills 标准格式,不影响其他 AI 工具。
- Claude(support.claude.com「How to create custom skills」):zip 里要有一层和 skill 名字相同的
  文件夹(resume-tailor/SKILL.md),description 最多 200 个字符。仓库里的 description 更长,
  只在 zip 里换成 CLAUDE_DESCRIPTION。不放 docs/(README 截图)、tools/、tests/、.github/。
- 打包后自动检查:没有个人文件、联系方式只有示例里的虚构值、头部格式正确、大小不超过 10 MB。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import zipfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELDS = {
    'display_name': '土豆简历顾问',
    'display_name_en': 'Potato Resume Consultant',
    'description_zh': ('按 JD 定制能过机筛的一页中英文简历：资格核查、从全部真实经历里重新选材、按目标行业改写、'
                       'JD 技能先写后学并附速成清单、机筛自检和 HR 挑刺，一页 Word 和 PDF 直接交付，'
                       '附面试速查卡和网申纯文本；不想建素材库也能先做简历体检，逐句拆解夸大风险。不编造经历，每句话都能在你的素材库里找到出处。'),
    'description_en': ('Tailor a one-page Chinese or English resume to a job description: eligibility check, '
                       'selection from your full real experience, industry-specific rewriting, ATS self-check '
                       'and recruiter critique. Outputs Word and PDF plus an interview cheat sheet and '
                       'form-ready plain text. A quick resume check-up flags overstated claims line by line. Never fabricates experience.'),
    'category': '求职招聘',
}

# Claude.ai 上传时的 description(官方上限 200 个字符;保留主要触发词)
CLAUDE_DESCRIPTION = ('土豆简历顾问：记住你的全部经历和投递记录，按 JD 定制能过机筛的一页中英文简历，不编经历和数字。'
                      '改简历、简历体检、网申、海投、投实习/校招/社招、过机筛时用。Tailor a one-page resume to a JD.')

# 不进 zip 的跟踪文件:仓库维护用的东西
EXCLUDE = {
    'workbuddy': ('.gitignore', 'tools/', 'tests/', '.github/'),  # docs/ 留着:平台详情页会展示 README 里的示例图
    'claude': ('.gitignore', 'tools/', 'tests/', '.github/', 'docs/'),  # 运行时用不到截图
}
# 绝不能出现在 zip 里的文件名(个人数据)
PERSONAL = re.compile(r'(^|/)(profile\.json|materials\.md|applications\.md|photo\.[a-z]+|.*\.notes\.md)$', re.I)
# 示例里允许出现的虚构联系方式
OK_EMAIL = re.compile(r'@example\.com$', re.I)
OK_PHONE = {'+86 138 0000 0000', '+65 8000 0000'}


def q(v):
    return json.dumps(v, ensure_ascii=False)  # JSON 字符串也是合法的 YAML 双引号字符串


def add_fields(skill_md, extra):
    m = re.match(r'---\n(.*?)\n---\n', skill_md, re.S)
    if not m:
        sys.exit('SKILL.md 开头没有 --- 包起来的头部')
    head = m.group(1)
    if 'name' in extra:  # 覆盖仓库里的 name(WorkBuddy 上 resume-tailor 已被别人注册)
        head = re.sub(r'^name: .*$', 'name: ' + extra['name'], head, count=1, flags=re.M)
    have = set(re.findall(r'^([A-Za-z_]+):', head, re.M))
    lines = [head] + ['%s: %s' % (k, q(v)) for k, v in extra.items() if k not in have]
    return '---\n' + '\n'.join(lines) + '\n---\n' + skill_md[m.end():]


def set_description(skill_md, desc):
    m = re.match(r'---\n(.*?)\n---\n', skill_md, re.S)
    head = re.sub(r'^description: .*$', lambda _: 'description: ' + desc, m.group(1), count=1, flags=re.M)
    return '---\n' + head + '\n---\n' + skill_md[m.end():]


def check_head(skill_md, target='workbuddy'):
    head = re.match(r'---\n(.*?)\n---\n', skill_md, re.S).group(1)
    errs = []
    for ln in head.split('\n'):
        if not re.match(r'^[A-Za-z_]+: \S', ln):
            errs.append('头部这一行格式不对(要 "key: value",冒号后一个空格):' + ln[:40])
        elif re.search(r'[“”‘’]', ln.split(': ', 1)[1][:1]):
            errs.append('值用了中文引号:' + ln[:40])
    need = ('name', 'description') if target == 'claude' else (
        'name', 'description', 'display_name', 'display_name_en', 'description_zh', 'description_en',
        'category', 'version', 'author')
    for k in need:
        if not re.search(r'^%s: ' % k, head, re.M):
            errs.append('缺字段 ' + k)
    nm = re.search(r'^name: (.*)$', head, re.M)
    if nm and not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', nm.group(1)):
        errs.append('name 只能用小写字母、数字和连字符:' + nm.group(1))
    ds = re.search(r'^description: (.*)$', head, re.M)
    if target == 'claude' and ds and len(ds.group(1)) > 200:
        errs.append('description 超过 200 个字符(%d)' % len(ds.group(1)))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=('workbuddy', 'claude'), default='workbuddy')
    ap.add_argument('--name', default=None,
                    help='WorkBuddy 默认 ultimate-resume-tailor(resume-tailor 已被别人注册);Claude 默认 resume-tailor')
    ap.add_argument('--version', default='1.0.0')
    ap.add_argument('--author', default='Potatokid830')
    ap.add_argument('--category', default=FIELDS['category'])
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    claude = a.target == 'claude'
    a.name = a.name or ('resume-tailor' if claude else 'ultimate-resume-tailor')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', a.name):
        sys.exit('--name 只能用小写字母、数字和连字符')
    files = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split('\0')
    files = [f for f in files if f and not f.startswith(EXCLUDE[a.target])]

    extra = dict(FIELDS, name=a.name, category=a.category, version=a.version, author=a.author)
    if claude:  # 固定文件名,README 可以直接链到 releases/latest/download/resume-tailor-claude.zip
        out = a.out or os.path.join(ROOT, 'dist', '%s-claude.zip' % a.name)
    else:
        out = a.out or os.path.join(ROOT, 'dist', '%s-workbuddy-%s.zip' % (a.name, a.version))
    os.makedirs(os.path.dirname(out), exist_ok=True)

    problems = []
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if PERSONAL.search(f):
                problems.append('个人文件被 git 跟踪了,先移出仓库:' + f)
                continue
            data = open(os.path.join(ROOT, f), 'rb').read()
            if f == 'SKILL.md':
                if claude:
                    txt = add_fields(data.decode('utf-8'), {'name': a.name})
                    txt = set_description(txt, CLAUDE_DESCRIPTION)
                else:
                    txt = add_fields(data.decode('utf-8'), extra)
                data = txt.encode('utf-8')
                problems += check_head(txt, a.target)
            if f.endswith(('.md', '.py', '.json', '.sh')):
                txt = data.decode('utf-8', 'replace')
                for em in set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', txt)):
                    if not OK_EMAIL.search(em) and 'noreply' not in em:
                        problems.append('%s 里有真实邮箱?%s' % (f, em))
                for ph in set(re.findall(r'\+\d{2,3}[ \d]{8,14}\d', txt)):
                    if ph.strip() not in OK_PHONE:
                        problems.append('%s 里有真实电话?%s' % (f, ph))
            # WorkBuddy:SKILL.md 在根目录;Claude:套一层和 name 同名的文件夹
            z.writestr(a.name + '/' + f if claude else f, data)

    size = len(buf.getvalue())
    if size > 10 * 1024 * 1024:
        problems.append('zip 超过 10 MB(%.1f MB)' % (size / 1048576))
    if problems:
        print('没有生成 zip,先处理这些问题:')
        for p in problems:
            print('❌', p)
        sys.exit(1)
    open(out, 'wb').write(buf.getvalue())
    print('已生成 %s(%d 个文件,%.0f KB)' % (os.path.relpath(out, ROOT), len(files), size / 1024))
    if claude:
        print('结构:%s/SKILL.md;description %d 个字符' % (a.name, len(CLAUDE_DESCRIPTION)))
        print('在 Claude.ai:Customize → Skills → + → Create skill → Upload a skill。')
    else:
        print('头部字段:name=%s version=%s author=%s category=%s' % (a.name, a.version, a.author, a.category))
        print('上传前再解压看一遍;分类以后台下拉框为准,不一致就在后台改。')


if __name__ == '__main__':
    main()
