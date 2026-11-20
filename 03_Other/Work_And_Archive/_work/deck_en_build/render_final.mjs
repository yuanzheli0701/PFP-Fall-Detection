import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const ROOT = "C:/Users/13968/Documents/ChatGPT/PFP _ Fall detection";
const FINAL = ROOT + "/slides/PFP_QUIDA_CNN_LSTM_MetricLearning_EN.pptx";
const OUT = ROOT + "/_work/deck_en_build/preview/final";
await fs.mkdir(OUT, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(FINAL));
const count = presentation.slides.items.length;
for (let i = 0; i < count; i += 1) {
  const slide = presentation.slides.items[i];
  const png = await presentation.export({ slide: slide, format: "png", scale: 1.5 });
  await fs.writeFile(OUT + "/final-" + String(i + 1).padStart(2, "0") + ".png", new Uint8Array(await png.arrayBuffer()));
}
const montage = await presentation.export({ format: "webp", montage: true });
await fs.writeFile(OUT + "/montage.webp", new Uint8Array(await montage.arrayBuffer()));
console.log("rendered", count, "slides");
