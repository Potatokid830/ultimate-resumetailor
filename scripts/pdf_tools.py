#!/usr/bin/env python3
"""docx → pdf, page count, PNG preview — with whatever is installed. Works on Windows, macOS and Linux.

    python pdf_tools.py convert in.docx out.pdf   # see order below
    python pdf_tools.py pages file.pdf            # prints the page count
    python pdf_tools.py png file.pdf out_prefix   # renders page 1 to out_prefix.png for a visual check

Converter order:
  Windows: Microsoft Word (via PowerShell COM) → WPS (KWps COM) → LibreOffice
  macOS / Linux: LibreOffice (soffice) → Microsoft Word for Mac (osascript)

Note for Word for Mac: it is sandboxed and may ask once for permission to open the folder;
if it can't, work inside ~/Documents or ~/Desktop.
"""
import os
import re
import shutil
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8')
    except Exception:
        pass

WIN = sys.platform.startswith('win')

# PowerShell: open the docx read-only in Word / WPS and export PDF (17 = wdExportFormatPDF).
# Paths go in through environment variables so quotes and Chinese characters are safe.
_PS = r'''
$ErrorActionPreference = "Stop"
$app = $null
try {
  $app = New-Object -ComObject $env:RT_PROGID
  try { $app.Visible = $false } catch {}
  try { $app.DisplayAlerts = 0 } catch {}
  $d = $app.Documents.Open($env:RT_SRC, $false, $true)
  $d.ExportAsFixedFormat($env:RT_OUT, 17)
  $d.Close(0)
} finally {
  # Quit only if no other documents are open (WPS may attach to the user's running window)
  if ($app) { try { if ($app.Documents.Count -eq 0) { $app.Quit() } } catch {} }
}
'''


def _soffice():
    s = shutil.which('soffice') or shutil.which('libreoffice')
    cands = ['/Applications/LibreOffice.app/Contents/MacOS/soffice']
    if WIN:
        for base in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
            if base:
                cands.append(os.path.join(base, 'LibreOffice', 'program', 'soffice.exe'))
    for c in cands:
        if not s and os.path.exists(c):
            s = c
    return s


def _via_soffice(src, out):
    soffice = _soffice()
    if not soffice:
        return False
    outdir = os.path.dirname(out)
    try:
        subprocess.run([soffice, '--headless', '--convert-to', 'pdf', '--outdir', outdir, src],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    except subprocess.TimeoutExpired:
        return False
    made = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + '.pdf')
    if made != out and os.path.exists(made):
        shutil.move(made, out)
    return os.path.exists(out)


def _via_windows_com(src, out, progid):
    ps = shutil.which('powershell') or shutil.which('pwsh')
    if not ps:
        return False
    env = dict(os.environ, RT_SRC=src, RT_OUT=out, RT_PROGID=progid)
    try:
        subprocess.run([ps, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-Command', _PS],
                       env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    except subprocess.TimeoutExpired:
        sys.stderr.write('%s did not finish exporting. Check for an open dialog in Word / WPS, '
                         'or open the .docx and Save As PDF by hand.\n' % progid)
    return os.path.exists(out)


def _via_mac_word(src, out):
    if not os.path.exists('/Applications/Microsoft Word.app'):
        return False
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


def convert(src, out):
    src, out = os.path.abspath(src), os.path.abspath(out)
    if os.path.exists(out):
        os.remove(out)
    if WIN:
        steps = [lambda: _via_windows_com(src, out, 'Word.Application'),
                 lambda: _via_windows_com(src, out, 'KWps.Application'),
                 lambda: _via_soffice(src, out)]
    else:
        steps = [lambda: _via_soffice(src, out)]
        if sys.platform == 'darwin':
            steps.append(lambda: _via_mac_word(src, out))
    for step in steps:
        if step():
            return True
    sys.stderr.write('No PDF converter worked: install LibreOffice or Microsoft Word '
                     '(on Windows WPS may also work), or open the .docx and Save As PDF by hand.\n')
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
