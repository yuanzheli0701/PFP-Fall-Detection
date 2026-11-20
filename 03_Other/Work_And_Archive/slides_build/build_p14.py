# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\slides\P14_OUR_PROJECT_corrected.pptx"

PX = lambda v: Inches(v / 110.0)
CENTER_OFF = 0.2888
NUDGE = -2.5

SLATE = RGBColor(0x4E, 0x6E, 0x81)
PLUM  = RGBColor(0x41, 0x3A, 0x42)
WARM  = RGBColor(0xA7, 0x9E, 0x9C)
ROWG  = RGBColor(0xF2, 0xF1, 0xF1)
BOXM  = RGBColor(0xB3, 0xB0, 0xB5)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.3333)
prs.slide_height = Inches(7.5)
slide = prs.slides.add_slide(prs.slide_layouts[6])

def rect(x, y, w, h, color, rounded=False, radius=0.044):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        PX(x), PX(y), PX(w), PX(h))
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    if rounded:
        shp.adjustments[0] = radius
    return shp

def textr(x, y, runs, base_size=None, mid=None):
    size = base_size or max(r[2] for r in runs)
    if mid is None:
        top = PX(y + NUDGE - CENTER_OFF * size); h = PX(size * 2.2)
    else:
        top = PX(mid[0]); h = PX(mid[1])
    tb = slide.shapes.add_textbox(PX(x), top, PX(1100), h)
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    if mid is not None:
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    for (s, name, sz, bold, color, spc) in runs:
        r = p.add_run(); r.text = s
        f = r.font; f.size = Pt(sz); f.bold = bold; f.name = name; f.color.rgb = color
        if spc is not None:
            rPr = r._r.get_or_add_rPr(); rPr.set('spc', str(int(spc * 100)))
    return tb

def text(x, y, s, size, color=BLACK, bold=False, font="Lato", mid=None):
    return textr(x, y, [(s, font, size, bold, color, None)], base_size=size, mid=mid)

def text_multi(x, y_top, y_bot, lines, size, color=BLACK, font="Lato"):
    tb = slide.shapes.add_textbox(PX(x), PX(y_top), PX(1100), PX(y_bot - y_top))
    tf = tb.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, s in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = s
        f = r.font; f.size = Pt(size); f.name = font; f.color.rgb = color
    return tb

# decorations
for y, h in [(9, 28), (57, 28), (105, 28), (154, 26)]:
    rect(77, y, 7, h, SLATE)
rect(1364, 83, 20, 19, BLACK)
text(1420, 768, "14", 15.3, font="Lato")

# title
text(110, 44, "07", 40, WARM, bold=True, font="Arial")
text(239, 46, "OUR PROJECT", 40, BLACK, bold=True, font="Arial")
text(111, 146.5, "How we will use it on QUIDA", 18.7, BLACK, bold=True, font="Heebo")

# left column
text(73, 228, "Two sensors, two encoders", 21.3, SLATE, bold=True, font="Heebo")
text(85, 272.5, "\u2022", 18, font="Arial"); text(103, 272.5, "Baseline: encoder + classifier head (supervised)", 18)
text(85, 315.5, "\u2022", 18, font="Arial"); text(103, 315.5, "Metric learning: same encoder, trained with Siamese", 18)
text(102, 351.5, "or Triplet loss", 18)
text(85, 391.5, "\u2022", 18, font="Arial"); text(103, 391.5, "Same encoder in both cases, so the comparison is fair", 18)
text(73, 447, "Decision", 21.3, SLATE, bold=True, font="Heebo")
text(85, 491.5, "\u2022", 18, font="Arial"); text(103, 491.5, "Class prototypes (main) and k-NN", 18)
text(73, 547, "Evaluation: leave-one-subject-out", 21.3, SLATE, bold=True, font="Heebo")
text(85, 592.5, "\u2022", 18, font="Arial"); text(103, 592.5, "Train on 9 subjects, test on the 10th, repeat 10 times", 18)
text(85, 633.5, "\u2022", 18, font="Arial"); text(103, 633.5, "Measures: recall, specificity, F1, AUROC", 18)

