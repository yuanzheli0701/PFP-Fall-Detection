# -*- coding: utf-8 -*-
"""Build the English data cleaning report DOCX for the QUIDA project."""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\reports\Data_Cleaning_Report_QUIDA_EN.docx"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = Document()
base = doc.styles["Normal"]
base.font.name = "Calibri"
base.font.size = Pt(10.5)

def para(text, style=None, size=None, bold=False, italic=False, align=None):
    p = doc.add_paragraph(style=style)
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    if align:
        p.alignment = align
    return p

def bullet(text, bold_head=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_head:
        r = p.add_run(bold_head)
        r.bold = True
    p.add_run(text)
    return p

def numbered(num, text, bold_head=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.add_run("%d. " % num)
    if bold_head:
        r = p.add_run(bold_head)
        r.bold = True
    p.add_run(text)
    return p

def add_table(data, widths=None, font_size=9.5):
    t = doc.add_table(rows=len(data), cols=len(data[0]))
    t.style = "Table Grid"
    t.autofit = False
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(font_size)
            if i == 0:
                run.bold = True
    if widths:
        for j, w in enumerate(widths):
            for i in range(len(data)):
                t.cell(i, j).width = Inches(w)
    doc.add_paragraph()
    return t

# ---------------- title block ----------------
tp = doc.add_paragraph(style="Title")
tr = tp.add_run("Data Cleaning Report for the QUIDA Fall Detection Dataset")
tr.font.color.rgb = RGBColor(0, 0, 0)
para("PFP project - comparison of CNN, LSTM and metric-learning classifiers for fall detection", size=11)
para("Prepared by: Clemence Vergniaud, Yuanzhe Li")
para("Date: 13 October 2026")
para("Status: raw-data verification complete; the cleaning pipeline that produces model-ready arrays is specified in Section 7 and not yet implemented.")

# ---------------- 1 ----------------
doc.add_heading("1. Purpose and Current Status", level=1)
para("This report documents what we have done to the raw QUIDA recordings so far, what the measurements showed, and what remains before the data can feed the CNN, LSTM and metric-learning experiments. Every number below was measured directly from the files with scripts/verifier_donnees_quida.py and scripts/explorer_donnees.py; nothing is copied from the dataset documentation.")
para("Bottom line. The verification pass is complete, the deep cleaning pipeline is not. The raw recordings contain 130 ten-second clips: 99 clips contain a fall and 31 do not, a ratio of 3.2 fall clips per no-fall clip. Three findings correct earlier documentation:")
bullet("The correct fall / no-fall balance is 99 / 31. The 97 / 32 figure in the current README draft comes from a segmentation method that fails on subject_8 (Section 5.1).", "Class balance. ")
bullet("LiDAR runs at 10.0 Hz, not at the 8.3 Hz stated in the dataset presentation.", "LiDAR rate. ")
bullet("subject_8 stores three fall clips out of order, and one fall record of subject_3 (fall 2) cannot be reconciled between the annotation file and the index files. Both cases are documented in Section 5 and must be handled before training; they are the only such cases in the dataset.", "Two quality issues. ")
para("All operations so far are read-only: no file in data_raw/ has been modified, moved or deleted. What is still missing is listed in Section 7: radar feature extraction, window construction on a common time base, normalization statistics, leave-one-subject-out splits and the saved processed artifacts.")

# ---------------- 2 ----------------
doc.add_heading("2. Raw Data as Received", level=1)
para("The dataset arrives as yjgdv-osfstorage-archive.zip (115 MB), which contains dataset.zip; its contents were extracted to data_raw/ (388 MB). The extraction contains 45 CSV files: 10 subjects (subject_1 to subject_10), each with the same four modality files, plus five top-level annotation matrices.")
bullet("falls.csv holds the 10 annotated fall times per subject as Unix timestamps (10 x 10 matrix).")
bullet("The same-named accelerometer, radar, lidar and ir_camera matrices hold, for every (fall, subject) pair, the row position of that fall inside the subject file of that sensor. In other words: falls.csv gives when, the index matrices give where.")
para("Accelerometer files contain only the 13 clipped 10-second trials per subject (130 s of signal in total), separated by 10 to 90 second gaps. Radar, LiDAR and IR run quasi-continuously through the session (about 440 to 460 s per subject), so their 10-second fall clips have to be cut by time using the index matrices. Per-subject file sizes: 0.3-0.4 MB accelerometer, 12.6-22.3 MB radar, 6.3-10.8 MB LiDAR, 14.3-25.3 MB IR camera.")
para("Table 1. File inventory and row structure (measured totals over the 10 subjects).")
add_table([
    ["Modality", "File per subject", "Total rows", "Row structure"],
    ["Accelerometer", "accelerometer.csv", "81,250", "timestamp + 3 axes"],
    ["Radar", "radar.csv", "36,838 frames", "timestamp + 7 values per detected target; 0 to 186 targets"],
    ["LiDAR", "LIDAR.csv", "44,226", "timestamp + 512 values (8 x 8 panel per frame)"],
    ["IR camera", "ir_camera.csv", "11,877", "timestamp + 768 values (32 x 24 thermopile frame)"],
], widths=[1.15, 1.35, 1.1, 2.9])

# ---------------- 3 ----------------
doc.add_heading("3. Operations Performed on the Raw Data", level=1)
para("The workflow so far is a verification pass; it produces no new data files. It is implemented in two scripts: scripts/explorer_donnees.py (initial exploration) and scripts/verifier_donnees_quida.py (verification pass; regenerates every number in this report).")
numbered(1, "We checked the 45 extracted files: all 10 subjects present, four modality files each, five annotation matrices at the top level, timestamps monotonic except where noted in Section 5.", "Extraction and inventory. ")
numbered(2, "For every sensor file we computed 1 / median(dt) from the timestamp column, per subject. No rate was taken from the documentation.", "Sampling-rate measurement. ")
numbered(3, "Two candidate methods were tested on the accelerometer channel. Method A, time-gap splitting: start a new segment whenever the gap between consecutive timestamps exceeds 10 times the median gap. Method B, fixed 625-sample blocks: 625 samples equal exactly 10.00 s at 62.5 Hz, matching the recording procedure (one fall trial = one 10-second clip). Method B was adopted after Method A failed on subject_8 (Section 5.1).", "Clip segmentation. ")
numbered(4, "Each annotated fall was assigned to a clip through its index position: clip = position divided by 625 (integer part). A clip containing at least one fall index is labelled fall; every other clip is labelled no-fall.", "Fall labelling. ")
numbered(5, "For each of the 100 fall events and each modality we compared the timestamp at the index position with the annotated time in falls.csv (offset = timestamp at index minus annotated time) and looked for outliers.", "Synchronization audit. ")
numbered(6, "Every row of the fixed-width files (accelerometer, LiDAR, IR camera) was scanned for missing values (NaN) and infinities. Radar rows are variable length and were checked structurally instead (frame count, target count, empty frames).", "Integrity scan. ")
numbered(7, "Frames per subject, empty frames (no target detected) and maximum target count were counted, because the radar is the least regular modality and its format drives later feature extraction.", "Radar structure survey. ")

# ---------------- 4 ----------------
doc.add_heading("4. Results", level=1)
para("Table 2. Sampling rates: documentation values versus measured values (mean over 10 subjects).")
add_table([
    ["Modality", "Documentation", "Measured", "Range", "Note"],
    ["Accelerometer", "not given", "62.50 Hz", "62.50 - 62.50", "13 clips of 625 samples per subject"],
    ["Radar", "8.3 Hz", "8.33 Hz", "8.31 - 8.33", "variable row length, 7 values per target"],
    ["LiDAR", "8.3 Hz (dataset presentation)", "10.00 Hz", "10.00 - 10.00", "512 values per frame; documentation value is wrong"],
    ["IR camera", "2.6 Hz", "2.60 Hz", "2.59 - 2.61", "768 values per frame"],
], widths=[1.05, 1.75, 0.85, 0.95, 1.9])
para("Table 3. Segmentation methods compared on the accelerometer channel.")
add_table([
    ["Method", "Clips found", "Fall clips", "No-fall clips", "Outcome"],
    ["A. Time-gap splitting", "129 (subject_8 gives 12)", "97", "32", "Rejected: merges two of subject_8's clips"],
    ["B. Fixed 625-sample blocks", "130 (13 per subject)", "99", "31", "Adopted: every clip intact"],
], widths=[1.5, 1.35, 0.85, 0.95, 1.85])
para("The 100 fall events map to 99 distinct fall clips because two falls (subject_3, falls 1 and 2 per the index matrix) fall inside one clip. Only Method B keeps all 13 clips per subject; that is why the correct class balance is 99 / 31 and not the 97 / 32 currently written in the README.")
para("Table 4. Clips per subject under Method B (13 clips each; the first three clips of every subject contain no annotated fall).")
add_table([
    ["Subject", "Fall clips", "Note"],
    ["1 - 2, 4 - 7, 9 - 10", "10 each", "falls 1 to 10 in clips 4 to 13, in order"],
    ["3", "9", "two falls inside clip 4; clip 8 contains no annotated fall (Section 5.2)"],
    ["8", "10", "clips 9, 10 and 11 store falls 7, 8 and 6 in file order (Section 5.1)"],
    ["Total", "99 of 130", "31 no-fall clips; ratio 3.2 : 1"],
], widths=[1.6, 1.05, 3.85])
para("Table 5. Synchronization: offset between the index position timestamp and the annotated time in falls.csv (100 events per modality).")
add_table([
    ["Modality", "Median offset", "p90 of |offset|", "Events beyond 2 s"],
    ["Accelerometer", "+0.72 s", "1.10 s", "1 (subject_3 / fall 2, -9.0 s)"],
    ["Radar", "+0.62 s", "1.00 s", "1 (subject_3 / fall 2, +10.0 s)"],
    ["LiDAR", "+0.63 s", "1.00 s", "1 (subject_3 / fall 2, +10.1 s)"],
    ["IR camera", "+0.34 s", "0.73 s", "1 (subject_3 / fall 2, +9.8 s)"],
], widths=[1.2, 1.15, 1.2, 2.95])
para("The small positive offset of 0.3 to 0.7 seconds is consistent across subjects: the index matrices point at the movement peak just after the annotated event start. Apart from the single subject_3 / fall 2 record, all 99 remaining events agree within 1.1 s on all four sensors, which confirms that the index matrices can be trusted for labelling.")
para("Table 6. Integrity scan: missing values and infinities.")
add_table([
    ["File type", "Rows checked", "Missing values", "Infinities"],
    ["Accelerometer", "81,250", "0", "0"],
    ["LiDAR", "44,226", "0", "0"],
    ["IR camera", "11,877", "0", "0"],
    ["Total", "137,353", "0", "0"],
], widths=[1.5, 1.3, 1.45, 1.25])
para("Radar (checked structurally): 36,838 frames in total, of which 1,377 frames (3.7 %) contain no detected target; the largest number of targets in one frame is 186. Only subject_3 and subject_10 have radar recorded in two segments; every other radar file is one continuous stream.")
para("Table 7. Raw data as received versus after the operations described above.")
add_table([
    ["Property", "Raw, as received", "After operations"],
    ["Clip organisation", "continuous recordings, no clip boundaries or labels", "130 clips of 10 s, each labelled fall / no-fall"],
    ["Class balance", "not directly computable", "99 fall / 31 no-fall (3.2 : 1)"],
    ["Sampling rates", "taken from documentation (one wrong figure)", "measured per file: 62.5 / 8.33 / 10.0 / 2.6 Hz"],
    ["Label alignment", "index matrices never cross-checked", "99 of 100 events within 1.1 s; 1 event flagged"],
    ["Data integrity", "unknown", "0 NaN, 0 infinities in 137,353 rows"],
    ["Known anomalies", "not documented", "3 documented (Section 5)"],
    ["Files modified", "-", "none; every operation was read-only"],
], widths=[1.15, 2.4, 2.95])

# ---------------- 5 ----------------
doc.add_heading("5. Anomalies Found", level=1)
doc.add_heading("5.1 subject_8: fall clips stored out of order", level=2)
para("At sample 6,250, the start of the eleventh clip, the timestamp jumps back by 67.0 seconds: the last clips were concatenated out of chronological order. Measured effect: clips 9, 10 and 11 contain falls 7, 8 and 6 respectively in file order (falls 6 and 7 are inverted). Time-gap segmentation (Method A) reacts to positive gaps only, so the negative jump merges two clips into one segment: subject_8 yields 12 segments instead of 13, two falls collapse into a single window, and the dataset-wide mapping drops to 97 fall / 32 no-fall clips. With fixed 625-sample blocks (Method B) every clip stays intact and the index matrices still identify each fall correctly. Decision: cut subject_8 by fixed blocks and assign labels exclusively through the index matrices; never assume that clip k contains fall k.")
doc.add_heading("5.2 subject_3, fall 2: one fall record cannot be reconciled", level=2)
para("This is the only event, out of 100, where the index matrices and the annotated time disagree by more than 2 seconds, and the disagreement concerns all four sensors: the accelerometer index sits 9.0 seconds before the annotated time (at the very last sample of clip 4), while radar, LiDAR and IR indices sit about 10 seconds after it. In addition, the annotated time falls inside a recording gap of the accelerometer: clip 4 ends 9.0 seconds before it and clip 5 starts 34 seconds after it. Every other event of the same subject agrees within 1 second. Consequence and decision: clip 4 is kept as a fall clip (it directly contains fall 1); fall 2 is marked unresolved and must be checked against the session notes before final training; if it cannot be resolved, this single event is excluded from the fall labels and recorded in the exclusion list. Related: clip 8 of subject_3 (a 10-second clip with no annotated fall nearby and no index entry) is kept as a no-fall clip but carries a review flag.")
doc.add_heading("5.3 radar frames without detection", level=2)
para("1,377 of 36,838 radar frames (3.7 %) contain no detected target, and two subjects (3 and 10) have their radar in two recording segments. Decision: the later feature extraction will encode empty frames explicitly (target count = 0) instead of dropping them silently, so that the model sees the sensor's real detection behaviour.")

# ---------------- 6 ----------------
doc.add_heading("6. Decisions Adopted", level=1)
bullet("Fixed 625-sample clips (10.00 s), 13 clips per subject, labels read from the index matrices (position divided by 625).", "Segmentation. ")
bullet("Keep each sensor at its measured native rate; no resampling before radar feature extraction; align modalities on the time axis when building fused clips (Section 7).", "Sampling. ")
bullet("A clip is positive if any index position falls inside it; two falls inside one clip count once as a positive clip (subject_3, clip 4).", "Labelling. ")
bullet("Raw files stay untouched; derived numbers are reproducible from the two scripts; the flagged records (subject_3 / fall 2, subject_3 clip 8) go into an exclusion list shipped with the processed data.", "Traces. ")

# ---------------- 7 ----------------
doc.add_heading("7. Remaining Cleaning Pipeline (Next Work Item)", level=1)
para("The steps below turn the verified raw files into model-ready arrays. They are the next implementation item and are the required input for the CNN / LSTM baselines and the metric-learning comparison.")
numbered(1, "Convert each variable-length radar frame into a fixed-length feature vector (target count, range statistics, radial velocity statistics), and quantify per-clip detection gaps.", "Radar feature extraction: ")
numbered(2, "Slice all four modalities on the 130 fixed clips; for fusion, build a common time base per clip from the timestamps instead of concatenating raw rows.", "Clip and window construction: ")
numbered(3, "Compute scaling statistics (mean / standard deviation per channel and modality) on training folds only, inside each split, and store them with the split.", "Normalization: ")
numbered(4, "Leave-one-subject-out, 10 folds, for the unseen-subject evaluation protocol; store fold membership.", "Splits: ")
numbered(5, "Save processed arrays (.npz), labels, splits and the exclusion list, then re-derive the counts (130 clips, 99 / 31, per-subject fall clips) from the saved artifacts as a final quality check before training.", "Artifacts and final QA: ")

# ---------------- 8 ----------------
doc.add_heading("8. Reproducing the Measurements", level=1)
para("Both commands are read-only and print every number quoted in this report:")
para("D:\\Anaconda\\python.exe scripts\\explorer_donnees.py", style="No Spacing")
para("D:\\Anaconda\\python.exe scripts\\verifier_donnees_quida.py", style="No Spacing")
para("Reference documents: README.md (dataset notes), etat_de_lart/plan_semaines_1_2.md (two-week study plan), scripts/explorer_donnees.py and scripts/verifier_donnees_quida.py.")

from docx.oxml.ns import qn
title_style = doc.styles["Title"]
_pPr = title_style.element.get_or_add_pPr()
for _bdr in _pPr.findall(qn("w:pBdr")):
    _pPr.remove(_bdr)

doc.core_properties.title = "Data Cleaning Report for the QUIDA Fall Detection Dataset"
doc.core_properties.author = "Clemence Vergniaud, Yuanzhe Li"
doc.core_properties.subject = "PFP project - QUIDA fall detection - raw data verification and cleaning status"

doc.save(OUT)
print("saved:", OUT)


