#!/usr/bin/env python3
"""出一份简历(docx + pdf + 预览图 + 机筛自检)。Windows / macOS / Linux 通用,只需要 Python。
在这一份简历的工作文件夹里跑:

    python <skill>/scripts/build.py my_build.py 输出文件名 cn photo     # 中文版,带照片(profile.json 里要有 "photo")
    python <skill>/scripts/build.py my_build.py Output_Name en           # 英文版,不带照片
    python <skill>/scripts/build.py my_build.py 输出文件名 cn --phone "+65 8000 0000"   # 临时换一个电话
    python <skill>/scripts/build.py my_build.py 输出文件名 cn --jd jd_公司_岗位.txt     # 顺便跑 JD 关键词覆盖

macOS / Linux 上命令一般是 python3,Windows 上一般是 python 或 py。
个人信息来自 profile.json(找不到就用虚构的 profile.example.json 并提示)。
PDF 文件名默认用 profile 的 pdf_name_cn / pdf_name_en(投递时 PDF 只带人名),Word 保留你给的输出文件名。
"""
import functools
import json
import os
import shutil
import subprocess
import sys
import zipfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

print = functools.partial(print, flush=True)  # keep order with child processes
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)


def usage():
    print(__doc__)
    sys.exit(1)


args = sys.argv[1:]
opts = {}
for flag in ('--phone', '--jd'):
    if flag in args:
        i = args.index(flag)
        if i + 1 >= len(args):
            usage()
        opts[flag] = args[i + 1]
        del args[i:i + 2]
if len(args) < 2:
    usage()
build, out = args[0], args[1]
lang = args[2] if len(args) > 2 else 'cn'
photo = len(args) > 3 and args[3] == 'photo'

env = dict(os.environ)
env['SKILL_DIR'] = SKILL_DIR
env['PYTHONPATH'] = HERE + (os.pathsep + env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
env['PYTHONIOENCODING'] = 'utf-8'
env['PYTHONUTF8'] = '1'
if opts.get('--phone'):
    env['PHONE'] = opts['--phone']
jd = opts.get('--jd') or env.get('JD')


def py(*a, quiet=True):
    r = subprocess.run([sys.executable, *a], env=env,
                       stdout=subprocess.DEVNULL if quiet else None)
    return r.returncode


def profile():
    for c in (env.get('RESUME_PROFILE'), 'profile.json', os.path.join(SKILL_DIR, 'profile.json'),
              os.path.join(SKILL_DIR, 'profile.example.json')):
        if c and os.path.isfile(c):
            return c, json.load(open(c, encoding='utf-8-sig'))
    return None, {}


tpl = os.path.join(SKILL_DIR, 'assets', 'template_%s.docx' % lang)
if not os.path.isfile(tpl):
    sys.exit('no template: ' + tpl)
if not os.path.isfile(build):
    sys.exit('no build script: ' + build)

# 1. 解开模版 → 跑 build 脚本 → 自动修正
shutil.rmtree('un', ignore_errors=True)
zipfile.ZipFile(tpl).extractall('un')
if py(build):
    sys.exit('build 脚本出错,看上面的报错')
py(os.path.join(HERE, 'ats_fix.py'))

# 2. 可选证件照
ppath, P = profile()
if photo:
    ph = P.get('photo') or ''
    if ph and not os.path.isabs(ph):
        ph = os.path.join(os.path.dirname(os.path.abspath(ppath)), ph)
    if ph and os.path.isfile(ph):
        py(os.path.join(HERE, 'addphoto.py'), ph)
    else:
        print('⚠️ profile 里没有可用的 photo,跳过照片')

# 3. 打包 docx([Content_Types].xml 放第一个)
pdf_name = P.get('pdf_name_' + lang) or out
docx = out + '.docx'
if os.path.exists(docx):
    os.remove(docx)
with zipfile.ZipFile(docx, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join('un', '[Content_Types].xml'), '[Content_Types].xml')
    for root, _, files in os.walk('un'):
        for f in sorted(files):
            full = os.path.join(root, f)
            arc = os.path.relpath(full, 'un').replace(os.sep, '/')
            if arc != '[Content_Types].xml':
                z.write(full, arc)
shutil.rmtree('un', ignore_errors=True)

# 4. 转 PDF → 页数 → 预览图 → 机筛自检
sys.path.insert(0, HERE)
import pdf_tools  # noqa: E402

pdf = pdf_name + '.pdf'
if not pdf_tools.convert(docx, pdf):
    print('⚠️ 没能转 PDF(装 LibreOffice,或用 Microsoft Word 打开 docx 另存为 PDF)')
    sys.exit(0)
pdf_tools.clean_metadata(pdf, P.get('author') or P.get('name_en') or P.get('name_cn') or '')
print('%s -> %s  pages: %s   # 必须是 1' % (docx, pdf, pdf_tools.pages(pdf)))
pdf_tools.png(pdf, 'preview_' + pdf_name)  # 看图:底部不能留白,也不能溢出
py(os.path.join(HERE, 'fit_report.py'), pdf, '--docx', docx, '--auto', quiet=False)  # 溢出或留白时才输出
check = [os.path.join(HERE, 'ats_check.py'), docx, pdf] + (['--jd', jd] if jd else [])
if py(*check, quiet=False):
    print('⚠️ 机筛自检没通过,按上面的 ❌ 逐条改完再交付')
