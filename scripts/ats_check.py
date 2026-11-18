#!/usr/bin/env python3
"""简历机筛(ATS / AI 筛简历)自检。

    python scripts/ats_check.py 简历.docx [简历.pdf] [--jd jd_keywords.txt]

jd_keywords.txt:每行一个关键词;以"必须:"开头的是必须项,其余是加分项;同义词用 / 隔开(任一命中即算)。
个人红线词:写在 profile.json 的 "banned_words" 里(例如你确认过"不能这么写"的说法),命中即 ❌。
退出码 1 = 有 ❌ 必须修;只有 ⚠️ 时退出码 0,但要逐条看。

PDF 检查优先用 PyMuPDF(pip install pymupdf),没有就用 poppler 的 pdfinfo / pdftotext / pdffonts。
"""
import html
import os
import re
import shutil
import subprocess
import sys
import zipfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('SKILL_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_profile():
    import json
    sd = os.environ['SKILL_DIR']
    for c in (os.environ.get('RESUME_PROFILE'), 'profile.json', os.path.join(sd, 'profile.json'), os.path.join(sd, 'profile.example.json')):
        if c and os.path.isfile(c):
            return json.load(open(c, encoding='utf-8-sig'))
    return {}


P = load_profile()

args = sys.argv[1:]
jd = None
if '--jd' in args:
    i = args.index('--jd'); jd = args[i + 1]; del args[i:i + 2]
docx_path = args[0]
pdf_path = args[1] if len(args) > 1 else None
fails, warns = [], []
def F(m): fails.append(m)
def W(m): warns.append(m)


z = zipfile.ZipFile(docx_path)
xml = z.read('word/document.xml').decode('utf-8')
paras = re.findall(r'<w:p[ >].*?</w:p>', xml, re.S)


def ptext(p):
    return html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)))


texts = [ptext(p) for p in paras]
full = '\n'.join(texts)
is_cn = bool(re.search(r'[一-鿿]{6,}', full))

# ---------- 1. 板块标题 ----------
OK_CN = {'教育背景', '实习经历', '工作经历', '项目经历', '校园经历', '社团经历', '校园与社团经历', '专业技能', '技能', '技能与证书',
         '技能与兴趣', '证书', '荣誉奖项', '个人总结', '研究经历', '科研经历'}
OK_EN = {'EDUCATION', 'EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'INTERNSHIP EXPERIENCE', 'PROJECTS', 'LEADERSHIP',
         'LEADERSHIP & ACTIVITIES', 'ACTIVITIES', 'SKILLS', 'SKILLS & CERTIFICATIONS', 'SKILLS & INTERESTS', 'CERTIFICATIONS',
         'AWARDS', 'SUMMARY', 'RESEARCH EXPERIENCE', 'PUBLICATIONS'}
sections, sec_of = [], []
cur = '(页首)'
for p, tx in zip(paras, texts):
    if 'w:pBdr' in p and 'w:bottom' in p and tx.strip():
        cur = tx.strip(); sections.append(cur)
    sec_of.append(cur)
bad = [s for s in sections if s not in OK_CN and s.upper() not in OK_EN]
if bad: F('非标准板块标题(系统可能认不出):' + '、'.join(bad) + ' → 只用 ' + '/'.join(sorted(OK_CN)) + ' 或英文标准标题')
if not any(s == '教育背景' or s.upper() == 'EDUCATION' for s in sections): F('缺少"教育背景 / Education"板块')
if not any(s in ('实习经历', '工作经历') or 'EXPERIENCE' in s.upper() for s in sections): F('缺少"实习经历 / Experience"板块')

# ---------- 2. 口语词、红线、第一人称 ----------
COLLOQUIAL = ['果断', '砍掉', '砍了', '拉人', '拉群', '搞定', '谈下来', '地盘', '牛逼', '巨大提升', '赋能', '抓手', '闭环打法']
for w in COLLOQUIAL:
    if w in full: F('口语 / 套话:"%s"' % w)
