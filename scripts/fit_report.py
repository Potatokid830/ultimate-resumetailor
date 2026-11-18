#!/usr/bin/env python3
"""一页压不下或底部留白时,告诉你差几行、删哪里最省事。

    python fit_report.py 简历.pdf [--docx 简历.docx] [--auto]

输出:
- 溢出:第 2 页及以后有几行
- 留白:第 1 页最后一行到下边距之间大约还能放几行
- 短尾行:每条要点的最后一行如果很短(中文 ≤ 12 个字,英文 ≤ 25 个字符),删掉这几个字这条就少一行
--docx  从 docx 读下边距(不给就按模版的 640 twips = 32 磅)
--auto  只在溢出或留白超过约 2 cm 时才输出(build.py 用)
需要 PyMuPDF(python -m pip install --user pymupdf);没有就提示一行后退出,返回码 0。
"""
import os
import re
import statistics
import sys
import zipfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

GAP_WARN = 60  # 磅,和 ats_check.py 的留白阈值一致
BULLET = '•'


def _fz():
    try:
        import pymupdf as fz
    except ImportError:
        try:
            import fitz as fz
        except ImportError:
            return None
    return fz


def bottom_margin(docx):
    if docx and os.path.isfile(docx):
        xml = zipfile.ZipFile(docx).read('word/document.xml').decode('utf-8', 'ignore')
        m = re.search(r'<w:pgMar [^>]*w:bottom="(\d+)"', xml)
        if m:
            return int(m.group(1)) / 20
    return 32.0


def rows_of(page):
    """把同一行(y 接近)的文字片段合成一行,按从上到下排序。"""
    lines = []
    for b in page.get_text('dict')['blocks']:
        for ln in b.get('lines', []):
            t = ''.join(s['text'] for s in ln['spans'])
            if t.strip():
                lines.append((ln['bbox'][1], ln['bbox'][0], ln['bbox'][3], t))
    lines.sort()
    rows = []
    for y0, x0, y1, t in lines:
        if rows and abs(rows[-1]['y0'] - y0) < 3:
            r = rows[-1]
            r['parts'].append((x0, t)); r['y1'] = max(r['y1'], y1); r['x0'] = min(r['x0'], x0)
        else:
            rows.append({'y0': y0, 'y1': y1, 'x0': x0, 'parts': [(x0, t)]})
    for r in rows:
        r['text'] = ' '.join(t.strip() for _, t in sorted(r['parts']))
    return rows


def short_tails(all_rows):
    out, cur = [], None

    def close():
        if cur and len(cur) >= 2:
            last = cur[-1]['text'].strip()
            cjk = bool(re.search(r'[一-鿿]', ''.join(r['text'] for r in cur)))
            n = len(re.sub(r'\s', '', last)) if cjk else len(last)
            if n <= (12 if cjk else 25):
                head = re.sub(r'^\s*' + BULLET + r'\s*', '', cur[0]['text'])[:15]
                out.append((head, last, n, 'cn' if cjk else 'en'))

    for r in all_rows:
        t = r['text'].lstrip()
        if t.startswith(BULLET):
            close()
            cur = [r]
            cur_x = r['x0']
        elif cur is not None and r['x0'] > cur_x + 4:
            cur.append(r)  # 续行:比项目符号更靠右
        else:
            close()
            cur = None  # 板块标题、公司行等,要点结束
    close()
    return out


def main():
    args = sys.argv[1:]
    auto = '--auto' in args
    if auto:
        args.remove('--auto')
    docx = None
    if '--docx' in args:
        i = args.index('--docx'); docx = args[i + 1]; del args[i:i + 2]
    if not args:
        print(__doc__); return
    fz = _fz()
    if not fz:
        print('fit_report:没装 PyMuPDF,无法分析排版(python -m pip install --user pymupdf)')
        return
    d = fz.open(args[0])
    pages = [rows_of(p) for p in d]
    overflow = sum(len(p) for p in pages[1:])
    p1 = pages[0]
    gap = d[0].rect.height - bottom_margin(docx) - max(r['y1'] for r in p1) if p1 else 0
    steps = [b['y0'] - a['y0'] for a, b in zip(p1, p1[1:]) if 8 < b['y0'] - a['y0'] < 25]
    lh = statistics.median(steps) if steps else 14.0
    if auto and not overflow and gap <= GAP_WARN:
        return
    tails = short_tails([r for p in pages for r in p])

    print('—— 一页排版报告(fit_report)——')
    if overflow:
        print('溢出:第 2 页及以后共 %d 行,要删掉约 %d 行' % (overflow, overflow))
    else:
        print('页数:1 页,没有溢出')
    if not overflow:
        print('留白:底部约 %.1f cm,大约还能放 %d 行%s' % (gap / 28.35, max(int(gap // lh), 0),
              '(要补真实内容,见 SKILL.md 第 3 节)' if gap > GAP_WARN else ''))
    if tails:
        print('短尾行(删掉最后这几个字,这条就少一行;按字数从少到多):')
        for head, last, n, lang in sorted(tails, key=lambda x: x[2]):
            unit = '字' if lang == 'cn' else '字符'
            print('  - 「%s…」最后一行:「%s」(%d %s)' % (head, last, n, unit))
    elif overflow:
        print('没有短尾行:只能整条删,或合并两条要点。')


if __name__ == '__main__':
    main()
