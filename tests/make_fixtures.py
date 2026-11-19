"""生成几份"不是用本 skill 模版做的"普通简历,用来测体检模式(ats_check.py --external)。需要 python-docx。

    python tests/make_fixtures.py [输出文件夹]

external_cn.docx / external_en.docx:没有问题的普通简历,体检应该 ❌ 0。
bad_cn.docx:真有问题(有"我负责"、没有邮箱),体检必须报出来。
"""
import os
import sys

from docx import Document
from docx.shared import Pt


def make(path, name, contact, sections):
    d = Document()
    cp = d.core_properties
    cp.author = cp.last_modified_by = name
    cp.comments = cp.title = cp.subject = cp.keywords = ''
    r = d.add_paragraph().add_run(name); r.bold = True; r.font.size = Pt(16)
    d.add_paragraph(contact)
    for h, items in sections:
        hr = d.add_paragraph().add_run(h); hr.bold = True; hr.font.size = Pt(12)
        for it in items:
            d.add_paragraph(it, style='List Bullet')
    d.save(path)


def make_all(out='.'):
    os.makedirs(out, exist_ok=True)
    j = lambda f: os.path.join(out, f)
    make(j('external_cn.docx'), '张三', '电话：138 0000 0000 | 邮箱：zhangsan@example.com', [
        ('教育背景', ['某某大学 金融学 本科 2023.09-2027.06']),
        ('实习经历', ['某券商 研究所 实习生 2025.07-2025.12', '负责行业研究，撰写行业深度报告，培养了自我驱动能力。']),
        ('技能', ['Excel、SQL、Python']),
    ])
    make(j('external_en.docx'), 'San Zhang', 'Phone: +86 138 0000 0000 | Email: san.zhang@example.com', [
        ('EDUCATION', ['Example University, BSc Finance, Sep 2023 - Jun 2027']),
        ('EXPERIENCE', ['Example Securities, Research Intern, Jul 2025 - Dec 2025', 'Built a tracker of 8 platforms over 20 quarters.']),
        ('SKILLS', ['Excel, SQL, Python']),
    ])
    make(j('bad_cn.docx'), '张三', '电话：138 0000 0000', [
        ('教育背景', ['某某大学 金融学 本科 2023.09-2027.06（预计）']),
        ('实习经历', ['某券商 研究所 实习生 2025.07-2025.12', '我负责行业研究，撰写行业深度报告。']),
        ('技能', ['Excel、SQL、Python']),
    ])


if __name__ == '__main__':
    make_all(sys.argv[1] if len(sys.argv) > 1 else '.')
