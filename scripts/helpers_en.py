"""English resume building blocks. In a build script:

    from helpers_en import *
    body = header(info_line='Available full-time from Jun 2027') + [
        section('Education'),
        entry('Example University', 'City, Country'),
        sub('Bachelor of Science, Major', 'Sep 2023 – Jun 2027'),
        bullet('**Relevant coursework:** ...'),
        ...
    ]
    finish(body)
"""
from core import *  # noqa: F401,F403
from core import P, pid, t, run, contact_runs
import re

F = '<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="SimSun" w:cs="Calibri"/>'

_GREY = F + '<w:b w:val="0"/><w:bCs w:val="0"/><w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="555555"/><w:sz w:val="19"/><w:szCs w:val="19"/>'
_LINK = F + '<w:b w:val="0"/><w:bCs w:val="0"/><w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="1F3864"/><w:sz w:val="19"/><w:szCs w:val="19"/><w:u w:val="single"/>'


def name(text=None):
    text = text or P.get('display_name_en') or P.get('name_en', '')
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="40"/><w:jc w:val="center"/></w:pPr>'
            '<w:r><w:rPr>%s<w:b/><w:bCs/><w:color w:val="1F3864"/><w:sz w:val="44"/><w:szCs w:val="44"/></w:rPr>%s</w:r></w:p>') % (pid(), F, t(text))


def contact(location=None):
    loc = P.get('location_en') if location is None else location
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="28"/><w:jc w:val="center"/></w:pPr>%s</w:p>') % (
        pid(), contact_runs(_GREY, _LINK, loc))


def centered(text, size=19):
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="30"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr>%s<w:color w:val="555555"/>'
            '<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>%s</w:r></w:p>') % (pid(), F, size, size, t(text))


def header(info_line=None, location=None):
    """Name + contact line (+ optional availability line). location defaults to profile location_en."""
    out = [name(), contact(location)]
    if info_line:
        out.append(centered(info_line))
    return out


def section(title):
    return ('<w:p w14:paraId="%s"><w:pPr><w:pBdr><w:bottom w:val="single" w:color="1F3864" w:sz="8" w:space="2"/></w:pBdr>'
            '<w:spacing w:before="120" w:after="50"/></w:pPr><w:r><w:rPr>%s<w:b/><w:bCs/><w:caps/><w:color w:val="1F3864"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr>%s</w:r></w:p>') % (pid(), F, t(title))


def entry(name, right=''):
    return ('<w:p w14:paraId="%s"><w:pPr><w:tabs><w:tab w:val="right" w:pos="10224"/></w:tabs><w:spacing w:before="50" w:after="0"/></w:pPr>'
            '<w:r><w:rPr>%s<w:b/><w:bCs/><w:color w:val="222222"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>%s</w:r>'
            '<w:r><w:rPr>%s<w:color w:val="555555"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:tab/>%s</w:r></w:p>') % (
        pid(), F, t(name), F, t(right))


def sub(left, right=''):
    r = ('<w:r><w:rPr>%s<w:i/><w:iCs/><w:color w:val="555555"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr><w:tab/>%s</w:r>' % (F, t(right))) if right else ''
    return ('<w:p w14:paraId="%s"><w:pPr><w:tabs><w:tab w:val="right" w:pos="10224"/></w:tabs><w:spacing w:after="30"/></w:pPr>'
            '<w:r><w:rPr>%s<w:i/><w:iCs/><w:color w:val="555555"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>%s</w:r>%s</w:p>') % (pid(), F, t(left), r)


def bullet(text):
    runs = []
    for i, seg in enumerate(re.split(r'\*\*', text)):
        if not seg:
            continue
        b = '<w:b/><w:bCs/>' if i % 2 else '<w:b w:val="0"/><w:bCs w:val="0"/>'
        runs.append('<w:r><w:rPr>%s%s<w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="222222"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>%s</w:r>' % (F, b, t(seg)))
    return ('<w:p w14:paraId="%s"><w:pPr><w:pStyle w:val="16"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            '<w:spacing w:after="30" w:line="250" w:lineRule="auto"/></w:pPr>%s</w:p>') % (pid(), ''.join(runs))
