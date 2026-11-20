import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/13968/Documents/ChatGPT/PFP _ Fall detection";
const BUILD = ROOT + "/_work/deck_en_build";
const PREVIEW = BUILD + "/preview";
const FIG = ROOT + "/figures/en";
const SKILL_DIR = "C:/Users/13968/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations";
const utils = await import(pathToFileURL(SKILL_DIR + "/container_tools/artifact_tool_utils.mjs").href);
const { makeNativeBulletParagraphs, finalizePresentation } = utils;

const FINAL_PPTX = ROOT + "/slides/PFP_QUIDA_CNN_LSTM_MetricLearning_EN.pptx";
const DRAFT_PPTX = BUILD + "/draft_deck.pptx";

const FONT = "Segoe UI";
const INK = "#0F172A";
const MUTED = "#475569";
const FAINT = "#94A3B8";
const LINE = "#E2E8F0";
const PANEL = "#F8FAFC";
const BLUE = "#2563EB";
const EMERALD = "#059669";
const VIOLET = "#7C3AED";
const AMBER = "#B45309";

function addText(slide, name, x, y, w, h, text, opts) {
  const o = opts || {};
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text.style = {
    typeface: FONT,
    fontSize: o.size || 16,
    bold: o.bold || false,
    color: o.color || INK,
    alignment: o.align || "left",
    verticalAlignment: o.valign || "top",
    lineSpacing: o.lineSpacing || 1.2,
    insets: 0,
    autoFit: "none",
  };
  shape.text = text;
  return shape;
}

