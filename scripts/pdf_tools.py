#!/usr/bin/env python3
"""docx → pdf, page count, PNG preview — with whatever is installed.

    python3 pdf_tools.py convert in.docx out.pdf   # LibreOffice (soffice) first; on macOS falls back to Microsoft Word
    python3 pdf_tools.py pages file.pdf            # prints the page count
    python3 pdf_tools.py png file.pdf out_prefix   # renders page 1 to out_prefix.png for a visual check

Note for the Word fallback: Word for Mac is sandboxed and may ask once for permission to
open the folder; if it can't, work inside ~/Documents or ~/Desktop.
"""
import os
import re
import shutil
import subprocess
import sys


def convert(src, out):
    src, out = os.path.abspath(src), os.path.abspath(out)
    soffice = shutil.which('soffice') or shutil.which('libreoffice')
    mac_lo = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    if not soffice and os.path.exists(mac_lo):
        soffice = mac_lo
    if soffice:
        outdir = os.path.dirname(out)
        subprocess.run([soffice, '--headless', '--convert-to', 'pdf', '--outdir', outdir, src],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        made = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + '.pdf')
        if made != out and os.path.exists(made):
            shutil.move(made, out)
        return os.path.exists(out)
    if sys.platform == 'darwin' and os.path.exists('/Applications/Microsoft Word.app'):
        if os.path.exists(out):
            os.remove(out)
        script = '''
tell application "Microsoft Word"
  set d to open file name "%s"
  delay 1
  save as d file name "%s" file format format PDF
  close d saving no
end tell''' % (src.replace('"', '\\"'), out.replace('"', '\\"'))
        try:
            subprocess.run(['osascript', '-e', script], stdout=subprocess.DEVNULL, timeout=180)
        except subprocess.TimeoutExpired:
            pass
        if not os.path.exists(out):
            sys.stderr.write('Word did not export the PDF. Switch to Word and check for an open dialog '
                             '(file-access permission, repair prompt), or open the .docx and Save As PDF by hand.\n')
        return os.path.exists(out)
    sys.stderr.write('No PDF converter found: install LibreOffice (soffice) or Microsoft Word.\n')
    return False


def _fz():
    try:
        import pymupdf as fz
    except ImportError:
        try:
            import fitz as fz
        except ImportError:
            return None
    return fz


def pages(pdf):
    fz = _fz()
    if fz:
        return fz.open(pdf).page_count
    if shutil.which('pdfinfo'):
        o = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        m = re.search(r'Pages:\s+(\d+)', o)
        return int(m.group(1)) if m else 0
    return -1


def png(pdf, prefix):
    fz = _fz()
    if fz:
        fz.open(pdf)[0].get_pixmap(dpi=70).save(prefix + '.png')
    elif shutil.which('pdftoppm'):
        subprocess.run(['pdftoppm', '-r', '70', '-png', '-f', '1', '-l', '1', '-singlefile', pdf, prefix])


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'convert':
        sys.exit(0 if convert(sys.argv[2], sys.argv[3]) else 1)
    elif cmd == 'pages':
        print(pages(sys.argv[2]))
    elif cmd == 'png':
        png(sys.argv[2], sys.argv[3])