for w in P.get('banned_words', []):
    if w and w.lower() in full.lower(): F('个人红线词(profile.banned_words):"%s"' % w)
if re.search(r'精通|expert in|mastery of', full, re.I): W('出现"精通 / expert":确认真的精通,否则改成"熟悉 / 掌握基础 / familiar with"')
if re.search(r'我', full): F('中文第一人称"我/我们":%d 处' % len(re.findall(r'我', full)))
en_fp = re.findall(r'(?<!Level )\b(I|my|me|we|our)\b', full)
if en_fp: F('英文第一人称(I/my/me/we/our):%d 处——英文简历省略主语,动词开头' % len(en_fp))

# ---------- 3. 符号与"标签 +"写法 ----------
for sym, nm in [('→', '箭头'), ('←', '箭头'), ('⇒', '箭头'), ('～', '波浪号'), ('≈', '约等号')]:
    n = full.count(sym)
    if n: W('符号"%s"(%s)%d 处——正文改用文字(如"导致""约")' % (sym, nm, n))
lab = [tx[:20] for tx in texts if re.match(r'\s*[一-鿿A-Za-z ]{1,12}\s?\+\s?[一-鿿A-Za-z ]{1,12}([\s+一-鿿A-Za-z]*)[:：]', tx)]
if lab: F('"标签 + 标签:"套模板写法 %d 处,例:%s' % (len(lab), ' / '.join(lab[:3])))
if re.search(r'\*\*', full): F('残留 Markdown 星号 **')
# 小写 L 冒充大写 I:"Al Agent"、"Al 产品"
al = re.findall(r'(?<![A-Za-z])Al(?![a-z])\s*[A-Za-z一-鿿]{0,4}', full)
if al: W('疑似把 AI 打成了 Al(小写 L)%d 处,例:%s' % (len(al), ' / '.join(al[:3])))
# 经历要点里的"粗体 + 冒号"标签 → 像模板;技能栏里可以用
lab_b, emph_b = [], []
for p_, tx, sec in zip(paras, texts, sec_of):
    if 'w:numPr' not in p_ or '技能' in sec or 'SKILL' in sec.upper() or sec in ('教育背景',) or sec.upper() == 'EDUCATION':
        continue
    for r_ in re.findall(r'<w:r>.*?</w:r>', p_, re.S):
        rpr = re.search(r'<w:rPr>(.*?)</w:rPr>', r_, re.S)
        if not rpr or not re.search(r'<w:b/>|<w:b w:val="(1|true)"/>', rpr.group(1)): continue
        rt = html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', r_))).strip()
        if not rt: continue
        (lab_b if re.search(r'[:：]\s*$', rt) else emph_b).append(rt[:14])
if lab_b: W('经历要点里有"粗体标签:"%d 处(像套模板,关键词最好在句子里自然出现),例:%s' % (len(lab_b), ' / '.join(lab_b[:3])))
if len(emph_b) > 6: W('经历要点里加粗 %d 处,太多会稀释重点,例:%s' % (len(emph_b), ' / '.join(emph_b[:3])))

# ---------- 4. 必备信息 ----------
if not re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', full): F('读不到邮箱')
if not re.search(r'\+?\d[\d\s-]{7,}\d', full): F('读不到电话')
if P.get('website'):
    host = re.sub(r'^https?://(www\.)?', '', P['website']).rstrip('/')
    if host not in full: F('缺个人网站 / 作品集:%s' % host)
if P.get('linkedin') and 'linkedin.com/in/' not in full:
    F('LinkedIn 只显示了文字,系统读不到网址——显示完整网址 linkedin.com/in/…')
g = P.get('graduation_cn') if is_cn else P.get('graduation_en')
if g and g in full and not re.search(re.escape(g) + r'[^\n]{0,6}(预计|Expected)', full):
    F('毕业时间 %s 没写"预计 / Expected"' % g)