function addBullets(slide, name, x, y, w, h, items, opts) {
  const o = opts || {};
  const shape = slide.shapes.add({
    geometry: "textbox",
    name: name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text.style = {
    typeface: FONT,
    fontSize: o.size || 16,
    bold: false,
    color: o.color || MUTED,
    alignment: "left",
    verticalAlignment: "top",
    lineSpacing: o.lineSpacing || 1.28,
    insets: 0,
    autoFit: "none",
  };
  shape.text = makeNativeBulletParagraphs(items, {
    marginLeftPoints: 17,
    hangingPoints: 8.5,
    spaceAfterPoints: o.spaceAfter || 12,
  });
  return shape;
}

function addCard(slide, name, x, y, w, h, opts) {
  const o = opts || {};
  return slide.shapes.add({
    geometry: "rect",
    name: name,
    position: { left: x, top: y, width: w, height: h },
    fill: o.fill || PANEL,
    line: { style: "solid", fill: o.line === undefined ? LINE : o.line, width: o.lineWidth === undefined ? 1 : o.lineWidth },
    borderRadius: o.radius || "rounded-xl",
  });
}

function addRect(slide, name, x, y, w, h, fill, radius) {
  return slide.shapes.add({
    geometry: "rect",
    name: name,
    position: { left: x, top: y, width: w, height: h },
    fill: fill,
    line: { style: "solid", fill: "none", width: 0 },
    borderRadius: radius || 0,
  });
}

function addLine(slide, name, x, y, w, h, color, width, dash) {
  return slide.shapes.add({
    geometry: "rect",
    name: name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: dash ? "dashed" : "solid", fill: color, width: width || 1 },
  });
}

async function addImage(slide, file, name, x, y, w, h, alt) {
  const bytes = await fs.readFile(file);
  const blob = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  return slide.images.add({
    blob: blob,
    contentType: "image/png",
    alt: alt,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function header(slide, eyebrow, accent, title, titleSize) {
  addText(slide, "eyebrow", 64, 40, 900, 22, eyebrow, { size: 12, bold: true, color: accent });
  addText(slide, "heading", 64, 66, 1152, 84, title, { size: titleSize || 27, bold: true, lineSpacing: 1.05 });
}

function footer(slide, folio) {
  addText(slide, "footer-left", 64, 688, 420, 16, "QUIDA - fall detection", { size: 10, color: FAINT });
  if (folio) {
    addText(slide, "footer-folio", 1128, 688, 88, 16, folio, { size: 10, color: FAINT, align: "right" });
  }
}

function notes(slide, paragraphs) {
  slide.speakerNotes.text = paragraphs;
}

function run(text, color, bold) {
  return { run: text, style: { typeface: FONT, color: color || INK, bold: bold || false } };
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// ---------------- Slide 1 - Cover ----------------
const s1 = presentation.slides.add();
s1.background.fill = "linear(160deg, slate-950 0%, blue-950 100%)";
addRect(s1, "cover-rule", 64, 206, 72, 4, "#3B82F6", 2);
addText(s1, "cover-eyebrow", 64, 166, 900, 22, "PFP - IP.3510 - FALL DETECTION ON QUIDA", { size: 13, bold: true, color: "#93C5FD" });
addText(s1, "cover-title", 64, 228, 1020, 132, [
  [run("CNN, LSTM, and metric learning", "#FFFFFF", true)],
  [run("for fall detection on QUIDA", "#FFFFFF", true)],
], { size: 45, lineSpacing: 1.1 });
addText(s1, "cover-sub", 64, 384, 940, 70, "Supervised baselines vs. learned-distance classification - limited data, unseen subjects", { size: 17, color: "#CBD5E1", lineSpacing: 1.35 });
addText(s1, "cover-meta", 64, 560, 1000, 96, [
  [run("Team   ", "#E2E8F0", true), run("Clémence Vergniaud  ·  Yuanzhe Li", "#94A3B8", false)],
  [run("Advisor   ", "#E2E8F0", true), run("Wafa Njima", "#94A3B8", false)],
  [run("Weekly review - October 2026", "#94A3B8", false)],
], { size: 14, lineSpacing: 1.75 });
notes(s1, [
  "Opening (30 s). One sentence to frame the review: we are building fall detection on QUIDA and comparing two ways to learn - direct supervised classifiers, and distance-based (metric) models.",
  "Goal for today: validate the method choices before coding the metric models next week. Keep the pace tight; questions are collected at the end and the total budget is about 12 minutes.",
]);

// ---------------- Slide 2 - Agenda ----------------
const s2 = presentation.slides.add();
header(s2, "AGENDA", BLUE, "Four blocks - about twelve minutes", 28);
footer(s2, "2");
const agenda = [
  ["01", "2 min", "Context & protocol", "QUIDA data, constraints, and how we evaluate."],
  ["02", "5 min", "CNN & LSTM", "What each architecture contributes to the pipeline."],
  ["03", "4 min", "Metric learning", "Why our experiment needs learned distances."],
  ["04", "2 min", "Next steps", "Implementation plan, fusion, and the data-reduction study."],
];
const agendaPos = [[64, 164], [656, 164], [64, 366], [656, 366]];
agenda.forEach(function (row, i) {
  const x = agendaPos[i][0];
  const y = agendaPos[i][1];
  addCard(s2, "agenda-card-" + (i + 1), x, y, 560, 170);
  addText(s2, "agenda-num-" + (i + 1), x + 28, y + 22, 80, 22, row[0], { size: 15, bold: true, color: BLUE });
  addText(s2, "agenda-time-" + (i + 1), x + 448, y + 24, 84, 20, row[1], { size: 12, color: FAINT, align: "right" });
  addText(s2, "agenda-title-" + (i + 1), x + 28, y + 54, 500, 30, row[2], { size: 21, bold: true });
  addText(s2, "agenda-desc-" + (i + 1), x + 28, y + 96, 500, 64, row[3], { size: 14.5, color: MUTED, lineSpacing: 1.3 });
});
notes(s2, [
  "Agenda (30 s). Walk through the four blocks quickly: context and protocol; what CNN and LSTM each contribute; why metric learning is the right answer for our constraints; and the plan for the coming weeks.",
  "Signal that block 3 is the core of the review; the rest is context the team already largely knows.",
]);

// ---------------- Slide 3 - Context ----------------
const s3 = presentation.slides.add();
header(s3, "01 · CONTEXT", BLUE, "Goal: compare supervised baselines with metric learning on QUIDA", 27);
footer(s3, "3");
addBullets(s3, "context-bullets", 64, 200, 590, 380, [
  "Task: classify 10 s sensor windows as fall or no-fall.",
  "QUIDA: 10 subjects, four modalities; we start with the accelerometer (62.5 Hz) and the radar (8.3 Hz).",
  "Limits: few labelled windows, imbalanced classes, and tests on subjects the model has never seen.",
], { size: 16, spaceAfter: 18 });
addCard(s3, "routes-card", 676, 172, 540, 400);
addText(s3, "routes-title", 704, 196, 480, 28, "Two routes, one protocol", { size: 19, bold: true });
addRect(s3, "routes-divider", 704, 238, 484, 1, LINE, 0);
addText(s3, "route-a", 704, 258, 480, 26, [run("Route A - Supervised", BLUE, true)], { size: 15 });
addText(s3, "route-a-desc", 704, 290, 480, 64, "1D-CNN for the accelerometer, LSTM for the radar; trained directly on labels.", { size: 14, color: MUTED, lineSpacing: 1.32 });
addText(s3, "route-b", 704, 380, 480, 26, [run("Route B - Metric learning", VIOLET, true)], { size: 15 });
addText(s3, "route-b-desc", 704, 412, 480, 84, "Embed windows so that distances reflect similarity; classify by prototype or nearest neighbour.", { size: 14, color: MUTED, lineSpacing: 1.32 });
addText(s3, "route-foot", 704, 508, 484, 40, "Shared encoders and splits - the comparison isolates the objective and the decision rule.", { size: 13, color: FAINT, lineSpacing: 1.3 });
notes(s3, [
  "Context (1 min). QUIDA comes from the OSF archive: 10 subjects recorded with four sensor families. This period we scope to the accelerometer (62.5 Hz) and the radar (8.3 Hz); LiDAR and the IR camera stay out unless time allows.",
  "The scientific question is not 'which architecture wins' but 'does learning distances instead of labels help when labelled data is scarce'. Both routes share encoders and splits, so the comparison isolates the training objective and the decision rule.",
  "Dataset reference: Taramasco et al., 2025 - QUIDA multimodal fall dataset (OSF archive).",
]);

// ---------------- Slide 4 - Data & protocol ----------------
const s4 = presentation.slides.add();
header(s4, "01 · CONTEXT", BLUE, "Small, imbalanced, subject-disjoint - the protocol follows from that", 27);
footer(s4, "4");
const stats = [
  ["About 130", "windows of 10 s (625 samples at 62.5 Hz)"],
  ["About 3 : 1", "fall vs. no-fall windows in the raw clips"],
  ["10 folds", "leave-one-subject-out; test subjects never seen"],
];
stats.forEach(function (st, i) {
  const x = 64 + i * 392;
  addText(s4, "stat-" + (i + 1) + "-value", x, 168, 360, 34, st[0], { size: 25, bold: true, color: BLUE });
  addText(s4, "stat-" + (i + 1) + "-label", x, 206, 360, 44, st[1], { size: 13, color: MUTED, lineSpacing: 1.3 });
});
await addImage(s4, FIG + "/fig_fall_window.png", "fall-window", 190, 264, 900, 390, "A real 10 s accelerometer fall window with impact peak and the three phases");
addText(s4, "protocol-caption", 190, 664, 900, 20, "We cut 4 s windows around each annotated fall; negative windows must not overlap a fall. Metrics: recall, precision, F1, specificity.", { size: 12.5, color: FAINT });
notes(s4, [
  "Protocol (1 min). Numbers on the slide: about 130 ten-second clips (13 per subject x 10), roughly three fall windows for every non-fall window; folds are leave-one-subject-out, so the test subject is never seen in training.",
  "Windows are cut 4 s around each annotated fall, and negatives are kept only if they do not overlap a fall window - the stillness after a fall must never be labelled 'no-fall'.",
  "Metrics: recall, precision, F1 and specificity; accuracy would flatter a majority-class guess. Speaker note: the README says 97/32 while the study plan says 99/31 - recount before the presentation and fix the slide. Source: QUIDA dataset paper (Taramasco et al., 2025).",
]);

// ---------------- Slide 5 - CNN principles ----------------
const s5 = presentation.slides.add();
header(s5, "02 · CNN", BLUE, "A 1D-CNN learns local shapes: filters slide along the signal", 27);
footer(s5, "5");
addBullets(s5, "cnn-principles", 64, 196, 404, 400, [
  "A convolution is a small learnable filter - length 5 here - sliding along the window.",
  "Weight sharing and a local receptive field give few parameters, and the same pattern is detected wherever it appears.",
  "Stacked layers build a hierarchy: slopes and peaks first, then the impact shape.",
], { size: 15, spaceAfter: 16 });
await addImage(s5, FIG + "/fig_conv1d.png", "conv1d", 492, 172, 700, 377, "One filter sliding along the acceleration signal with the strongest response at the impact");
notes(s5, [
  "CNN intuition (1.5 min). The filter is a length-5 kernel sliding along the acceleration magnitude; it responds strongly at the impact and stays near zero on flat sections.",
  "Weight sharing means the same detector works anywhere in the window, and stacking layers enlarges the receptive field so deeper filters see richer shapes.",
  "Classic reference for this style of baseline: Wang, Yan and Oates, 2016 - time series classification from scratch with deep neural networks. Detailed arithmetic (stride, padding, output sizes) is on backup slide B1.",
]);

// ---------------- Slide 6 - CNN for accelerometer ----------------
const s6 = presentation.slides.add();
header(s6, "02 · CNN", BLUE, "The accelerometer baseline: three conv blocks watch for the impact peak", 27);
footer(s6, "6");
await addImage(s6, FIG + "/fig_cnn_arch.png", "cnn-arch", 64, 168, 1104, 444, "Architecture of the 1D-CNN baseline: three convolutional blocks, pooling, global average pooling and a two-class head");
addText(s6, "cnn-arch-caption-1", 64, 624, 1104, 20, "Input 3 x 625 -> three conv blocks + global average pooling -> 2 classes.", { size: 13, color: MUTED });
addText(s6, "cnn-arch-caption-2", 64, 648, 1104, 20, "Architecture drawn on the 10 s analysis window; the protocol keeps the same blocks on 4 s windows (about 250 samples).", { size: 13, color: FAINT });
notes(s6, [
  "Baseline architecture (1 min). Three convolutional blocks with pooling, then global average pooling and a small dense head: about 9.3 k parameters, training in seconds on CPU.",
  "The final receptive field covers 24 samples, roughly 0.38 s - tuned to the impact, not the whole window. The figure is drawn on the 10 s analysis window; the protocol keeps the same blocks but cuts 4 s windows (about 250 samples).",
  "Related work: Santos et al., 2019 - accelerometer fall detection with a CNN; Casilari-Perez and Garcia-Lagos, 2020 - CNN fall detection across several datasets.",
]);

// ---------------- Slide 7 - LSTM principles ----------------
const s7 = presentation.slides.add();
header(s7, "03 · LSTM", EMERALD, "LSTM gates decide what to keep, write, and expose over time", 27);
footer(s7, "7");
await addImage(s7, FIG + "/fig_lstm_cell.png", "lstm-cell", 160, 162, 960, 483, "The LSTM cell: forget, input and output gates around the cell state, with the candidate update");
notes(s7, [
  "LSTM intuition (1.5 min). The cell state is the memory highway: the forget gate erases, the input gate writes, the output gate exposes a filtered version as the hidden state.",
  "Gates are sigmoid units, so they learn to open and close smoothly; the tanh candidate proposes new content. This solves the vanishing-gradient problem of a plain RNN and lets the model bridge the seconds between free fall, impact and stillness.",
  "If the equations come up: cell update c_t = f_t (.) c_{t-1} + i_t (.) c_tilde_t, hidden state h_t = o_t (.) tanh(c_t), where (.) is elementwise multiplication.",
]);

// ---------------- Slide 8 - LSTM for radar ----------------
const s8 = presentation.slides.add();
header(s8, "03 · LSTM", EMERALD, "Radar branch: summarize each frame, then let the LSTM read the timeline", 27);
footer(s8, "8");
const pipeline = [
  ["Radar frames", "8.3 Hz, variable detections"],
  ["Per-frame features", "8 values: count, Doppler, height, centroid"],
  ["About 33-frame sequence", "4 s window at 8.3 Hz"],
  ["LSTM -> fall score", "height drop + Doppler spike"],
];
pipeline.forEach(function (p, i) {
  const x = 95 + i * 280;
  addCard(s8, "pipe-box-" + (i + 1), x, 178, 250, 104);
  addText(s8, "pipe-title-" + (i + 1), x + 18, 196, 216, 24, p[0], { size: 15.5, bold: true });
  addText(s8, "pipe-desc-" + (i + 1), x + 18, 226, 216, 46, p[1], { size: 12, color: MUTED, lineSpacing: 1.25 });
  if (i < 3) {
    s8.shapes.add({ geometry: "rightArrow", name: "pipe-arrow-" + (i + 1), position: { left: x + 252, top: 218, width: 26, height: 24 }, fill: "#CBD5E1", line: { style: "solid", fill: "none", width: 0 } });
  }
});
addBullets(s8, "radar-bullets-left", 64, 330, 540, 200, [
  "Why not PointNet-style point sets: they need far more data than QUIDA offers - we summarize frames instead.",
  "Raw radar frames vary in length; fixed per-frame features keep the input regular.",
], { size: 15, spaceAfter: 16 });
addBullets(s8, "radar-bullets-right", 656, 330, 560, 200, [
  "The LSTM reads the fall's evolution: pre-impact, impact, then lying still.",
  "Expected signature: a height drop followed by a Doppler peak.",
], { size: 15, spaceAfter: 16 });
addText(s8, "radar-ref", 64, 636, 1152, 20, "Reference: Musci et al. - online fall detection with recurrent networks and sliding windows.", { size: 12.5, color: FAINT });
notes(s8, [
  "Radar branch (1 min). Radar frames contain a variable number of detections, so each frame is summarized into 8 fixed features (point count, mean and max Doppler, mean height, centroid, spread).",
  "A 4 s window gives about 33 frames; the LSTM reads the sequence and outputs a fall score. We deliberately avoid point-set networks such as PointNet (Qi et al., 2017) - they are data-hungry, and QUIDA is small.",
  "The temporal signature we expect: a height drop followed by a Doppler peak. Related work: Musci et al. - online fall detection with recurrent networks.",
]);

// ---------------- Slide 9 - Baseline limits ----------------
const s9 = presentation.slides.add();
header(s9, "04 · METRIC LEARNING", VIOLET, "A standard classifier is fragile with this little data", 28);
footer(s9, "9");
const limits = [
  ["01", "Few labels, imbalanced classes", "About three falls for every non-fall. Cross-entropy drifts toward the majority class - and accuracy still looks fine."],
  ["02", "Bound to the training classes", "The output layer is tied to the classes it was trained on. New subject or new class - retrain."],
  ["03", "Weak cross-subject generalization", "Only ten subjects, so models can memorize individual style; leave-one-subject-out exposes it."],
];
limits.forEach(function (c, i) {
  const x = 64 + i * 392;
  addCard(s9, "limit-card-" + (i + 1), x, 172, 368, 330);
  addText(s9, "limit-num-" + (i + 1), x + 26, 196, 60, 22, c[0], { size: 14, bold: true, color: VIOLET });
  addText(s9, "limit-title-" + (i + 1), x + 26, 228, 316, 58, c[1], { size: 18, bold: true, lineSpacing: 1.12 });
  addText(s9, "limit-desc-" + (i + 1), x + 26, 296, 316, 180, c[2], { size: 14, color: MUTED, lineSpacing: 1.34 });
});
addRect(s9, "limit-accent", 64, 556, 4, 26, VIOLET, 2);
addText(s9, "limit-bottom", 82, 552, 1080, 34, "These three limits are exactly the regime that metric learning was designed for", { size: 17, bold: true });
notes(s9, [
  "Motivation (1 min). Three failure modes of direct classification on this dataset. One: with roughly 3:1 imbalance, cross-entropy drifts toward the majority class, and accuracy hides it.",
  "Two: the output layer is coupled to the classes of the training set, so a new class or a new deployment setting means retraining. Three: ten subjects is small enough that subject style is easily memorized - LOSO exposes it.",
  "Table 3 of our review rates metric methods clearly more robust under imbalance and limited data. This sets up the next two slides.",
]);

// ---------------- Slide 10 - Metric learning core ----------------
const s10 = presentation.slides.add();
header(s10, "04 · METRIC LEARNING", VIOLET, "Learn a space where distance means similarity", 28);
footer(s10, "10");
addBullets(s10, "metric-bullets", 64, 196, 540, 420, [
  "Train an encoder f so that similar windows land close together and different ones far apart.",
  "Training units become pairs and triplets: N windows give on the order of N x N / 2 pairs - much more signal from the same data.",
  "Classification is then pure distance: nearest neighbours or class prototypes. No classifier head to retrain.",
], { size: 15, spaceAfter: 16 });
addCard(s10, "embed-panel", 656, 168, 560, 400, { fill: PANEL, line: LINE });
addText(s10, "embed-caption", 676, 188, 520, 20, "Embedding space (schematic)", { size: 12, color: FAINT });
s10.shapes.add({ geometry: "ellipse", name: "cluster-fall", position: { left: 690, top: 252, width: 170, height: 140 }, fill: "none", line: { style: "dashed", fill: VIOLET, width: 1.5 } });
s10.shapes.add({ geometry: "ellipse", name: "cluster-nofall", position: { left: 1012, top: 252, width: 170, height: 140 }, fill: "none", line: { style: "dashed", fill: BLUE, width: 1.5 } });
const fallDots = [[735, 302], [775, 277], [815, 297], [745, 357], [800, 362]];
fallDots.forEach(function (d, i) {
  addRect(s10, "fall-dot-" + (i + 1), d[0] - 4, d[1] - 4, 9, 9, VIOLET, 4);
});
addRect(s10, "fall-prototype", 766, 314, 18, 18, VIOLET, 9);
const nofallDots = [[1057, 302], [1097, 277], [1137, 297], [1067, 357], [1122, 362]];
nofallDots.forEach(function (d, i) {
  addRect(s10, "nofall-dot-" + (i + 1), d[0] - 4, d[1] - 4, 9, 9, BLUE, 4);
});
addRect(s10, "nofall-prototype", 1088, 314, 18, 18, BLUE, 9);
addLine(s10, "distance-line", 862, 321, 148, 2, FAINT, 1.5, true);
addText(s10, "distance-label", 866, 292, 140, 20, "distance d", { size: 12, color: FAINT, align: "center" });
addText(s10, "cluster-fall-label", 690, 404, 170, 22, "fall windows", { size: 13.5, bold: true, color: VIOLET, align: "center" });
addText(s10, "cluster-nofall-label", 1012, 404, 170, 22, "no-fall windows", { size: 13.5, bold: true, color: BLUE, align: "center" });
addText(s10, "embed-foot", 676, 500, 520, 40, "Classify by nearest prototype (class mean) or by k-NN - no retraining required.", { size: 12.5, color: MUTED, lineSpacing: 1.3 });
notes(s10, [
  "Core idea (1.5 min). Metric learning replaces 'signal -> label' with 'signal -> embedding'. Training shapes the embedding through pairs (contrastive) or triplets (anchor, positive, negative).",
  "With N windows you can form on the order of N x N / 2 pairs, so a small dataset still yields many training constraints. At test time, classification is geometric: nearest prototype (class mean) or k-NN, and neither needs extra training.",
  "References: Hadsell, Chopra and LeCun, 2006 (contrastive loss); Koch et al., 2015 (siamese networks, one-shot learning); Snell et al., 2017 (prototypical networks).",
]);

// ---------------- Slide 11 - Why it fits + methods ----------------
const s11 = presentation.slides.add();
header(s11, "04 · METRIC LEARNING", VIOLET, "Metric learning matches our constraints - and it plugs into fusion", 27);
footer(s11, "11");
addCard(s11, "fit-card", 64, 166, 560, 404);
addText(s11, "fit-title", 92, 190, 500, 28, "Why it fits", { size: 19, bold: true });
addBullets(s11, "fit-bullets", 92, 232, 504, 320, [
  "Small data: pairs and triplets amplify the training signal.",
  "Imbalance: balanced P x K batches stop the majority class from dominating.",
  "Decisions: prototypes stay robust when one class is rare.",
  "Fusion: two encoders can be trained jointly on concatenated embeddings.",
], { size: 14.5, spaceAfter: 15 });
addCard(s11, "impl-card", 656, 166, 560, 404);
addText(s11, "impl-title", 684, 190, 500, 28, "What we will implement", { size: 19, bold: true });
const implRows = [
  ["Baseline", "1D-CNN for the accelerometer; LSTM for the radar."],
  ["Metric models", "Siamese + contrastive loss first; triplet + P x K + semi-hard as the main model."],
  ["Decision", "Prototypes first; k-NN on the same embeddings for comparison."],
  ["Fusion", "Intermediate fusion on concatenated embeddings; late fusion as the baseline."],
];
implRows.forEach(function (r, i) {
  const y = 236 + i * 82;
  addText(s11, "impl-label-" + (i + 1), 684, y, 500, 20, r[0], { size: 13, bold: true, color: VIOLET });
  addText(s11, "impl-text-" + (i + 1), 684, y + 22, 504, 56, r[1], { size: 13.5, color: MUTED, lineSpacing: 1.28 });
});
addRect(s11, "fair-accent", 64, 596, 4, 24, VIOLET, 2);
addText(s11, "fair-line", 82, 592, 1090, 32, "Same encoders, same splits as the baselines - only the training objective and the decision rule change", { size: 16, bold: true });
notes(s11, [
  "Why it fits us, and the choices (1.5 min). Four matches: small data - pairs and triplets amplify supervision; imbalance - balanced P x K batches and semi-hard triplet mining; robustness - prototypes use one summary per class instead of fitting the majority; fusion - two encoders trained jointly on concatenated embeddings.",
  "Implementation plan: reuse the supervised encoders, drop the classification layer. Contrastive loss first as the simplest reference, then triplet + P x K + semi-hard as the main model (FaceNet, Schroff et al., 2015; Hermans et al., 2017). Decisions by prototypes (primary) and k-NN (comparison). Fusion: intermediate first, late fusion as baseline.",
  "Key fairness point: identical encoders and identical splits - the only change is the objective and the decision rule.",
]);

// ---------------- Slide 12 - Next steps ----------------
const s12 = presentation.slides.add();
header(s12, "05 · NEXT STEPS", AMBER, "Next: metric models, then fusion, then the data-reduction study", 27);
footer(s12, "12");
const status = ["Data verified", "Pipeline + baselines run", "Literature review complete"];
status.forEach(function (t, i) {
  const x = 64 + i * 392;
  addCard(s12, "status-pill-" + (i + 1), x, 162, 368, 46, { fill: "#F1F5F9", line: "#F1F5F9", radius: "rounded-full" });
  addText(s12, "status-text-" + (i + 1), x, 174, 368, 24, t, { size: 14, color: "#334155", align: "center" });
});
const steps = [
  ["Week 3", "Implement the siamese network with contrastive loss; first embedding visualizations on the accelerometer."],
  ["Week 4", "Triplet loss with P x K batches and semi-hard mining; evaluate prototypes vs. k-NN on the same splits."],
  ["Then", "Intermediate fusion of accelerometer and radar; late fusion as the baseline."],
  ["Then", "Data-reduction study (k = 1, 2, 4, 8; 100% down to 10% of training falls), error analysis, report and defense."],
];
steps.forEach(function (st, i) {
  const y = 238 + i * 80;
  addText(s12, "step-time-" + (i + 1), 64, y, 140, 24, st[0], { size: 15, bold: true, color: AMBER });
  addText(s12, "step-text-" + (i + 1), 236, y - 2, 980, 60, st[1], { size: 15, color: MUTED, lineSpacing: 1.3 });
  addRect(s12, "step-rule-" + (i + 1), 64, y + 62, 1152, 1, LINE, 0);
});
addRect(s12, "question-accent", 64, 586, 4, 24, AMBER, 2);
addText(s12, "question-line", 82, 582, 1100, 32, "Today's question: do you agree with the 4 s window and the prototype-first decision rule?", { size: 16, bold: true });
notes(s12, [
  "Next steps (1 min). Status: data verified (synchronization checked; the subject_8 window-order trap is documented), the pipeline and both supervised baselines run, and the literature review is delivered.",
  "Plan: week 3 siamese + contrastive; week 4 triplet + P x K + semi-hard, then prototypes vs. k-NN; after that, intermediate fusion, then the data-reduction study (k = 1, 2, 4, 8 per class and 100/50/25/10% of training falls).",
  "Risks we are watching: radar feature design, triplet mining stability, augmentation leakage across subjects, and the subject_3 annotation offset of about 10 s, which we plan to fix or exclude.",
  "Question for today: do you agree with the 4 s window and the prototype-first decision rule? Expected deliverable: two metric models compared with the baselines on identical splits and data budgets.",
]);

// ---------------- Backup B1 ----------------
const b1 = presentation.slides.add();
header(b1, "BACKUP · NOT PRESENTED", "#64748B", "Convolution and pooling arithmetic", 28);
footer(b1, "B1");
addText(b1, "b1-formula", 64, 184, 1152, 44, "output length = (input + 2 x padding - kernel) / stride + 1", { size: 24, bold: true });
addBullets(b1, "b1-bullets", 64, 268, 950, 300, [
  "625 samples, kernel 5, padding 2, stride 1 -> 625 outputs; after max-pool 2 -> 312.",
  "Second block: 312 -> 312, pool -> 156; third block, kernel 3, padding 1 -> 156.",
  "Receptive field after three blocks: 24 samples, about 0.38 s at 62.5 Hz.",
], { size: 17, spaceAfter: 16 });
notes(b1, [
  "Backup - arithmetic. Keep this in reserve for the question 'why does the CNN see local shapes rather than the whole window'. The final receptive field of about 0.38 s is deliberately matched to the impact rather than the full 4 s.",
]);

// ---------------- Backup B2 ----------------
const b2 = presentation.slides.add();
header(b2, "BACKUP · NOT PRESENTED", "#64748B", "Contrastive and triplet losses at a glance", 28);
footer(b2, "B2");
addText(b2, "b2-contrastive-heading", 64, 176, 1000, 30, "Contrastive loss (Hadsell et al., 2006)", { size: 20, bold: true, color: VIOLET });
addText(b2, "b2-contrastive-1", 64, 214, 800, 30, "similar pair:  L = d^2", { size: 18 });
addText(b2, "b2-contrastive-2", 64, 248, 800, 30, "different pair:  L = max(0, m - d)^2", { size: 18 });
addText(b2, "b2-contrastive-desc", 64, 288, 900, 24, "Pulls similar windows together; pushes different ones beyond the margin m.", { size: 14.5, color: MUTED });
addRect(b2, "b2-rule", 64, 344, 1152, 1, LINE, 0);
addText(b2, "b2-triplet-heading", 64, 372, 1100, 30, "Triplet loss (Schroff et al., 2015; Hermans et al., 2017)", { size: 20, bold: true, color: VIOLET });
addText(b2, "b2-triplet-formula", 64, 410, 900, 30, "L = max(0, d(a, p) - d(a, n) + m)", { size: 18 });
addText(b2, "b2-triplet-desc", 64, 452, 1000, 50, "Semi-hard negatives: d(a, p) < d(a, n) < d(a, p) + m. Informative enough to learn from, not so hard that training collapses.", { size: 14.5, color: MUTED, lineSpacing: 1.32 });
notes(b2, [
  "Backup - losses. Contrastive: L = d^2 for similar pairs and max(0, m - d)^2 for dissimilar ones. Triplet: L = max(0, d(a, p) - d(a, n) + m).",
  "Semi-hard mining picks negatives with d(a, p) < d(a, n) < d(a, p) + m, which keeps gradients informative without destabilizing small batches (Schroff et al., 2015; Hermans et al., 2017).",
]);

// ---------------- Backup B3 ----------------
const b3 = presentation.slides.add();
header(b3, "BACKUP · NOT PRESENTED", "#64748B", "Why we report recall, precision, F1 and specificity", 28);
footer(b3, "B3");
addBullets(b3, "b3-bullets", 64, 204, 1100, 340, [
  "About three quarters of the windows are falls; predicting 'fall' everywhere already scores about 75% accuracy while detecting nothing.",
  "We report recall, precision, specificity and F1, computed on identical folds for every method.",
  "P x K batches keep every batch balanced; prototype decisions do not depend on class frequency.",
], { size: 17, spaceAfter: 18 });
notes(b3, [
  "Backup - imbalance. On a 99/31 split, 'always fall' scores roughly 76% accuracy and is useless. Recall tracks the falls we find, precision tracks the false alarms, specificity tracks the non-falls we leave alone.",
]);

// ---------------- Export previews and draft ----------------
async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(PREVIEW, { recursive: true });
for (let i = 0; i < presentation.slides.items.length; i += 1) {
  const slide = presentation.slides.items[i];
  const png = await presentation.export({ slide: slide, format: "png", scale: 1.5 });
  await writeBlob(PREVIEW + "/draft-" + String(i + 1).padStart(2, "0") + ".png", png);
}

const draftFile = await PresentationFile.exportPptx(presentation);
let draftPath = DRAFT_PPTX;
try {
  await draftFile.save(draftPath);
} catch (error) {
  draftPath = BUILD + "/draft_deck_" + Date.now() + ".pptx";
  await draftFile.save(draftPath);
}
console.log("draft:", draftPath, "slides:", presentation.slides.items.length);

// ---------------- Finalize (only with --finalize) ----------------
if (process.argv.includes("--finalize")) {
  const staging = BUILD + "/.codex-finalizer";
  await fs.mkdir(staging, { recursive: true });
  await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
  const candidatePath = staging + "/candidate.pptx";
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const result = await finalizePresentation({
    explicitTotalSlideCount: 15,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    workspaceDir: ROOT,
    candidatePath: candidatePath,
    finalPath: FINAL_PPTX,
    pythonExecutable: "C:/Users/13968/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
    integrityValidatorPath: SKILL_DIR + "/container_tools/inspect_presentation_package_integrity.py",
    layoutValidatorPath: SKILL_DIR + "/container_tools/inspect_presentation_layout_geometry.py",
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry",
      "--validate-heading-fit",
      "--cover-role", "cover",
    ],
    fontPolicy: { basis: "design", families: ["Segoe UI"] },
    verifyArtifactToolImport: true,
    receiptPath: staging + "/final.validation.json",
  });
  console.log("finalized:", JSON.stringify(result, null, 2));
  const finalPreview = PREVIEW + "/final";
  await fs.mkdir(finalPreview, { recursive: true });
  const reopened = await PresentationFile.importPptx(await FileBlob.load(FINAL_PPTX));
  for (let i = 0; i < reopened.slides.items.length; i += 1) {
    const slide = reopened.slides.items[i];
    const png = await reopened.export({ slide: slide, format: "png", scale: 1.5 });
    await writeBlob(finalPreview + "/final-" + String(i + 1).padStart(2, "0") + ".png", png);
  }
  console.log("final previews rendered");
}





