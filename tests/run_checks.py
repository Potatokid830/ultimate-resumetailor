"""体检模式(ats_check.py --external)的回归测试。需要 python-docx(python -m pip install --user python-docx)。

    python tests/run_checks.py

在临时文件夹里生成简历、跑检查,不碰你的 profile.json / materials.md。
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CHECK = os.path.join(SKILL, 'scripts', 'ats_check.py')
sys.path.insert(0, HERE)

try:
    from make_fixtures import make_all
except ImportError:
    sys.exit('需要 python-docx:python -m pip install --user python-docx')

failed = []


def run(docx, *extra, env_extra=None):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', **(env_extra or {}))
    env.pop('RESUME_PROFILE', None)
    r = subprocess.run([sys.executable, CHECK, docx, *extra], capture_output=True, text=True,
                       encoding='utf-8', env=env, cwd=os.path.dirname(docx))
    return r.stdout + r.stderr


def expect(name, cond, out):
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        failed.append(name)
        print('    ' + out.strip().replace('\n', '\n    '))


def n_fail(out):
    m = re.search(r'❌ (\d+),', out)
    return int(m.group(1)) if m else -1


with tempfile.TemporaryDirectory() as d:
    make_all(d)
    cn, en, bad = (os.path.join(d, f) for f in ('external_cn.docx', 'external_en.docx', 'bad_cn.docx'))

    o = run(cn, '--external')
    expect('中文普通简历 --external:❌ 0', n_fail(o) == 0, o)
    expect('中文板块:教育背景 → 实习经历 → 技能', '板块: 教育背景 → 实习经历 → 技能' in o, o)
    expect('中文:"自我驱动"不算第一人称', '第一人称' not in o, o)
    expect('中文:教育经历没写"预计"给 ⚠️', re.search(r'⚠️ 教育经历的结束时间 2023\.09-2027\.06', o), o)
    expect('--external 说明跳过了哪些检查', '跳过这些检查' in o, o)

    o = run(en, '--external')
    expect('英文普通简历 --external:❌ 0', n_fail(o) == 0, o)
    expect('英文板块:EDUCATION → EXPERIENCE → SKILLS', '板块: EDUCATION → EXPERIENCE → SKILLS' in o, o)

    o = run(bad, '--external')
    expect('有问题的简历:报第一人称 ❌', re.search(r'❌ 中文第一人称', o), o)
    expect('有问题的简历:报读不到邮箱 ❌', '❌ 读不到邮箱' in o, o)

    # 不加 --external、也没有 profile.json:不能拿虚构的示例档案(Alex Li)去查
    empty_skill = os.path.join(d, 'no_profile_skill')
    os.makedirs(empty_skill)
    o = run(cn, env_extra={'SKILL_DIR': empty_skill})
    expect('没有 profile.json 时按 --external 处理:❌ 0', n_fail(o) == 0 and '按 --external 处理' in o, o)
    expect('没有 profile.json 时不出现示例人物', 'Alex' not in o and 'alexli' not in o, o)

print()
print('全部通过' if not failed else '有 %d 项没通过:%s' % (len(failed), '、'.join(failed)))
sys.exit(1 if failed else 0)