# table
rect(785, 216, 607, 69, SLATE)
rect(785, 285, 607, 65, ROWG)
text(796, 0, "Sensor", 13, WHITE, bold=True, font="Heebo", mid=(216, 69))
text(986, 0, "Window (4 s)", 13, WHITE, bold=True, font="Heebo", mid=(216, 69))
text(1258, 0, "Encoder", 13, WHITE, bold=True, font="Heebo", mid=(216, 69))
text(795, 0, "Accelerometer", 13, BLACK, bold=True, font="Heebo", mid=(287, 65))
text(987, 0, "~250 samples \u00d7 3 axes", 13, mid=(287, 65))
text(1259, 0, "1D-CNN", 13, mid=(287, 65))
text(796, 0, "Radar", 13, BLACK, bold=True, font="Heebo", mid=(352, 70))
text(987, 0, "~33 frames \u00d7 23 statistics", 13, mid=(352, 70))
text_multi(1259, 352, 422, ["1D-CNN", "(LSTM next)"], 13)

# dark box
rect(785, 437, 607, 273, PLUM, rounded=True)
text(820, 473, "TWO KINDS OF ERROR", 19.3, BOXM, bold=True, font="Heebo")
text(825, 506, "\u2022", 16.7, WHITE, font="Arial")
textr(844, 506, [("False negative:", "Lato", 16.7, True, WHITE, None),
                 (" a real fall is missed. Dangerous.", "Lato", 16.7, False, WHITE, None)], base_size=16.7)
text(842, 540, "Tracked by recall.", 16.7, WHITE)
text(825, 581, "\u2022", 16.7, WHITE, font="Arial")
textr(844, 581, [("False positive:", "Lato", 16.7, True, WHITE, None),
                 (" an alarm without a fall.", "Lato", 16.7, False, WHITE, None)], base_size=16.7)
text(842, 615, "Annoying. Tracked by specificity.", 16.7, WHITE)

# speaker notes
notes = (
    "EN: Where we are. Done: dataset verified and the four sensor rates measured; "
    "QC report written; 4 s / 1:3 windowing built (383 windows = 99 fall / 284 no-fall); "
    "leave-one-subject-out split with normalisation fitted on training subjects only; "
    "encoder and loss code in place (1D-CNN encoder, triplet loss with semi-hard mining, "
    "focal loss for the supervised baseline). Radar input: 33 frames x 23 summary statistics. "
    "Next step: the full supervised-vs-metric comparison, the LSTM baseline, thermal + LiDAR, "
    "concat/late fusion, prototypes vs k-NN, ablations, then the report.\n\n"
    "\u4E2D: P14 \u73B0\u72B6\u3002\u5DF2\u5B8C\u6210\uFF1A\u6570\u636E\u96C6\u6838\u9A8C\u4E0E\u56DB\u4F20\u611F\u5668\u9891\u7387\u5B9E\u6D4B\uFF1B"
    "QC \u62A5\u544A\uFF1B4 \u79D2\u7A97 / 1:3 \u5207\u7A97\uFF08383 \u4E2A\u7A97\u53E3 = 99 \u8DCC\u5012 / 284 \u65E0\u8DCC\u5012\uFF09\uFF1B"
    "\u7559\u4E00\u53D7\u8BD5\u8005\u5212\u5206\uFF0C\u5F52\u4E00\u5316\u4EC5\u5728\u8BAD\u7EC3\u53D7\u8BD5\u8005\u4E0A\u62DF\u5408\uFF1B"
    "\u7F16\u7801\u5668\u4E0E\u635F\u5931\u4EE3\u7801\u5C31\u4F4D\uFF081D-CNN \u7F16\u7801\u5668\u3001semi-hard \u4E09\u5143\u7EC4\u635F\u5931\u3001"
    "\u76D1\u7763\u7AEF focal \u635F\u5931\uFF09\u3002\u96F7\u8FBE\u8F93\u5165\uFF1A33 \u5E27 \u00D7 23 \u4E2A\u7EDF\u8BA1\u91CF\u3002"
    "\u4E0B\u4E00\u6B65\uFF1A\u5B8C\u6574\u7684\u76D1\u7763 vs \u5EA6\u91CF\u5BF9\u6BD4\u3001LSTM \u57FA\u7EBF\u3001\u70ED\u6210\u50CF + LiDAR\u3001"
    "\u62FC\u63A5/\u540E\u671F\u878D\u5408\u3001prototype vs k-NN\u3001\u6D88\u878D\u5B9E\u9A8C\uFF0C\u6700\u540E\u51FA\u62A5\u544A\u3002"
)
slide.notes_slide.notes_text_frame.text = notes

prs.save(OUT)
print("saved:", OUT)
