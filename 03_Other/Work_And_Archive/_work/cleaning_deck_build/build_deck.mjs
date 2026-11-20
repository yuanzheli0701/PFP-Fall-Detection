import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/13968/Documents/ChatGPT/PFP _ Fall detection";
const BUILD = ROOT + "/_work/cleaning_deck_build";
const PREVIEW = BUILD + "/preview";
const FIG = ROOT + "/figures/cleaning_light";
const SKILL_DIR = "C:/Users/13968/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations";
const utils = await import(pathToFileURL(SKILL_DIR + "/container_tools/artifact_tool_utils.mjs").href);
const { makeNativeBulletParagraphs, finalizePresentation } = utils;

const FINAL_PPTX = process.env.FINAL_PPTX || ROOT + "/slides/QUIDA_Data_Cleaning_EN_WhiteBlue.pptx";
const DRAFT_PPTX = BUILD + "/draft_deck.pptx";

const BG = "#F7FBFF";
const PANEL = "#FFFFFF";
const PANEL_BLUE = "#EEF7FF";
const PANEL_BLUE_2 = "#E4F2FF";
const NAVY = "#0B1F33";
const BLUE = "#2563EB";
const SKY = "#0EA5E9";
const CYAN = "#0891B2";
const MINT = "#0F766E";
const AMBER = "#D97706";
const ROSE = "#E11D48";
const TEXT = "#122A40";
const MUTED = "#587089";
const FAINT = "#8298AD";
const BORDER = "#CBDFF0";
const BORDER_STRONG = "#A9C9E5";
const HEAD = "Bahnschrift";
const BODY = "Segoe UI";

function addText(slide, name, x, y, w, h, text, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: opts.font || BODY,
    fontSize: opts.size || 16,
    bold: opts.bold || false,
    color: opts.color || TEXT,
    alignment: opts.align || "left",
    verticalAlignment: opts.valign || "top",
    lineSpacing: opts.lineSpacing || 1.16,
    insets: 0,
    autoFit: "none",
  };
  return shape;
}

function addBullets(slide, name, x, y, w, h, items, opts = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = makeNativeBulletParagraphs(items, {
    marginLeftPoints: opts.marginLeftPoints || 16,
    hangingPoints: opts.hangingPoints || 8,
    spaceAfterPoints: opts.spaceAfter || 8,
  });
  shape.text.style = {
    typeface: opts.font || BODY,
    fontSize: opts.size || 15,
    bold: false,
    color: opts.color || MUTED,
    alignment: "left",
    verticalAlignment: "top",
    lineSpacing: opts.lineSpacing || 1.22,
    insets: 0,
    autoFit: "none",
  };
  return shape;
}

function addRect(slide, name, x, y, w, h, fill, opts = {}) {
  const config = {
    geometry: opts.geometry || "rect",
    name,
    position: { left: x, top: y, width: w, height: h, rotation: opts.rotation || 0 },
    fill,
    line: opts.line || { style: "solid", fill: "none", width: 0 },
    shadow: opts.shadow,
  };
  if (opts.radius !== undefined) config.borderRadius = opts.radius;
  if (opts.customPaths !== undefined) config.customPaths = opts.customPaths;
  return slide.shapes.add(config);
}

function addPanel(slide, name, x, y, w, h, opts = {}) {
  return addRect(slide, name, x, y, w, h, opts.fill || PANEL, {
    radius: opts.radius === undefined ? 18 : opts.radius,
    line: opts.line || { style: "solid", fill: opts.lineColor || BORDER, width: 1 },
    shadow: opts.shadow === false ? undefined : "0px 10px 28px #0B1F33/08",
  });
}

function addHLine(slide, name, x, y, w, color = BORDER, width = 1) {
  return addRect(slide, name, x, y, w, width, color);
}

function addVLine(slide, name, x, y, h, color = BORDER, width = 1) {
  return addRect(slide, name, x, y, width, h, color);
}

function addDot(slide, name, x, y, d, color) {
  return addRect(slide, name, x, y, d, d, color, { geometry: "ellipse" });
}

function addPill(slide, name, x, y, w, text, opts = {}) {
  const color = opts.color || BLUE;
  const h = opts.height || 28;
  addRect(slide, name + "-bg", x, y, w, h, opts.fill || "#F1F8FF", {
    radius: Math.round(h / 2),
    line: { style: "solid", fill: opts.lineColor || color, width: 1 },
  });
  addText(slide, name + "-text", x + 9, y + 5, w - 18, h - 7, text, {
    size: opts.size || 10.5,
    bold: true,
    color,
    font: HEAD,
    align: "center",
  });
}

