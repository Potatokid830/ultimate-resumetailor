#!/bin/bash
# 出一份简历(docx + pdf + 预览图 + 机筛自检)。在你的工作目录里跑:
#
#   bash <skill>/scripts/build.sh my_build.py 输出文件名 cn photo      # 中文版,带照片(profile.json 里要有 "photo")
#   bash <skill>/scripts/build.sh my_build.py Output_Name en            # 英文版,不带照片
#   PHONE="+65 8000 0000" bash <skill>/scripts/build.sh ...            # 临时换一个电话
#   JD=jd_keywords.txt bash <skill>/scripts/build.sh ...               # 顺便跑 JD 关键词覆盖
#
# 个人信息来自 profile.json(找不到就用虚构的 profile.example.json 并提示)。
# PDF 文件名默认用 profile 的 pdf_name_cn / pdf_name_en(投递时 PDF 只带人名),Word 保留你给的输出文件名。
set -e
B=$1; OUT=$2; LANG_=${3:-cn}; PHOTO=${4:-nophoto}
if [ -z "$B" ] || [ -z "$OUT" ]; then sed -n '2,12p' "$0"; exit 1; fi
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SKILL_DIR
export PYTHONPATH="$SKILL_DIR/scripts${PYTHONPATH:+:$PYTHONPATH}"
TPL="$SKILL_DIR/assets/template_$LANG_.docx"
[ -f "$TPL" ] || { echo "no template: $TPL"; exit 1; }

rm -rf un && mkdir un && (cd un && unzip -q "$TPL")
python3 "$B" >/dev/null
python3 "$SKILL_DIR/scripts/ats_fix.py" >/dev/null

if [ "$PHOTO" = "photo" ]; then
  PH=$(python3 -c "
import core, os
p = core.P.get('photo') or ''
if p and not os.path.isabs(p): p = os.path.join(os.path.dirname(os.path.abspath(core.PROFILE_PATH)), p)
print(p if p and os.path.isfile(p) else '')")
  if [ -n "$PH" ]; then python3 "$SKILL_DIR/scripts/addphoto.py" "$PH" >/dev/null; else echo "⚠️ profile 里没有可用的 photo,跳过照片"; fi
fi

PDF=$(python3 -c "
import core
print(core.P.get('pdf_name_$LANG_') or '$OUT')" 2>/dev/null)
rm -f "$OUT.docx" && (cd un && zip -qr -X "../$OUT.docx" '[Content_Types].xml' _rels docProps word)
rm -rf un
python3 "$SKILL_DIR/scripts/pdf_tools.py" convert "$OUT.docx" "$PDF.pdf" || { echo "⚠️ 没能转 PDF(装 LibreOffice 或 Microsoft Word)"; exit 0; }
echo "$OUT.docx -> $PDF.pdf  pages: $(python3 "$SKILL_DIR/scripts/pdf_tools.py" pages "$PDF.pdf")   # 必须是 1"
python3 "$SKILL_DIR/scripts/pdf_tools.py" png "$PDF.pdf" "preview_$PDF"       # 看图:底部不能留白,也不能溢出
python3 "$SKILL_DIR/scripts/ats_check.py" "$OUT.docx" "$PDF.pdf" ${JD:+--jd "$JD"} || echo "⚠️ 机筛自检没通过,按上面的 ❌ 逐条改完再交付"
