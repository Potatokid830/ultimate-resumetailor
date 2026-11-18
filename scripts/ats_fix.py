#!/usr/bin/env python3
"""build.py 在 build 脚本之后自动调用:
- 毕业时间后补"(预计)" / "(Expected)"(读 profile 的 graduation_cn / graduation_en,还没毕业才填)
- 页边距不小于 1.1 cm(太窄部分系统会裁切)
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import P  # noqa: E402

p = 'un/word/document.xml'
d = open(p, encoding='utf-8').read()

g_cn, g_en = P.get('graduation_cn'), P.get('graduation_en')
if g_cn and '预计' not in d and g_cn in d:
    d = re.sub(re.escape(g_cn) + r'(?!\s*[(（]预计)', g_cn + '(预计)', d, count=1)
if g_en and 'Expected' not in d and g_en in d:
    d = re.sub(re.escape(g_en) + r'(?! \(Expected\))', g_en + ' (Expected)', d, count=1)


def fix(m):
    s = m.group(0)
    for k in ('top', 'bottom', 'left', 'right'):
        s = re.sub(r'w:%s="(\d+)"' % k, lambda x: 'w:%s="%d"' % (k, max(int(x.group(1)), 640)), s)
    return s


d = re.sub(r'<w:pgMar [^>]*/>', fix, d)
open(p, 'w', encoding='utf-8').write(d)
print('ats fix ok')
