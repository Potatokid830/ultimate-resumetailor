"""Shared plumbing for helpers_cn.py / helpers_en.py.

- Loads the unzipped template from ./un/ (build.sh unzips it there).
- Loads the user's profile (name, contact, optional photo) from JSON.
- Provides finish(body) which writes document.xml and clean docProps.

Profile lookup order:
  1. $RESUME_PROFILE
  2. ./profile.json            (your working directory)
  3. <skill dir>/profile.json
  4. <skill dir>/profile.example.json   (fictional demo person; prints a warning)
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timezone

SKILL_DIR = os.environ.get('SKILL_DIR') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_profile():
    cands = [os.environ.get('RESUME_PROFILE'), 'profile.json',
             os.path.join(SKILL_DIR, 'profile.json')]
    for c in cands:
        if c and os.path.isfile(c):
            return c
    ex = os.path.join(SKILL_DIR, 'profile.example.json')
    sys.stderr.write('[resume-tailor] profile.json not found, using the fictional profile.example.json\n')
    return ex


PROFILE_PATH = _find_profile()
P = json.load(open(PROFILE_PATH, encoding='utf-8'))
# phone override, e.g. PHONE="+65 8000 0000" bash scripts/build.sh ...
if os.environ.get('PHONE'):
    P['phone'] = os.environ['PHONE']

DOC = 'un/word/document.xml'
src = open(DOC, encoding='utf-8').read()
paras = re.findall(r'<w:p[ >].*?</w:p>', src, re.S)
head = src[:src.find('<w:body>') + len('<w:body>')]
sect = src[src.find('<w:sectPr'):]

_id = [0x50000000]


def pid():
    _id[0] += 7
    return '%08X' % _id[0]


def esc(s):
    return html.escape(s, quote=False)


def t(s):
    return '<w:t xml:space="preserve">%s</w:t>' % esc(s)


def run(rpr, text):
    return '<w:r><w:rPr>%s</w:rPr>%s</w:r>' % (rpr, t(text))


def link(rpr_link, url, text):
    """Field-code hyperlink (same structure Word/WPS use; ATS parsers read the visible text)."""
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> HYPERLINK &quot;%s&quot; </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:rPr>%s</w:rPr>%s</w:r>'
            '<w:r><w:rPr>%s</w:rPr><w:fldChar w:fldCharType="end"/></w:r>') % (esc(url), rpr_link, t(text), rpr_link)


def _url(s):
    return s if re.match(r'https?://', s) else 'https://' + s


def _display(s):
    return re.sub(r'^https?://(www\.)?', '', s).rstrip('/')


def contact_runs(rpr, rpr_link, location=None, sep='  |  '):
    """location | phone | email | linkedin | website — empty fields are skipped.
    LinkedIn and website are shown as full addresses so ATS can read them."""
    parts = []
    if location:
        parts.append(run(rpr, location))
    if P.get('phone'):
        parts.append(run(rpr, P['phone']))
    if P.get('email'):
        parts.append(link(rpr_link, 'mailto:' + P['email'], P['email']))
    for key in ('linkedin', 'website'):
        if P.get(key):
            parts.append(link(rpr_link, _url(P[key]), _display(P[key])))
    return run(rpr, sep).join(parts)


def finish(body, ts=None):
    """Write document.xml and set docProps author / modified time from the profile."""
    open(DOC, 'w', encoding='utf-8').write(head + ''.join(body) + sect)
    author = P.get('author') or P.get('name_en') or P.get('name_cn') or ''
    ts = ts or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    cp = 'un/docProps/core.xml'
    core = open(cp, encoding='utf-8').read()
    core = re.sub(r'<dc:creator>.*?</dc:creator>|<dc:creator/>', '<dc:creator>%s</dc:creator>' % esc(author), core)
    core = re.sub(r'<cp:lastModifiedBy>.*?</cp:lastModifiedBy>|<cp:lastModifiedBy/>', '<cp:lastModifiedBy>%s</cp:lastModifiedBy>' % esc(author), core)
    core = re.sub(r'<dcterms:modified[^>]*>.*?</dcterms:modified>',
                  '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>' % ts, core)
    open(cp, 'w', encoding='utf-8').write(core)
    print('ok')
