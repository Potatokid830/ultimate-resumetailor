"""中文简历积木。build 脚本里:

    from helpers_cn import *
    body = header(info_line='现居上海  |  可到岗:2027.06 起全职') + [
        section('教育背景'),
        entry('某某大学  Example University', '城市'),
        sub('学士 · 专业', '2023.09 – 2027.06'),
        bullet('**相关课程:**……'),
        ...
    ]
    finish(body)

bullet() 里用 **粗体**;但机筛自检不鼓励"粗体标签 + 冒号"写在经历要点里(技能栏可以)。
"""
from core import *  # noqa: F401,F403  (P, paras, head, sect, t, run, link, finish ...)
from core import P, pid, t, run, contact_runs
import re

TNR = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="SimSun"/>'
YH = '<w:rFonts w:ascii="Microsoft YaHei" w:hAnsi="Microsoft YaHei" w:eastAsia="Microsoft YaHei"/>'

_GREY = TNR + '<w:b w:val="0"/><w:bCs w:val="0"/><w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="555555"/><w:sz w:val="18"/><w:szCs w:val="18"/>'
_LINK = TNR + '<w:b w:val="0"/><w:bCs w:val="0"/><w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="1F3864"/><w:sz w:val="18"/><w:szCs w:val="18"/><w:u w:val="single"/>'


def name(text=None):
    text = text or P.get('display_name_cn') or P.get('name_cn', '')
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="40"/><w:jc w:val="center"/></w:pPr>'
            '<w:r><w:rPr>%s<w:b/><w:bCs/><w:color w:val="1F3864"/><w:sz w:val="44"/><w:szCs w:val="44"/></w:rPr>%s</w:r></w:p>') % (pid(), YH, t(text))


def contact(location=None):
    loc = P.get('location_cn') if location is None else location
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="28"/><w:jc w:val="center"/></w:pPr>%s</w:p>') % (
        pid(), contact_runs(_GREY, _LINK, loc))


def info(text):
    """联系方式下面那一行,例:'籍贯:广东  |  可到岗:2027.06 起全职(每周 5 天)'"""
    return ('<w:p w14:paraId="%s"><w:pPr><w:spacing w:after="38"/><w:jc w:val="center"/></w:pPr>%s</w:p>') % (pid(), run(_GREY, text))


def header(info_line=None, location=None):
    """姓名 + 联系方式 (+ 可选的到岗/籍贯行)。location 默认读 profile 的 location_cn。"""
    out = [name(), contact(location)]
    if info_line:
        out.append(info(info_line))
    return out


def section(title):
    return ('<w:p w14:paraId="%s"><w:pPr><w:pBdr><w:bottom w:val="single" w:color="1F3864" w:sz="8" w:space="2"/></w:pBdr>'
            '<w:spacing w:before="140" w:after="60"/></w:pPr><w:r><w:rPr>%s<w:b/><w:bCs/><w:color w:val="1F3864"/>'
            '<w:sz w:val="23"/><w:szCs w:val="23"/></w:rPr>%s</w:r></w:p>') % (pid(), YH, t(title))


def entry(name, right=''):
    """单位/学校一行:左边粗体名称,右边斜体地点或时间。"""
    return ('<w:p w14:paraId="%s"><w:pPr><w:tabs><w:tab w:val="right" w:pos="10224"/></w:tabs><w:spacing w:before="60" w:after="10"/></w:pPr>'
            '<w:r><w:rPr>%s<w:b/><w:bCs/><w:color w:val="222222"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>%s</w:r>'
            '<w:r><w:rPr>%s<w:i/><w:iCs/><w:color w:val="555555"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr><w:tab/>%s</w:r></w:p>') % (
        pid(), YH, t(name), TNR, t(right))


def sub(left, right=''):
    """岗位/学位一行:左边斜体,右边(可选)时间,右对齐。"""
    r = ('<w:r><w:rPr>%s<w:i/><w:iCs/><w:color w:val="555555"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr><w:tab/>%s</w:r>' % (TNR, t(right))) if right else ''
    return ('<w:p w14:paraId="%s"><w:pPr><w:tabs><w:tab w:val="right" w:pos="10224"/></w:tabs><w:spacing w:after="34"/></w:pPr>'
            '<w:r><w:rPr>%s<w:i/><w:iCs/><w:color w:val="555555"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr>%s</w:r>%s</w:p>') % (pid(), TNR, t(left), r)


def bullet(text):
    """要点。支持 **粗体** 片段。"""
    runs = []
    for i, seg in enumerate(re.split(r'\*\*', text)):
        if not seg:
            continue
        b = '<w:b/><w:bCs/>' if i % 2 else '<w:b w:val="0"/><w:bCs w:val="0"/>'
        runs.append('<w:r><w:rPr>%s%s<w:i w:val="0"/><w:iCs w:val="0"/><w:color w:val="222222"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>%s</w:r>' % (TNR, b, t(seg)))
    return ('<w:p w14:paraId="%s"><w:pPr><w:pStyle w:val="16"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            '<w:spacing w:after="34" w:line="256" w:lineRule="auto"/></w:pPr>%s</w:p>') % (pid(), ''.join(runs))