# ---------- 5. 版式 ----------
m = re.search(r'<w:pgMar ([^>]*)/>', xml)
if m:
    mar = dict(re.findall(r'w:(top|bottom|left|right)="(\d+)"', m.group(1)))
    small = {k: round(int(v) / 567, 2) for k, v in mar.items() if int(v) < 624}
    if small: F('页边距小于 1.1 cm:%s(cm)' % small)
sizes = [int(s) for s in re.findall(r'<w:sz w:val="(\d+)"', xml)]
if sizes and min(sizes) < 18: F('有小于 9 磅的字(最小 %.1f 磅)' % (min(sizes) / 2))
body_sz = [int(s) for p in paras if 'w:numPr' in p for s in re.findall(r'<w:sz w:val="(\d+)"', p)]
if body_sz and min(body_sz) < 20: F('正文要点小于 10 磅(最小 %.1f 磅)' % (min(body_sz) / 2))
if '<w:tbl>' in xml or 'txbx' in xml: F('文档里有表格或文本框,部分系统会读乱顺序')
hf_names = [n for n in z.namelist() if re.match(r'word/(header|footer)', n)]
if hf_names:
    hf = ''.join(z.read(n).decode('utf-8', 'ignore') for n in hf_names)
    if re.findall(r'<w:t[^>]*>[^<]+<', hf): F('页眉/页脚里有文字,很多系统会跳过')

# ---------- 6. 文档属性 ----------
props = ''.join(z.read(n).decode('utf-8', 'ignore') for n in z.namelist() if n.startswith('docProps/'))
if re.search(r'python|docx|openpyxl|generated', props, re.I): F('docProps 里有生成工具痕迹(python / docx / generated)')
author = P.get('author') or P.get('name_en') or P.get('name_cn')
for tag in ['dc:creator', 'cp:lastModifiedBy']:
    v = re.search(r'<%s>(.*?)</%s>' % (tag, tag), props)
    if author and v and v.group(1) != author: F('%s 不是 %s:%s' % (tag, author, v.group(1)))

# ---------- 7. PDF 解析测试 ----------
norm = lambda s: re.sub(r'\s+', '', s)


def pdf_fill_gap(path):
    """第 1 页最后一行文字到下边距之间的空白(磅);没有 PyMuPDF 时返回 None"""
    try:
        import pymupdf as fz
    except ImportError:
        try:
            import fitz as fz
        except ImportError:
            return None
    pg = fz.open(path)[0]
    ys = [b[3] for b in pg.get_text('blocks') if b[4].strip()]
    if not ys: return None
    mb = re.search(r'<w:pgMar [^>]*w:bottom="(\d+)"', xml)
    bottom = int(mb.group(1)) / 20 if mb else 36
    return pg.rect.height - bottom - max(ys)


def pdf_probe(path):
    """returns (pages, text, fonts_str, author)"""
    try:
        import pymupdf as fz
    except ImportError:
        try:
            import fitz as fz
        except ImportError:
            fz = None
    if fz:
        d = fz.open(path)
        txt = ''.join(pg.get_text() for pg in d)
        fonts = ' '.join(f[3] for pg in d for f in pg.get_fonts())
        return d.page_count, txt, fonts, (d.metadata or {}).get('author', '')
    if shutil.which('pdfinfo'):
        from pdf_tools import run_text
        info = run_text(['pdfinfo', '-enc', 'UTF-8', path])
        pg = re.search(r'Pages:\s+(\d+)', info)
        if not pg:
            raise RuntimeError('pdfinfo 没有输出页数')
        au = re.search(r'Author:\s+(.*)', info)
        txt = run_text(['pdftotext', '-enc', 'UTF-8', path, '-'])
        fonts = run_text(['pdffonts', path])
        return int(pg.group(1)), txt, fonts, au.group(1).strip() if au else ''
    return None