async function addImage(slide, file, name, x, y, w, h, alt) {
  const bytes = await fs.readFile(file);
  const blob = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  return slide.images.add({
    blob,
    contentType: "image/png",
    name,
    alt,
    fit: "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function addNotes(slide, lines) {
  slide.speakerNotes.text = lines;
}

function addBackground(slide) {
  slide.background.fill = "linear(180deg, #FAFDFF 0%, #F4FAFF 100%)";
  addRect(slide, "ambient-glow", 790, 0, 490, 490, "radial(#0EA5E9/10 0%, #F7FBFF/0 72%)", {
    geometry: "ellipse",
  });
  addRect(slide, "top-accent", 64, 34, 18, 3, BLUE);
}

function contentSlide(kicker, title, folio, opts = {}) {
  const slide = presentation.slides.add();
  addBackground(slide);
  addText(slide, "eyebrow", 91, 28, 900, 18, kicker, {
    font: HEAD,
    size: 11,
    bold: true,
    color: BLUE,
  });
  addText(slide, "heading", 64, 58, 1120, 66, title, {
    font: HEAD,
    size: opts.titleSize || 33,
    bold: true,
    color: NAVY,
    lineSpacing: 1.04,
  });
  addText(slide, "deck-tag", 955, 31, 261, 15, "QUIDA / CLEAN DATA PIPELINE", {
    font: HEAD,
    size: 8.5,
    color: FAINT,
    align: "right",
  });
  addHLine(slide, "footer-rule", 64, 678, 1152, "#D9E7F3", 1);
  addText(slide, "footer-left", 64, 690, 650, 14, "QUIDA · data cleaning and preliminary baselines", {
    size: 9,
    color: FAINT,
  });
  addText(slide, "footer-folio", 1115, 689, 101, 15, String(folio).padStart(2, "0") + " / 13", {
    font: HEAD,
    size: 9,
    color: FAINT,
    align: "right",
  });
  return slide;
}

function waveformPath(width, height, phase = 0) {
  const commands = [];
  const n = 120;
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    const spike = 0.50 * Math.exp(-Math.pow((t - 0.55) / 0.018, 2))
      + 0.22 * Math.exp(-Math.pow((t - 0.58) / 0.035, 2));
    const noise = 0.025 * Math.sin(t * 111 + phase) + 0.018 * Math.sin(t * 247 + phase * 2.3);
    const y = height * (0.60 + 0.055 * Math.sin(t * Math.PI * 8 + phase) + noise - spike);
    commands.push(i === 0 ? { moveTo: { x: 0, y } } : { lineTo: { x: t * width, y } });
  }
  return { width, height, commands };
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// 01 - Cover
const s1 = presentation.slides.add();
s1.background.fill = "linear(135deg, #FFFFFF 0%, #F7FBFF 55%, #EAF5FF 100%)";
addRect(s1, "cover-orb-a", 0, 350, 420, 360, "radial(#2563EB/08 0%, #FFFFFF/0 72%)", { geometry: "ellipse" });
addPanel(s1, "cover-instrument", 690, 60, 526, 598, { fill: "#F3FAFF", lineColor: "#C8DFF2", radius: 26, shadow: "0px 20px 55px #2563EB/10" });
for (let i = 1; i < 12; i += 1) {
  addVLine(s1, "cover-grid-v-" + i, 690 + i * 44, 74, 570, "#DDECF9", 1);
}
for (let i = 1; i < 13; i += 1) {
  addHLine(s1, "cover-grid-h-" + i, 704, 60 + i * 44, 498, "#DDECF9", 1);
}
addRect(s1, "cover-beam", 781, 104, 344, 344, "linear(52deg, #2563EB/15 0%, #2563EB/0 72%)", {
  geometry: "custom",
  line: { style: "solid", fill: "none", width: 0 },
  customPaths: [{
    width: 344,
    height: 344,
    commands: [
      { moveTo: { x: 172, y: 172 } },
      { lineTo: { x: 172, y: 12 } },
      { lineTo: { x: 302, y: 82 } },
      { close: {} },
    ],
  }],
});
for (const [idx, radius] of [64, 106, 150, 190].entries()) {
  addRect(s1, "radar-ring-" + idx, 953 - radius, 320 - radius, radius * 2, radius * 2, "none", {
    geometry: "ellipse",
    line: { style: "solid", fill: idx === 3 ? "#2563EB/28" : "#7FB6DE/55", width: 1.1 },
  });
}
addHLine(s1, "radar-cross-h", 770, 319, 366, "#9AC7E7", 1);
addVLine(s1, "radar-cross-v", 952, 138, 362, "#9AC7E7", 1);
addDot(s1, "radar-center-ring", 942, 309, 22, "#DBEEFF");
addDot(s1, "radar-center", 948, 315, 10, BLUE);
for (const [x, y, color] of [[861, 237, CYAN], [1074, 250, AMBER], [1060, 419, ROSE], [873, 411, MINT]]) {
  addRect(s1, "sensor-node-ring", x - 12, y - 12, 24, 24, "none", {
    geometry: "ellipse",
    line: { style: "solid", fill: color + "/45", width: 1 },
  });
  addDot(s1, "sensor-node", x - 4, y - 4, 8, color);
}
addText(s1, "node-acc", 834, 185, 54, 14, "ACC", { font: HEAD, size: 9, bold: true, color: CYAN, align: "center" });
addText(s1, "node-radar", 1052, 198, 54, 14, "RADAR", { font: HEAD, size: 9, bold: true, color: AMBER, align: "center" });
addText(s1, "node-lidar", 1038, 438, 54, 14, "LiDAR", { font: HEAD, size: 9, bold: true, color: ROSE, align: "center" });
addText(s1, "node-ir", 847, 430, 54, 14, "THERMAL", { font: HEAD, size: 9, bold: true, color: MINT, align: "center" });
addText(s1, "instrument-label", 724, 96, 240, 14, "MULTI-SENSOR SIGNAL HUB", { font: HEAD, size: 9, bold: true, color: "#5E85A5" });
addText(s1, "instrument-status", 1094, 96, 92, 14, "LIVE / SYNCED", { font: HEAD, size: 8.5, color: CYAN, align: "right" });
addRect(s1, "cover-wave-glow", 760, 506, 390, 82, "none", {
  geometry: "custom",
  line: { style: "solid", fill: "#2563EB/12", width: 8 },
  customPaths: [waveformPath(390, 82, 0.8)],
});
addRect(s1, "cover-wave", 760, 506, 390, 82, "none", {
  geometry: "custom",
  line: { style: "solid", fill: BLUE, width: 2 },
  customPaths: [waveformPath(390, 82, 0.8)],
});
addHLine(s1, "instrument-bottom-rule", 724, 586, 456, "#D8E9F7", 1);
for (const [idx, label, value] of [[0, "SUBJECTS", "10"], [1, "CSV FILES", "45"], [2, "EVENTS", "100"], [3, "QA", "130/130"]]) {
  addText(s1, "instrument-stat-label-" + idx, 724 + idx * 116, 599, 96, 12, label, { font: HEAD, size: 7.5, color: FAINT });
  addText(s1, "instrument-stat-value-" + idx, 724 + idx * 116, 614, 96, 22, value, { font: HEAD, size: 17, bold: true, color: NAVY });
}
addPill(s1, "cover-kicker", 64, 76, 158, "QUIDA / PFP 2026", { color: BLUE, size: 10.5, height: 30 });
addText(s1, "cover-title", 62, 150, 575, 178, "From raw signals\nto trainable data", {
  font: HEAD,
  size: 55,
  bold: true,
  color: NAVY,
  lineSpacing: 1.10,
});
addHLine(s1, "cover-rule", 65, 360, 94, BLUE, 4);
addText(s1, "cover-subtitle", 64, 386, 575, 82, "QUIDA four-modality fall detection\nData cleaning and preliminary baselines", {
  size: 19.5,
  color: "#415B73",
  lineSpacing: 1.36,
});
addText(s1, "cover-description", 64, 494, 560, 52, "A reproducible data foundation for the next modelling phase, with every decision documented and tested.", {
  size: 13.5,
  color: MUTED,
  lineSpacing: 1.42,
});
addPill(s1, "cover-status-1", 64, 586, 146, "DATA CLEANING", { color: BLUE, height: 30 });
addPill(s1, "cover-status-2", 222, 586, 181, "PRELIMINARY TEST", { color: CYAN, height: 30 });
addText(s1, "cover-date", 64, 662, 360, 16, "4 November 2026 · QUIDA project", { font: HEAD, size: 9.5, color: FAINT });
addNotes(s1, [
  "This deck covers the data-cleaning and preliminary-test phase of the QUIDA fall-detection project.",
  "Core result: 130 fixed 10 s clips, 130/130 QA checks passed, and 396 four-second windows for baseline experiments.",
  "The right-hand instrument panel is an abstract visual, not an experiment screenshot.",
]);

function addMiniBars(slide, prefix, x, y, w, h, values, color) {
  const gap = 5;
  const barWidth = (w - gap * (values.length - 1)) / values.length;
  const maxValue = Math.max(...values);
  values.forEach((value, index) => {
    const barHeight = Math.max(5, (value / maxValue) * h);
    addRect(slide, prefix + "-bar-" + index, x + index * (barWidth + gap), y + h - barHeight, barWidth, barHeight, color + (index % 3 === 0 ? "/45" : "/78"), {
      radius: Math.min(3, barWidth / 2),
    });
  });
}

// 02 - Executive summary
const s2 = contentSlide("01 / EXECUTIVE SUMMARY", "The cleaned dataset is ready for model experiments", 2);
const kpis = [
  { value: "130", label: "10-second clips", sub: "10 subjects × 13 fixed blocks", color: BLUE },
  { value: "130/130", label: "QA checks passed", sub: "labels, masks, time axes and SHA256", color: MINT },
  { value: "396", label: "4-second windows", sub: "99 fall + 297 no-fall", color: CYAN },
  { value: "0.952 / 0.946", label: "Preliminary pooled F1", sub: "ACC 1D-CNN / RADAR LSTM", color: NAVY },
];
kpis.forEach((item, index) => {
  const x = 64 + index * 288;
  addPanel(s2, "kpi-" + index, x, 155, 270, 194);
  addRect(s2, "kpi-accent-" + index, x + 20, 155, 52, 4, item.color, { radius: 2 });
  addText(s2, "kpi-value-" + index, x + 20, 179, 230, 52, item.value, {
    font: HEAD,
    size: index === 3 ? 33 : 46,
    bold: true,
    color: item.color,
  });
  addText(s2, "kpi-label-" + index, x + 20, 242, 230, 20, item.label, {
    font: HEAD,
    size: 15,
    bold: true,
    color: NAVY,
  });
  addText(s2, "kpi-sub-" + index, x + 20, 273, 230, 48, item.sub, {
    size: 12.5,
    color: MUTED,
    lineSpacing: 1.28,
  });
});
addPanel(s2, "deliverables", 64, 377, 1152, 174, { fill: "#F0F8FF", lineColor: "#D4E7F7", shadow: false });
addText(s2, "deliverables-label", 88, 397, 220, 16, "DELIVERED IN THIS PHASE", {
  font: HEAD,
  size: 9.5,
  bold: true,
  color: BLUE,
});
const milestones = [
  ["01", "Processed data", "4-modality NPZ + metadata"],
  ["02", "Independent QA", "130 assertions + hashes"],
  ["03", "Baseline results", "10-fold leave-one-subject-out"],
  ["04", "Evidence figures", "5 plots linked to reports"],
];
milestones.forEach((item, index) => {
  const x = 88 + index * 278;
  if (index > 0) addVLine(s2, "milestone-sep-" + index, x - 20, 428, 96, "#D3E5F4", 1);
  addText(s2, "milestone-number-" + index, x, 431, 40, 22, item[0], {
    font: HEAD,
    size: 17,
    bold: true,
    color: BLUE,
  });
  addText(s2, "milestone-title-" + index, x + 43, 430, 190, 22, item[1], {
    font: HEAD,
    size: 14,
    bold: true,
    color: NAVY,
  });
  addText(s2, "milestone-text-" + index, x + 43, 458, 200, 40, item[2], {
    size: 11.5,
    color: MUTED,
    lineSpacing: 1.26,
  });
});
addRect(s2, "takeaway-bg", 64, 575, 1152, 76, "#E8F3FF", { radius: 15 });
addRect(s2, "takeaway-rule", 64, 575, 5, 76, BLUE, { radius: 2 });
addText(s2, "takeaway-label", 88, 590, 86, 16, "TAKEAWAY", {
  font: HEAD,
  size: 9.5,
  bold: true,
  color: BLUE,
});
addText(s2, "takeaway-text", 88, 611, 1080, 26, "The dataset is usable now. The high baseline scores validate the pipeline first; they are not yet a final generalisation claim.", {
  size: 15.5,
  color: NAVY,
  bold: true,
});
addNotes(s2, [
  "All four headline numbers come from the cleaned artifacts and the frozen baseline report.",
  "130/130 is a structural and semantic QA count, not a model-accuracy score.",
  "The fourth card reports pooled F1 from the preliminary LOSO run. It validates that both branches can train and evaluate end-to-end.",
]);

// 03 - Data footprint
const s3 = contentSlide("02 / DATA FOOTPRINT", "Four modalities, four different sampling rhythms", 3);
addText(s3, "footprint-subtitle", 65, 128, 1120, 24, "10 subjects  ·  45 CSV files  ·  387.95 MB of raw measurements", {
  font: HEAD,
  size: 13,
  color: MUTED,
});
const sensors = [
  {
    code: "ACC",
    name: "Accelerometer",
    rate: "62.5",
    unit: "Hz",
    rows: ["625 × 3 per 10 s clip", "3-axis inertial signal"],
    bars: [0.42, 0.55, 0.47, 0.62, 0.51, 0.70, 0.59, 0.78, 0.64, 0.82, 0.68, 0.74],
    color: BLUE,
  },
  {
    code: "RADAR",
    name: "Millimetre-wave radar",
    rate: "8.33",
    unit: "Hz",
    rows: ["7 fields per detected target", "22 aggregated frame features"],
    bars: [0.38, 0.45, 0.36, 0.58, 0.49, 0.42, 0.66, 0.54, 0.72, 0.61, 0.74, 0.69],
    color: CYAN,
  },
  {
    code: "LIDAR",
    name: "SPAD depth array",
    rate: "10.0",
    unit: "Hz",
    rows: ["512 values per frame", "8 feature blocks × 64 SPADs"],
    bars: [0.50, 0.44, 0.58, 0.53, 0.62, 0.55, 0.69, 0.63, 0.71, 0.66, 0.76, 0.72],
    color: SKY,
  },
  {
    code: "THERMAL",
    name: "Infrared camera",
    rate: "2.60",
    unit: "Hz",
    rows: ["32 × 24 temperature grid", "768 values per frame"],
    bars: [0.30, 0.34, 0.32, 0.38, 0.36, 0.41, 0.39, 0.43, 0.40, 0.46, 0.44, 0.48],
    color: AMBER,
  },
];
sensors.forEach((sensor, index) => {
  const x = 64 + index * 288;
  addPanel(s3, "sensor-" + index, x, 175, 270, 380);
  addRect(s3, "sensor-accent-" + index, x + 20, 175, 58, 4, sensor.color, { radius: 2 });
  addText(s3, "sensor-code-" + index, x + 20, 198, 220, 16, sensor.code, {
    font: HEAD,
    size: 10,
    bold: true,
    color: sensor.color,
  });
  addText(s3, "sensor-name-" + index, x + 20, 223, 220, 38, sensor.name, {
    font: HEAD,
    size: 15.5,
    bold: true,
    color: NAVY,
    lineSpacing: 1.12,
  });
  addText(s3, "sensor-rate-" + index, x + 20, 269, 150, 49, sensor.rate, {
    font: HEAD,
    size: 39,
    bold: true,
    color: sensor.color,
  });
  addText(s3, "sensor-unit-" + index, x + 170, 284, 54, 22, sensor.unit, {
    font: HEAD,
    size: 13,
    bold: true,
    color: MUTED,
  });
  addHLine(s3, "sensor-rule-" + index, x + 20, 333, 230, "#DCEAF5", 1);
  addText(s3, "sensor-row-1-" + index, x + 20, 350, 225, 22, sensor.rows[0], { size: 11.3, color: TEXT });
  addText(s3, "sensor-row-2-" + index, x + 20, 378, 225, 36, sensor.rows[1], { size: 11.3, color: MUTED, lineSpacing: 1.22 });
  addMiniBars(s3, "sensor-" + index, x + 20, 445, 230, 74, sensor.bars, sensor.color);
  addText(s3, "sensor-raw-label-" + index, x + 20, 529, 220, 12, "SCHEMATIC / SENSOR FRAME", { font: HEAD, size: 7.5, color: FAINT });
});
addRect(s3, "footprint-insight-bg", 64, 585, 1152, 66, "#E8F3FF", { radius: 14 });
addText(s3, "footprint-insight", 86, 605, 1096, 28, "Sampling rates differ by up to 24×. All modalities are therefore aligned on absolute time, never by frame index.", {
  size: 14.5,
  color: NAVY,
  bold: true,
});
addNotes(s3, [
  "The four modalities do not share a frame clock: 62.5 Hz accelerometer, 8.33 Hz radar, 10 Hz LiDAR and 2.60 Hz thermal camera.",
  "Radar rows contain seven values per detected target; we aggregate each native frame to 22 fixed features.",
  "LiDAR contributes 512 values per frame, organised as eight 64-value feature blocks.",
]);

// 04 - Synchronisation evidence
const s4 = contentSlide("03 / SYNCHRONISATION", "One fall, four rhythms: the clocks line up", 4);
addText(s4, "sync-subtitle", 65, 128, 1120, 24, "99 of 100 events pass the sync check. S3 / event 2 is the only failed event.", {
  size: 13.5,
  color: MUTED,
});
await addImage(s4, FIG + "/sensor_alignment.png", "sync-evidence", 120, 151, 1010, 503, "Four sensor traces aligned around a fall event");
addText(s4, "sync-note", 170, 658, 910, 16, "Dashed line = annotated fall. Median signed offsets: 0.34–0.72 s; P90 absolute offset ≤ 1.10 s.", {
  font: HEAD,
  size: 9.5,
  color: MUTED,
  align: "center",
});
addNotes(s4, [
  "The figure shows subject 1 / fall 1 at the same clock time across all four modalities.",
  "The fast accelerometer spike, slower radar trajectory, and sparse LiDAR and thermal samples all agree around the annotation.",
  "The S3 / event 2 mismatch is roughly ten seconds in all four modalities, so it is excluded at the event level rather than hidden by relabelling.",
]);

// 05 - Cleaning pipeline
const s5 = contentSlide("04 / CLEANING PIPELINE", "Every cleaning decision is explicit and testable", 5);
addText(s5, "pipeline-subtitle", 65, 128, 1120, 24, "Six transformations turn the raw CSVs into reproducible model inputs.", {
  size: 13.5,
  color: MUTED,
});
const pipeline = [
  ["01", "Read source files", "45 CSVs and five index tables stay untouched."],
  ["02", "Slice fixed blocks", "625 accelerometer samples = one 10 s clip."],
  ["03", "Assign labels", "Fall time → accelerometer index → fixed clip."],
  ["04", "Align clocks", "Absolute timestamps use float64 before windowing."],
  ["05", "Preserve structure", "Native masks, padded rows and empty frames stay visible."],
  ["06", "Build model inputs", "4 s windows, LOSO folds, training-only statistics."],
];
pipeline.forEach((step, index) => {
  const x = 64 + index * 191;
  addPanel(s5, "pipe-" + index, x, 176, 174, 319);
  addText(s5, "pipe-number-" + index, x + 18, 196, 48, 27, step[0], {
    font: HEAD,
    size: 22,
    bold: true,
    color: index === 5 ? CYAN : BLUE,
  });
  addVLine(s5, "pipe-rule-" + index, x + 18, 236, 36, index === 5 ? CYAN : BLUE, 3);
  addText(s5, "pipe-title-" + index, x + 18, 290, 138, 47, step[1], {
    font: HEAD,
    size: 15,
    bold: true,
    color: NAVY,
    lineSpacing: 1.10,
  });
  addText(s5, "pipe-body-" + index, x + 18, 352, 138, 112, step[2], {
    size: 11.2,
    color: MUTED,
    lineSpacing: 1.36,
  });
  if (index < 5) {
    addText(s5, "pipe-arrow-" + index, x + 176, 314, 14, 26, "›", {
      font: HEAD,
      size: 26,
      bold: true,
      color: BORDER_STRONG,
      align: "center",
    });
  }
});
addPanel(s5, "keep-panel", 64, 526, 560, 124, { fill: "#F0F8FF", lineColor: "#D5E8F7", shadow: false });
addPanel(s5, "guard-panel", 648, 526, 568, 124, { fill: "#FFF8ED", lineColor: "#F2D7AE", shadow: false });
addText(s5, "keep-title", 86, 544, 220, 16, "KEPT IN THE DATASET", { font: HEAD, size: 9.5, bold: true, color: BLUE });
addText(s5, "guard-title", 670, 544, 250, 16, "GUARDRAILS", { font: HEAD, size: 9.5, bold: true, color: AMBER });
addText(s5, "keep-copy-1", 86, 568, 505, 18, "✓  Empty radar frames as target_count = 0", { size: 11.5, color: TEXT });
addText(s5, "keep-copy-2", 86, 591, 505, 18, "✓  Padding masks and timestamps for every modality", { size: 11.5, color: TEXT });
addText(s5, "keep-copy-3", 86, 614, 505, 18, "✓  The S3 clip-8 anomaly with an explicit review flag", { size: 11.5, color: TEXT });
addText(s5, "guard-copy-1", 670, 568, 520, 18, "×  Time-gap segmentation across clip boundaries", { size: 11.5, color: TEXT });
addText(s5, "guard-copy-2", 670, 591, 520, 18, "×  Full-dataset normalisation before a split", { size: 11.5, color: TEXT });
addText(s5, "guard-copy-3", 670, 614, 520, 18, "×  Silent relabelling of S3 / event 2", { size: 11.5, color: TEXT });
addNotes(s5, [
  "The central segmentation choice is the fixed 625-sample block. It prevents a timestamp discontinuity from merging two different clips.",
  "Labels come from the original index matrix, not from a new threshold on the signals.",
  "All empty radar frames and padded rows are represented explicitly with masks, so the model can distinguish an empty observation from missing data.",
  "Normalisation statistics are computed only from the nine training subjects in each LOSO fold.",
]);

// 06 - Class structure
const s6 = contentSlide("05 / CLASS STRUCTURE", "The raw clip set is imbalanced: 99 fall vs 31 no-fall", 6);
addText(s6, "class-subtitle", 65, 128, 1120, 24, "The 4-second window builder restores a per-subject 1:3 ratio without changing the held-out protocol.", {
  size: 13.5,
  color: MUTED,
});
addText(s6, "matrix-legend-title", 90, 168, 250, 16, "CLIP MAP · 10 SUBJECTS × 13 BLOCKS", {
  font: HEAD,
  size: 9,
  bold: true,
  color: MUTED,
});
const clipPatterns = [
  "0001111111111",
  "0001111111111",
  "0001111011111",
  "0001111111111",
  "0001111111111",
  "0001111111111",
  "0001111111111",
  "0001111111111",
  "0001111111111",
  "0001111111111",
];
const matrixX = 150;
const matrixY = 199;
const cellSize = 24;
const cellGap = 6;
for (let c = 0; c < 13; c += 1) {
  addText(s6, "clip-head-" + c, matrixX + c * (cellSize + cellGap), 177, 25, 12, String(c + 1).padStart(2, "0"), {
    font: HEAD,
    size: 7.5,
    color: FAINT,
    align: "center",
  });
}
clipPatterns.forEach((pattern, row) => {
  const y = matrixY + row * 31;
  addText(s6, "subject-" + row, 94, y + 4, 42, 18, "S" + (row + 1), {
    font: HEAD,
    size: 11,
    bold: row === 2,
    color: row === 2 ? AMBER : MUTED,
  });
  pattern.split("").forEach((value, col) => {
    const isFall = value === "1";
    const isReview = row === 2 && col === 7;
    addRect(s6, "clip-" + row + "-" + col, matrixX + col * (cellSize + cellGap), y, cellSize, cellSize, isFall ? BLUE : "#DCEBFA", {
      radius: 4,
      line: isReview ? { style: "solid", fill: AMBER, width: 2 } : { style: "solid", fill: "none", width: 0 },
    });
  });
});
addRect(s6, "legend-fall", 94, 541, 13, 13, BLUE, { radius: 3 });
addText(s6, "legend-fall-text", 114, 539, 78, 16, "fall clip", { size: 10.5, color: MUTED });
addRect(s6, "legend-no-fall", 205, 541, 13, 13, "#DCEBFA", { radius: 3 });
addText(s6, "legend-no-fall-text", 225, 539, 98, 16, "no-fall clip", { size: 10.5, color: MUTED });
addRect(s6, "legend-review", 338, 541, 13, 13, "none", { radius: 3, line: { style: "solid", fill: AMBER, width: 2 } });
addText(s6, "legend-review-text", 358, 539, 138, 16, "review flag (S3 · 8)", { size: 10.5, color: MUTED });
addPanel(s6, "class-stats", 642, 172, 574, 350, { fill: "#F6FBFF", lineColor: "#D5E8F7", shadow: false });
addText(s6, "class-stats-eyebrow", 670, 194, 500, 16, "COUNTS THAT SHAPE THE TEST SET", { font: HEAD, size: 9.5, bold: true, color: BLUE });
addText(s6, "count-99", 670, 226, 190, 66, "99", { font: HEAD, size: 51, bold: true, color: BLUE });
addText(s6, "count-99-label", 670, 291, 190, 18, "fall clips", { font: HEAD, size: 13, bold: true, color: NAVY });
addText(s6, "count-31", 880, 226, 190, 66, "31", { font: HEAD, size: 51, bold: true, color: CYAN });
addText(s6, "count-31-label", 880, 291, 190, 18, "no-fall clips", { font: HEAD, size: 13, bold: true, color: NAVY });
addText(s6, "count-ratio", 1100, 243, 84, 52, "3.2:1", { font: HEAD, size: 25, bold: true, color: NAVY, align: "right" });
addHLine(s6, "class-rule", 670, 327, 514, "#D9E9F6", 1);
addText(s6, "valid-events-label", 670, 348, 220, 16, "valid fall events", { size: 11.5, color: MUTED });
addText(s6, "valid-events-value", 941, 338, 238, 30, "99 / 100", { font: HEAD, size: 22, bold: true, color: NAVY, align: "right" });
addText(s6, "windows-label", 670, 384, 220, 16, "4-second windows", { size: 11.5, color: MUTED });
addText(s6, "windows-value", 941, 374, 238, 30, "99 + 297", { font: HEAD, size: 22, bold: true, color: NAVY, align: "right" });
addText(s6, "s3-label", 670, 420, 220, 16, "S3 special case", { size: 11.5, color: MUTED });
addText(s6, "s3-value", 941, 410, 238, 30, "9 fall + 4 no-fall", { font: HEAD, size: 18, bold: true, color: AMBER, align: "right" });
addText(s6, "class-callout", 670, 463, 514, 37, "Two S3 falls land in one fixed block; clip 8 has no valid index and stays review-flagged.", {
  size: 11.5,
  color: MUTED,
  lineSpacing: 1.30,
});
addRect(s6, "class-takeaway-bg", 64, 584, 1152, 67, "#E8F3FF", { radius: 14 });
addText(s6, "class-takeaway", 86, 604, 1100, 28, "No silent relabelling: S3 / event 2 is excluded at event level, while clip 4 remains positive because it contains event 1.", {
  size: 14.5,
  color: NAVY,
  bold: true,
});
addNotes(s6, [
  "The matrix uses the actual fixed-block labels, not a schematic ordering.",
  "Most subjects have three no-fall and ten fall clips; S3 has four no-fall and nine fall clips because one fall has no valid index.",
  "The 4-second window set restores 1:3 sampling independently for each subject, yielding 99 positive and 297 negative windows.",
]);

// 07 - Anomalies
const s7 = contentSlide("06 / DATA ANOMALIES", "Three edge cases are handled explicitly, not averaged away", 7);
addText(s7, "anomaly-subtitle", 65, 128, 1120, 24, "The fixed-block rule protects clip integrity when file order or timestamps disagree.", {
  size: 13.5,
  color: MUTED,
});
await addImage(s7, FIG + "/anomaly_order.png", "anomaly-order", 170, 153, 940, 305, "Subject 8 clip timestamps reveal three out-of-order clips");
const anomalies = [
  {
    code: "S8 · ORDER",
    title: "Clips 9–11 jump backwards",
    text: "Fixed 625-sample blocks preserve each clip. Labels come from the original index matrix, not file order.",
    color: BLUE,
  },
  {
    code: "S3 · EVENT 2",
    title: "About 10 s of offset",
    text: "All four modalities disagree with falls.csv. The event is marked invalid; clip 4 remains fall because event 1 is valid.",
    color: AMBER,
  },
  {
    code: "RADAR · EMPTY",
    title: "1,377 empty native frames",
    text: "3.74% of 36,838 raw frames contain no target. They stay in the data as target_count = 0, empty_frame = 1.",
    color: CYAN,
  },
];
anomalies.forEach((item, index) => {
  const x = 64 + index * 392;
  addPanel(s7, "anomaly-card-" + index, x, 482, 368, 169);
  addRect(s7, "anomaly-rule-" + index, x + 20, 482, 58, 4, item.color, { radius: 2 });
  addText(s7, "anomaly-code-" + index, x + 20, 503, 310, 16, item.code, { font: HEAD, size: 9.5, bold: true, color: item.color });
  addText(s7, "anomaly-title-" + index, x + 20, 528, 320, 24, item.title, { font: HEAD, size: 14.5, bold: true, color: NAVY });
  addText(s7, "anomaly-text-" + index, x + 20, 558, 320, 76, item.text, { size: 11.3, color: MUTED, lineSpacing: 1.31 });
});
addNotes(s7, [
  "S8 clips 9–11 have timestamps earlier than clip 8. A time-gap split would merge clips or assign the wrong label; fixed blocks avoid both.",
  "S3 / event 2 is the only sync failure. It is manually invalidated for event-level windows, while clip 4 is not reassigned because it still contains a valid event.",
  "Empty radar frames are real observations of an absent target. Dropping them would change the time series and hide sensor limitations.",
]);

// 08 - 4-second windows
const s8 = contentSlide("07 / WINDOW PROTOCOL", "Four-second windows, centred on the fall with a two-second guard", 8, { titleSize: 31 });
addText(s8, "window-subtitle", 65, 127, 1120, 24, "Positive windows are anchored to valid events. Negative windows must stay outside the event buffer.", {
  size: 13.5,
  color: MUTED,
});
addText(s8, "timeline-label-left", 90, 178, 220, 16, "10 s SOURCE CLIP", { font: HEAD, size: 9, bold: true, color: MUTED });
addText(s8, "timeline-label-right", 948, 178, 242, 16, "SIGNAL TIME", { font: HEAD, size: 9, bold: true, color: MUTED, align: "right" });
addRect(s8, "timeline-track", 90, 220, 1100, 48, "#E7F2FB", { radius: 12 });
for (let i = 0; i <= 10; i += 1) {
  addVLine(s8, "timeline-tick-" + i, 90 + i * 110, 220, 48, i === 5 ? "#8BB8D8" : "#D3E7F6", 1);
}
addRect(s8, "positive-window", 420, 220, 440, 48, "#BFE0FF", { radius: 10, line: { style: "solid", fill: BLUE, width: 2 } });
addText(s8, "positive-window-label", 444, 235, 392, 18, "4 s positive window   ·   250 samples", { font: HEAD, size: 11.5, bold: true, color: BLUE, align: "center" });
addVLine(s8, "event-line", 639, 202, 86, AMBER, 2);
addDot(s8, "event-dot", 632, 237, 15, AMBER);
addText(s8, "event-label", 664, 198, 150, 20, "fall event  t = 0", { font: HEAD, size: 10, bold: true, color: AMBER });
for (const [pos, label] of [[90, "-5 s"], [310, "-3 s"], [530, "-1 s"], [640, "0"], [750, "+1 s"], [970, "+3 s"], [1190, "+5 s"]]) {
  addText(s8, "tick-label-" + pos, pos - 34, 279, 68, 15, label, { font: HEAD, size: 8.5, color: MUTED, align: "center" });
}
addText(s8, "guard-label", 420, 307, 440, 16, "2 s guard on each side", { font: HEAD, size: 9.5, color: AMBER, align: "center" });
addText(s8, "negative-note", 970, 331, 228, 38, "Negative windows must not intersect the guard.", { size: 10.5, color: MUTED, lineSpacing: 1.25, align: "right" });
const windowCards = [
  ["396", "total windows", "99 fall + 297 no-fall", BLUE],
  ["1:3", "per-subject ratio", "S3 contributes 9 + 27", CYAN],
  ["10", "LOSO folds", "all statistics use training subjects only", MINT],
];
windowCards.forEach((item, index) => {
  const x = 64 + index * 392;
  addPanel(s8, "window-card-" + index, x, 382, 368, 222);
  addText(s8, "window-card-value-" + index, x + 24, 402, 138, 62, item[0], { font: HEAD, size: 43, bold: true, color: item[3] });
  addText(s8, "window-card-label-" + index, x + 24, 466, 190, 20, item[1], { font: HEAD, size: 14, bold: true, color: NAVY });
  addText(s8, "window-card-copy-" + index, x + 24, 500, 310, 52, item[2], { size: 11.5, color: MUTED, lineSpacing: 1.31 });
  addHLine(s8, "window-card-rule-" + index, x + 24, 564, 318, "#D9E9F6", 1);
  addText(s8, "window-card-shape-" + index, x + 24, 575, 310, 14, index === 1 ? "4 s window · fixed stride 0.5 s" : "shape · ACC 250 × 3 / RADAR 42 × 22", {
    font: HEAD,
    size: 8,
    color: FAINT,
  });
});
addRect(s8, "window-footer-bg", 64, 622, 1152, 36, "#E8F3FF", { radius: 10 });
addText(s8, "window-footer-text", 84, 633, 1112, 16, "No subject appears on both sides of a fold: every window from a held-out subject stays in that test fold.", {
  size: 11.5,
  color: NAVY,
  bold: true,
});
addNotes(s8, [
  "A 4-second window contains 250 accelerometer samples at 62.5 Hz.",
  "Positive windows are centred on a valid fall event, with two seconds before and after the anchor.",
  "Negative candidates are rejected when a window intersects a two-second buffer around any valid event.",
  "Sampling is 1:3 within each subject. S3 therefore has nine positives and twenty-seven negatives.",
  "Leave-one-subject-out keeps every window from the held-out subject out of training. Normalisation uses the nine training subjects only.",
]);

// 09 - Baseline models
const s9 = contentSlide("08 / BASELINE MODELS", "Two small baselines test the full learning path", 9, { titleSize: 31 });
addText(s9, "models-subtitle", 65, 127, 1120, 24, "The models stay deliberately simple: this phase checks shapes, training, prediction and reporting.", {
  size: 13.5,
  color: MUTED,
});
function addArchBox(slide, prefix, x, y, w, h, title, detail, color, active = false) {
  addPanel(slide, prefix, x, y, w, h, {
    fill: active ? "#EFF7FF" : "#FFFFFF",
    lineColor: active ? color + "/70" : "#D8E8F5",
    radius: 10,
    shadow: false,
  });
  addText(slide, prefix + "-title", x + 14, y + 8, w - 28, 16, title, { font: HEAD, size: 10.5, bold: true, color: active ? color : NAVY });
  if (detail) addText(slide, prefix + "-detail", x + 14, y + 25, w - 28, 12, detail, { size: 8.6, color: MUTED });
}
const branchPanels = [
  {
    x: 64,
    title: "ACC · 1D-CNN",
    subtitle: "Raw 3-axis signal → temporal feature extractor",
    color: BLUE,
    boxes: [
      ["Input", "250 time steps × 3 channels"],
      ["Conv1D · 16 filters", "kernel 5 · BatchNorm · ReLU · pool 2"],
      ["Conv1D · 32 filters", "kernel 5 · BatchNorm · ReLU · pool 2"],
      ["Conv1D · 64 filters", "kernel 3 · BatchNorm · ReLU"],
      ["Global average pool → Linear 2", "64 → 2 logits"],
    ],
    score: "0.952",
    scoreLabel: "pooled F1",
  },
  {
    x: 656,
    title: "RADAR · LSTM",
    subtitle: "22 frame features → sequence encoder",
    color: CYAN,
    boxes: [
      ["Input", "42 frames × 22 features + frame mask"],
      ["Packed LSTM · hidden 32", "variable native frame count per window"],
      ["Dropout · 0.30", "regularisation on the final hidden state"],
      ["Last hidden state", "sequence summary · 32 values"],
      ["Linear 2", "32 → 2 logits · fall vs no-fall"],
    ],
    score: "0.946",
    scoreLabel: "pooled F1",
  },
];
branchPanels.forEach((branch, branchIndex) => {
  addPanel(s9, "branch-" + branchIndex, branch.x, 167, 560, 433);
  addPill(s9, "branch-pill-" + branchIndex, branch.x + 24, 188, branchIndex === 0 ? 112 : 126, branch.title, { color: branch.color, size: 9.5, height: 27 });
  addText(s9, "branch-subtitle-" + branchIndex, branch.x + 24, 227, 510, 20, branch.subtitle, { size: 11.5, color: MUTED });
  branch.boxes.forEach((box, index) => {
    const y = 262 + index * 51;
    addArchBox(s9, "arch-" + branchIndex + "-" + index, branch.x + 34, y, 492, 39, box[0], box[1], branch.color, index === 0);
    if (index < branch.boxes.length - 1) {
      addVLine(s9, "arch-link-" + branchIndex + "-" + index, branch.x + 279, y + 39, 12, branch.color + "/45", 1.5);
    }
  });
  addHLine(s9, "branch-score-rule-" + branchIndex, branch.x + 24, 530, 512, "#DCEAF6", 1);
  addText(s9, "branch-score-" + branchIndex, branch.x + 24, 546, 170, 42, branch.score, { font: HEAD, size: 27, bold: true, color: branch.color });
  addText(s9, "branch-score-label-" + branchIndex, branch.x + 126, 553, 160, 18, branch.scoreLabel, { font: HEAD, size: 10.5, bold: true, color: NAVY });
  addText(s9, "branch-score-note-" + branchIndex, branch.x + 300, 553, 238, 26, branchIndex === 0 ? "386 / 396 pooled windows correct" : "385 / 396 pooled windows correct", { size: 9.5, color: MUTED, align: "right" });
});
addRect(s9, "training-config-bg", 64, 619, 1152, 40, "#E8F3FF", { radius: 10 });
addText(s9, "training-config", 86, 630, 1108, 18, "Training protocol   Adam · lr 1e-3 · weight decay 1e-4 · batch 32 · 45 epochs · seed 2026 · CPU", {
  font: HEAD,
  size: 10.5,
  bold: true,
  color: NAVY,
});
addNotes(s9, [
  "The accelerometer branch is a compact 1D-CNN over 250 samples and three axes.",
  "The radar branch consumes 42 frame-level feature vectors and uses a packed LSTM so native sequence lengths remain valid.",
  "Both branches use the same ten LOSO folds and the same reporting code. Architecture tuning is deliberately out of scope for this phase.",
  "The training protocol is Adam at 1e-3, batch size 32, 45 epochs and seed 2026.",
]);

// 10 - Results
const s10 = contentSlide("09 / PRELIMINARY RESULTS", "The baseline runs end to end; fall recall is the strongest signal", 10, { titleSize: 30 });
addText(s10, "results-subtitle", 65, 126, 1120, 24, "Pooled metrics over 396 held-out windows from ten unseen subjects.", {
  size: 13.5,
  color: MUTED,
});
await addImage(s10, FIG + "/model_metrics.png", "metrics-evidence", 64, 154, 780, 390, "Preliminary pooled metrics for accelerometer and radar baselines");
const resultCards = [
  { name: "ACC · 1D-CNN", f1: "0.952", color: BLUE, line1: "Recall 1.000  ·  Specificity 0.966", line2: "FP 10   ·   FN 0   ·   AUROC 0.995" },
  { name: "RADAR · LSTM", f1: "0.946", color: CYAN, line1: "Recall 0.970  ·  Specificity 0.973", line2: "FP 8   ·   FN 3   ·   AUROC 0.988" },
];
resultCards.forEach((item, index) => {
  const y = 154 + index * 207;
  addPanel(s10, "result-card-" + index, 868, y, 348, 190);
  addText(s10, "result-name-" + index, 890, y + 20, 300, 18, item.name, { font: HEAD, size: 11, bold: true, color: item.color });
  addText(s10, "result-f1-" + index, 890, y + 48, 105, 57, item.f1, { font: HEAD, size: 45, bold: true, color: item.color });
  addText(s10, "result-f1-label-" + index, 1002, y + 65, 190, 18, "pooled F1", { font: HEAD, size: 11, bold: true, color: NAVY });
  addText(s10, "result-line-1-" + index, 890, y + 116, 300, 17, item.line1, { size: 10.8, color: MUTED });
  addText(s10, "result-line-2-" + index, 890, y + 140, 300, 17, item.line2, { size: 10.8, color: MUTED });
  addHLine(s10, "result-rule-" + index, 890, y + 166, 298, "#DCEAF6", 1);
  addText(s10, "result-note-" + index, 890, y + 172, 298, 12, "balanced view: fall vs no-fall", { font: HEAD, size: 8, color: FAINT });
});
addRect(s10, "results-caveat-bg", 64, 576, 1152, 77, "#FFF7EA", { radius: 14, line: { style: "solid", fill: "#F0D3A3", width: 1 } });
addRect(s10, "results-caveat-rule", 64, 576, 5, 77, AMBER, { radius: 2 });
addText(s10, "results-caveat-label", 88, 590, 100, 15, "CAUTION", { font: HEAD, size: 9.5, bold: true, color: AMBER });
addText(s10, "results-caveat-text", 88, 611, 1090, 28, "The current negatives come mainly from limited walking activity. These scores validate the pipeline and may be optimistic; they are not a final generalisation claim.", {
  size: 14,
  color: NAVY,
  bold: true,
});
addNotes(s10, [
  "The pooled scores aggregate predictions from ten held-out folds, covering 396 windows.",
  "The accelerometer CNN recalls every fall but produces ten false positives. The radar LSTM produces eight false positives and misses three falls.",
  "Both AUROC values are above 0.98, but the class balance and limited activity set make these numbers look easier than a real deployment.",
  "This is a pipeline-validation result, not the final supervised-versus-metric-learning comparison.",
]);

// 11 - Error analysis
const s11 = contentSlide("10 / ERROR ANALYSIS", "S3 and S8 carry most of the remaining errors", 11, { titleSize: 32 });
addText(s11, "errors-subtitle", 65, 126, 1120, 24, "Six of ten folds reach F1 = 1.000, which is itself a warning that the negative task is still easy.", {
  size: 13.5,
  color: MUTED,
});
await addImage(s11, FIG + "/subject_f1.png", "subject-f1-evidence", 140, 151, 1000, 394, "Per-subject F1 for accelerometer and radar baselines");
const errorCards = [
  ["S3", "F1 0.783", "5 false positives · 0 false negatives · both models", ROSE],
  ["S8", "F1 0.870", "3 false positives · 0 false negatives · both models", AMBER],
  ["RADAR miss", "3 FN", "All radar misses occur on held-out S1 and S2", CYAN],
];
errorCards.forEach((item, index) => {
  const x = 64 + index * 392;
  addPanel(s11, "error-card-" + index, x, 558, 368, 93, { radius: 14, shadow: false });
  addRect(s11, "error-rule-" + index, x + 18, 558, 45, 4, item[3], { radius: 2 });
  addText(s11, "error-subject-" + index, x + 18, 574, 120, 18, item[0], { font: HEAD, size: 10, bold: true, color: item[3] });
  addText(s11, "error-value-" + index, x + 18, 595, 130, 27, item[1], { font: HEAD, size: 20, bold: true, color: NAVY });
  addText(s11, "error-copy-" + index, x + 148, 589, 200, 46, item[2], { size: 9.7, color: MUTED, lineSpacing: 1.24 });
});
addNotes(s11, [
  "The per-subject curves show that most held-out folds are already at F1 = 1.000.",
  "S3 and S8 expose the remaining false positives. Both branches agree on these two difficult folds.",
  "Radar additionally misses three fall windows, all when S1 or S2 is held out.",
  "Saturation is useful diagnostically: the negative distribution is too easy and must be hardened before any strong performance claim.",
]);

// 12 - Interpretation and next steps
const s12 = contentSlide("11 / INTERPRETATION", "The data foundation is solid; the performance claim needs a harder test", 12, { titleSize: 29 });
addPanel(s12, "support-panel", 64, 151, 560, 236, { fill: "#F2F9FF", lineColor: "#D5E8F7", shadow: false });
addPanel(s12, "open-panel", 656, 151, 560, 236, { fill: "#FFF8ED", lineColor: "#F0D8B4", shadow: false });
addText(s12, "support-title", 88, 172, 480, 20, "WHAT WE CAN SUPPORT", { font: HEAD, size: 9.5, bold: true, color: BLUE });
addText(s12, "open-title", 680, 172, 480, 20, "WHAT REMAINS OPEN", { font: HEAD, size: 9.5, bold: true, color: AMBER });
const supportItems = [
  "The cleaned dataset is reproducible and internally consistent.",
  "Labels, validity flags and review cases are traceable.",
  "LOSO isolation, masks and time axes pass 130 checks.",
];
supportItems.forEach((item, index) => {
  addText(s12, "support-index-" + index, 88, 207 + index * 47, 28, 16, String(index + 1).padStart(2, "0"), {
    font: HEAD,
    size: 9,
    bold: true,
    color: BLUE,
  });
  addText(s12, "support-item-" + index, 121, 202 + index * 47, 475, 28, item, {
    size: 13.2,
    color: TEXT,
  });
});
const openItems = [
  "Six of ten test folds are already saturated.",
  "Only 100 events from ten subjects limit external validity.",
  "These baselines are not the final model comparison.",
];
openItems.forEach((item, index) => {
  addText(s12, "open-index-" + index, 680, 207 + index * 47, 28, 16, String(index + 1).padStart(2, "0"), {
    font: HEAD,
    size: 9,
    bold: true,
    color: AMBER,
  });
  addText(s12, "open-item-" + index, 713, 202 + index * 47, 478, 28, item, {
    size: 13.2,
    color: TEXT,
  });
});
addText(s12, "roadmap-title", 65, 410, 420, 17, "NEXT EXPERIMENTS", { font: HEAD, size: 9.5, bold: true, color: BLUE });
const roadmap = [
  ["01", "Hard negatives", "Add sitting, bending, lying down and abrupt non-fall motion."],
  ["02", "Metric learning", "Use P×K batches with contrastive or triplet objectives."],
  ["03", "Sensor fusion", "Start with accelerometer + radar, then test LiDAR and thermal."],
  ["04", "Final benchmark", "Freeze folds, metrics and a paper-compatible protocol."],
];
roadmap.forEach((item, index) => {
  const x = 64 + index * 294;
  addPanel(s12, "roadmap-" + index, x, 438, 270, 211);
  addText(s12, "roadmap-number-" + index, x + 20, 456, 40, 27, item[0], { font: HEAD, size: 20, bold: true, color: index === 3 ? MINT : BLUE });
  addText(s12, "roadmap-step-" + index, x + 20, 493, 222, 24, item[1], { font: HEAD, size: 15, bold: true, color: NAVY });
  addText(s12, "roadmap-copy-" + index, x + 20, 526, 222, 89, item[2], { size: 11.4, color: MUTED, lineSpacing: 1.35 });
  if (index < 3) addText(s12, "roadmap-arrow-" + index, x + 272, 526, 20, 26, "›", { font: HEAD, size: 24, bold: true, color: BORDER_STRONG, align: "center" });
});
addNotes(s12, [
  "The cleaning result is supportable now: it is reproducible, traceable and independently checked.",
  "The performance result is not ready to be presented as final. The saturated folds point to an easy negative set, not to a solved deployment problem.",
  "The next sequence is hard negatives, metric learning, sensor fusion, then a frozen final benchmark.",
]);

// 13 - Backup schema
const s13 = contentSlide("BACKUP / REPRODUCIBILITY", "Schemas, artifacts and reproduction commands", 13, { titleSize: 32 });
addText(s13, "backup-subtitle", 65, 126, 1120, 24, "Every number in this deck can be regenerated from the scripts provided in the repository.", {
  size: 13.5,
  color: MUTED,
});
const schemaRows = [
  ["File", "Array", "Shape", "Role"],
  ["quida_clean.npz", "acc", "(130, 625, 3)", "10 s accelerometer clips"],
  ["quida_clean.npz", "radar", "(130, 90, 22)", "frame features + mask"],
  ["quida_clean.npz", "lidar", "(130, 105, 512)", "depth frames + mask"],
  ["quida_clean.npz", "ir", "(130, 40, 768)", "thermal frames + mask"],
  ["quida_windows_4s.npz", "acc", "(396, 250, 3)", "4 s model input"],
  ["quida_windows_4s.npz", "radar", "(396, 42, 22)", "4 s model input"],
  ["splits_loso.npz", "10 folds", "train / test", "fold-safe normalisation"],
];
const table = s13.tables.add({
  rows: 8,
  columns: 4,
  left: 64,
  top: 157,
  width: 700,
  height: 385,
  values: schemaRows,
  columnWidths: [160, 88, 133, 319],
});
table.borders.assign({ style: "solid", fill: "#D3E5F4", width: 1 });
table.styleOptions = { headerRow: true, bandedRows: false, firstColumn: false };
for (let row = 0; row < 8; row += 1) {
  for (let col = 0; col < 4; col += 1) {
    const cell = table.getCell(row, col);
    cell.fill = row === 0 ? BLUE : (row % 2 === 0 ? "#F2F9FF" : "#FFFFFF");
    cell.text.style = {
      typeface: col === 2 ? "Consolas" : BODY,
      fontSize: row === 0 ? 9.2 : 9.4,
      bold: row === 0 || col === 0,
      color: row === 0 ? "#FFFFFF" : (col === 0 ? NAVY : TEXT),
    };
  }
}
addPanel(s13, "code-panel", 788, 157, 428, 385, { fill: "#F0F7FE", lineColor: "#D4E7F7", shadow: false });
addText(s13, "code-title", 810, 178, 384, 16, "REPRODUCE FROM THE ROOT", { font: HEAD, size: 9.2, bold: true, color: BLUE });
addText(s13, "code-lines-1", 810, 210, 384, 115, [
  "D:\\Anaconda\\python.exe scripts\\",
  "  build_clean_dataset.py --overwrite",
  "D:\\Anaconda\\python.exe scripts\\",
  "  verify_clean_dataset.py",
  "D:\\Anaconda\\python.exe scripts\\",
  "  train_preliminary_baselines.py",
].join("\n"), { font: "Consolas", size: 9.6, color: "#173A5B", lineSpacing: 1.40 });
addHLine(s13, "code-rule", 810, 338, 384, "#CFE2F1", 1);
addText(s13, "code-output-title", 810, 352, 384, 14, "VERIFIED OUTPUT", { font: HEAD, size: 8.4, bold: true, color: MUTED });
addText(s13, "code-output", 810, 376, 384, 86, "PASS: 130 checks passed, 0 failed\n396 windows: 99 fall / 297 no-fall\n10 LOSO folds · 0 subject leakage", {
  font: "Consolas",
  size: 9.7,
  color: "#0F766E",
  lineSpacing: 1.45,
});
addText(s13, "code-figures", 810, 479, 384, 36, "Figures:  D:\\Anaconda\\python.exe scripts\\make_cleaning_figures.py --theme light", {
  font: "Consolas",
  size: 8.0,
  color: MUTED,
  lineSpacing: 1.30,
});
addPanel(s13, "audit-strip", 64, 568, 1152, 82, { fill: "#E8F3FF", lineColor: "#D6E8F7", shadow: false });
addText(s13, "audit-title", 86, 584, 190, 14, "AUDIT TRAIL", { font: HEAD, size: 8.8, bold: true, color: BLUE });
addText(s13, "audit-text", 86, 606, 1100, 30, "QA report  data_processed/qa_report.json  ·  data card  data_processed/data_card.md  ·  baselines  reports/preliminary_baselines.json  ·  manifest  data_processed/manifest.json", {
  font: HEAD,
  size: 9.2,
  color: NAVY,
});
addNotes(s13, [
  "This backup slide records the exact array shapes and the three commands that rebuild the data, verify it, and reproduce the baselines.",
  "The QA report is generated by verify_clean_dataset.py and checks 130 conditions, including manifest hashes.",
  "The light-theme figures were regenerated from the same scripts with --theme light.",
]);

// Export draft previews and PPTX
async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

await fs.mkdir(PREVIEW, { recursive: true });
await fs.mkdir(BUILD + "/.codex-finalizer", { recursive: true });
for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const slide = presentation.slides.items[index];
  const png = await presentation.export({ slide, format: "png", scale: 1.5 });
  await writeBlob(PREVIEW + "/draft-" + String(index + 1).padStart(2, "0") + ".png", png);
}
const draftFile = await PresentationFile.exportPptx(presentation);
await draftFile.save(DRAFT_PPTX);
const montage = await presentation.export({ format: "webp", montage: true, scale: 0.75 });
await writeBlob(PREVIEW + "/draft-montage.webp", montage);
console.log("draft:", DRAFT_PPTX, "slides:", presentation.slides.items.length);

// Optional finalization
if (process.argv.includes("--finalize")) {
  const staging = BUILD + "/.codex-finalizer";
  await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
  const candidatePath = staging + "/candidate.pptx";
  await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
  const result = await finalizePresentation({
    explicitTotalSlideCount: 13,
    requiredNativeTableOwnerSlides: [13],
    requiredNativeChartOwnerSlides: [],
    workspaceDir: ROOT,
    candidatePath,
    finalPath: FINAL_PPTX,
    pythonExecutable: "C:/Users/13968/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
    integrityValidatorPath: SKILL_DIR + "/container_tools/inspect_presentation_package_integrity.py",
    layoutValidatorPath: SKILL_DIR + "/container_tools/inspect_presentation_layout_geometry.py",
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry",
      "--validate-heading-fit",
      "--require-native-table-slide", "13",
    ],
    requiredNativeTableOwnerSlides: [13],
    fontPolicy: { basis: "design", families: ["Bahnschrift", "Segoe UI", "Consolas"] },
    verifyArtifactToolImport: true,
    receiptPath: staging + "/final.validation.json",
  });
  console.log("finalized:", JSON.stringify(result, null, 2));
  const finalPreview = PREVIEW + "/final";
  await fs.mkdir(finalPreview, { recursive: true });
  const reopened = await PresentationFile.importPptx(await FileBlob.load(FINAL_PPTX));
  for (let index = 0; index < reopened.slides.items.length; index += 1) {
    const slide = reopened.slides.items[index];
    const png = await reopened.export({ slide, format: "png", scale: 1.5 });
    await writeBlob(finalPreview + "/final-" + String(index + 1).padStart(2, "0") + ".png", png);
  }
  const finalMontage = await reopened.export({ format: "webp", montage: true, scale: 0.75 });
  await writeBlob(finalPreview + "/montage.webp", finalMontage);
  console.log("final previews rendered:", finalPreview);
}




