import re
p = r"_work\build_cleaning_report.py"
s = open(p, encoding="utf-8").read()

s = s.replace(
    "def numbered(text, bold_head=None):\n    p = doc.add_paragraph(style=\"List Number\")",
    "def numbered(num, text, bold_head=None):\n    p = doc.add_paragraph()\n"
    "    p.paragraph_format.left_indent = Inches(0.25)\n"
    "    p.paragraph_format.first_line_indent = Inches(-0.25)\n"
    "    p.add_run(\"%d. \" % num)")

i = s.index('doc.add_heading("7. Remaining')
def addnums(seg, start=1):
    n = [start]
    def rep(m):
        v = n[0]; n[0] += 1
        return 'numbered(%d, "' % v
    return re.sub(r'numbered\("', rep, seg)
part1 = addnums(s[:i]); part2 = addnums(s[i:])
s = part1 + part2

reps = [
    ('numbered(1, "checked the 45 extracted files', 'numbered(1, "Checked the 45 extracted files'),
    ('"Extraction and inventory. We "', '"Extraction and inventory. "'),
    ('numbered(2, "for every sensor file', 'numbered(2, "For every sensor file'),
    ('numbered(3, "two candidate methods', 'numbered(3, "Two candidate methods'),
    ('numbered(4, "each annotated fall', 'numbered(4, "Each annotated fall'),
    ('numbered(5, "for each of the 100', 'numbered(5, "For each of the 100'),
    ('numbered(6, "every row of the fixed-width', 'numbered(6, "Every row of the fixed-width'),
    ('numbered(7, "frames per subject', 'numbered(7, "Frames per subject'),
    ('bullet("the same-named accelerometer', 'bullet("The same-named accelerometer'),
    ('bullet("fixed 625-sample clips (10.00 s)', 'bullet("Fixed 625-sample clips (10.00 s)'),
    ('bullet("keep each sensor at its measured native rate', 'bullet("Keep each sensor at its measured native rate'),
    ('bullet("a clip is positive if any index position', 'bullet("A clip is positive if any index position'),
    ('bullet("raw files stay untouched', 'bullet("Raw files stay untouched'),
    ('numbered(1, "convert each variable-length', 'numbered(1, "Convert each variable-length'),
    ('numbered(2, "slice all four modalities', 'numbered(2, "Slice all four modalities'),
    ('numbered(3, "compute scaling statistics', 'numbered(3, "Compute scaling statistics'),
    ('numbered(4, "leave-one-subject-out, 10 folds', 'numbered(4, "Leave-one-subject-out, 10 folds'),
    ('numbered(5, "save processed arrays', 'numbered(5, "Save processed arrays'),
]
for a, b in reps:
    if a not in s:
        print("MISSING:", a[:60])
    s = s.replace(a, b)

border = ('from docx.oxml.ns import qn\n'
          'title_style = doc.styles["Title"]\n'
          '_pPr = title_style.element.get_or_add_pPr()\n'
          'for _bdr in _pPr.findall(qn("w:pBdr")):\n'
          '    _pPr.remove(_bdr)\n\n')
s = s.replace('doc.core_properties.title =', border + 'doc.core_properties.title =')
open(p, "w", encoding="utf-8").write(s)
print("patched")
