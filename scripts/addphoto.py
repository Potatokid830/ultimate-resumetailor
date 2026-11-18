"""Insert an ID photo (top-right, next to the name). Usage: python addphoto.py path/to/photo.jpg
build.py calls this when you pass `photo` and profile.json has "photo" set."""
import os
import re
import shutil
import sys

photo = sys.argv[1]
ext = os.path.splitext(photo)[1].lower().lstrip('.') or 'jpg'
ext = 'jpeg' if ext == 'jpg' else ext
ctype = {'jpeg': 'image/jpeg', 'png': 'image/png'}[ext]
base = 'un/'
os.makedirs(base + 'word/media', exist_ok=True)
target = 'photo1.' + ext
shutil.copy(photo, base + 'word/media/' + target)

ct = open(base + '[Content_Types].xml', encoding='utf-8').read()
if 'Extension="%s"' % ext not in ct:
    ct = ct.replace('<Default Extension="xml"', '<Default Extension="%s" ContentType="%s"/><Default Extension="xml"' % (ext, ctype), 1)
    assert 'Extension="%s"' % ext in ct
open(base + '[Content_Types].xml', 'w', encoding='utf-8').write(ct)

rp = base + 'word/_rels/document.xml.rels'
r = open(rp, encoding='utf-8').read()
if 'rIdPhoto1' not in r:
    r = r.replace('</Relationships>', '<Relationship Id="rIdPhoto1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s"/></Relationships>' % target)
open(rp, 'w', encoding='utf-8').write(r)

cx, cy = 666000, 888000  # ~1.85 cm x 2.47 cm (3:4)
drw = ('<w:r><w:drawing><wp:anchor distT="0" distB="0" distL="114300" distR="0" simplePos="0" relativeHeight="251659264" behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
       '<wp:simplePos x="0" y="0"/><wp:positionH relativeFrom="margin"><wp:align>right</wp:align></wp:positionH>'
       '<wp:positionV relativeFrom="paragraph"><wp:posOffset>0</wp:posOffset></wp:positionV>'
       f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapSquare wrapText="left"/>'
       '<wp:docPr id="901" name="Photo"/><wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
       '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
       f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{target}"/><pic:cNvPicPr/></pic:nvPicPr>'
       '<pic:blipFill><a:blip r:embed="rIdPhoto1"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
       f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
       '</a:graphicData></a:graphic></wp:anchor></w:drawing></w:r>')
p = base + 'word/document.xml'
d = open(p, encoding='utf-8').read()
i = d.index('<w:body>')
m = re.compile(r'<w:p[ >].*?</w:pPr>', re.S).search(d, i)
d = d[:m.end()] + drw + d[m.end():]
for ns in ('wp', 'r'):
    assert f'xmlns:{ns}=' in d[:3000], ns
open(p, 'w', encoding='utf-8').write(d)
print('photo added')