pdf_txt = None
if pdf_path:
    try:
        r = pdf_probe(pdf_path)
    except Exception as e:  # never let the PDF probe crash the whole check
        r = None
        W('PDF 检查出错,已跳过(%s: %s)。装 PyMuPDF 最稳:python -m pip install --user pymupdf' % (type(e).__name__, e))
    if r is None:
        if not any(m.startswith('PDF 检查出错') for m in warns):
            W('没装 PyMuPDF / poppler,跳过 PDF 检查(python -m pip install --user pymupdf)')
    else:
        pages, pdf_txt, fonts, pdf_author = r
        if pages != 1: F('PDF 不是 1 页(%s 页)' % pages)
        gap = pdf_fill_gap(pdf_path) if pages == 1 else None
        if gap is not None and gap > 60:
            W('页面底部留白约 %.1f cm(约 %d 行):一页没写满,补用户真实、相关的内容(课程、技能、奖项、校园经历等)' % (gap / 28.35, gap // 14))
        if '�' in pdf_txt: F('PDF 转文本出现乱码 %d 处' % pdf_txt.count('�'))
        PT = norm(pdf_txt).lower()
        lost = [tx.strip()[:16] for tx in texts if len(norm(tx)) >= 6 and norm(tx)[:12].lower() not in PT]
        if lost: F('PDF 转文本后丢了 %d 段,例:%s' % (len(lost), ' / '.join(lost[:3])))
        if is_cn and re.search(r'YaHei|SimSun', xml) and not re.search(r'YaHei|SimSun', fonts):
            W('PDF 用替代字体生成(本机没有微软雅黑/宋体):PDF 的 1 页只对 PDF 成立,Word 版在 HR 电脑上可能重排——能投 PDF 就投 PDF')
        if pdf_author and author and pdf_author != author:
            W('PDF 作者属性是"%s",不是 %s' % (pdf_author, author))

# ---------- 8. JD 关键词覆盖 ----------
if jd:
    src_low = (norm(pdf_txt) if pdf_txt else norm(full)).lower()
    skill_txt = norm('\n'.join(tx for tx, s in zip(texts, sec_of) if '技能' in s or 'SKILL' in s.upper())).lower()
    rows, miss_must, miss_plus, only_skill = [], [], [], []
    for line in open(jd, encoding='utf-8-sig'):
        line = line.strip()
        if not line or line.startswith('#'): continue
        must = bool(re.match(r'^(必须|must)[:：]', line, re.I))
        kw = re.sub(r'^(必须|must)[:：]', '', line, flags=re.I)
        alts = [a.strip() for a in kw.split('/') if a.strip()]
        hit = [a for a in alts if norm(a).lower() in src_low]
        if not hit:
            (miss_must if must else miss_plus).append(kw)
        else:
            body_low = src_low.replace(skill_txt, '') if skill_txt else src_low
            if not any(norm(a).lower() in body_low for a in hit): only_skill.append(kw)
        rows.append((must, kw, bool(hit)))
    tot = len(rows); got = sum(r[2] for r in rows)
    mt = [r for r in rows if r[0]]; mg = sum(r[2] for r in mt)
    print('JD 关键词覆盖:%d/%d(%.0f%%);必须项 %d/%d' % (got, tot, 100 * got / max(tot, 1), mg, len(mt)))
    if miss_must: F('漏掉必须关键词:' + '、'.join(miss_must))
    if miss_plus: W('漏掉加分关键词:' + '、'.join(miss_plus))
    if only_skill: W('这些词只出现在技能栏、经历里没有证据:' + '、'.join(only_skill))

print('板块:', ' → '.join(sections))
for m_ in fails: print('❌', m_)
for m_ in warns: print('⚠️', m_)
print('结果:%s(❌ %d,⚠️ %d)' % ('不通过' if fails else '通过', len(fails), len(warns)))
sys.exit(1 if fails else 0)
