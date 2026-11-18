#!/usr/bin/env python3
"""把这个 skill 打包成上传 WorkBuddy 开放平台用的 zip。

    python tools/package_workbuddy.py                    # 输出 dist/resume-tailor-workbuddy-<版本>.zip
    python tools/package_workbuddy.py --version 1.1.0 --author 你的名字

为什么单独打包,而不是直接压缩文件夹:
- 只打包 git 跟踪的文件(git ls-files),你本地的 profile.json、materials.md、照片、
  生成的简历和 .notes.md 都不会被带进去。
- WorkBuddy 要求 SKILL.md 在 zip 根目录(不能多套一层文件夹),并读取 display_name、
  description_zh / description_en、category、version、author 等字段。这些字段只写进
  zip 里的 SKILL.md,仓库里的 SKILL.md 保持 Agent Skills 标准格式,不影响其他 AI 工具。
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
    'display_name': '简历定制（过机筛版）',
    'display_name_en': 'Resume Tailor',
    'description_zh': ('按 JD 定制能过机筛的一页中英文简历：资格核查、从全部真实经历里重新选材、按目标行业改写、'
                       'JD 技能先写后学并附速成清单、机筛自检和 HR 挑刺，一页 Word 和 PDF 直接交付，'
                       '附面试速查卡和网申纯文本。不编造经历，每句话都能在你的素材库里找到出处。'),
    'description_en': ('Tailor a one-page Chinese or English resume to a job description: eligibility check, '
                       'selection from your full real experience, industry-specific rewriting, ATS self-check '
                       'and recruiter critique. Outputs Word and PDF plus an interview cheat sheet and '
                       'form-ready plain text. Never fabricates experience.'),
    'category': '求职招聘',
}

# 不进 zip 的跟踪文件:仓库维护用的东西
EXCLUDE = ('.gitignore', 'tools/')  # docs/ 留着:README 里的示例图在里面
# 绝不能出现在 zip 里的文件名(个人数据)
PERSONAL = re.compile(r'(^|/)(profile\.json|materials\.md|photo\.[a-z]+|.*\.notes\.md)$', re.I)
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
    have = set(re.findall(r'^([A-Za-z_]+):', head, re.M))
    lines = [head] + ['%s: %s' % (k, q(v)) for k, v in extra.items() if k not in have]
    return '---\n' + '\n'.join(lines) + '\n---\n' + skill_md[m.end():]


def check_head(skill_md):
    head = re.match(r'---\n(.*?)\n---\n', skill_md, re.S).group(1)
    errs = []
    for ln in head.split('\n'):
        if not re.match(r'^[A-Za-z_]+: \S', ln):
            errs.append('头部这一行格式不对(要 "key: value",冒号后一个空格):' + ln[:40])
        elif re.search(r'[“”‘’]', ln.split(': ', 1)[1][:1]):
            errs.append('值用了中文引号:' + ln[:40])
    for k in ('name', 'description', 'display_name', 'display_name_en', 'description_zh', 'description_en',
              'category', 'version', 'author'):
        if not re.search(r'^%s: ' % k, head, re.M):
            errs.append('缺字段 ' + k)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='1.0.0')
    ap.add_argument('--author', default='Potatokid830')
    ap.add_argument('--category', default=FIELDS['category'])
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    files = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in files if not f.startswith(EXCLUDE)]

    extra = dict(FIELDS, category=a.category, version=a.version, author=a.author)
    out = a.out or os.path.join(ROOT, 'dist', 'resume-tailor-workbuddy-%s.zip' % a.version)
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
                data = add_fields(data.decode('utf-8'), extra).encode('utf-8')
                problems += check_head(data.decode('utf-8'))
            if f.endswith(('.md', '.py', '.json', '.sh')):
                txt = data.decode('utf-8', 'replace')
                for em in set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', txt)):
                    if not OK_EMAIL.search(em) and 'noreply' not in em:
                        problems.append('%s 里有真实邮箱?%s' % (f, em))
                for ph in set(re.findall(r'\+\d{2,3}[ \d]{8,14}\d', txt)):
                    if ph.strip() not in OK_PHONE:
                        problems.append('%s 里有真实电话?%s' % (f, ph))
            z.writestr(f, data)  # SKILL.md 在根目录,不套外层文件夹

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
    print('头部字段:version=%s author=%s category=%s' % (a.version, a.author, a.category))
    print('上传前再解压看一遍;分类以后台下拉框为准,不一致就在后台改。')


if __name__ == '__main__':
    main()
