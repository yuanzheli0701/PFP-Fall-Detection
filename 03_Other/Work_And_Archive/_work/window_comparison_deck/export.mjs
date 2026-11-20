import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root='C:/Users/13968/Documents/ChatGPT/PFP _ Fall detection';
const build=root+'/03_Other/Work_And_Archive/_work/window_comparison_deck';
const skill='C:/Users/13968/.codex/plugins/cache/openai-primary-runtime/presentations/26.1116.12020/skills/presentations';
const runtime='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1116-1220-0_26.1116.1220.0_x64__3k8sg7r9htsxt/dependencies';
const p=Presentation.load(JSON.parse(await fs.readFile(build+'/presentation.json','utf8')));
const candidate=build+'/candidate.pptx';
await(await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const final=root+'/01_Reports_and_Presentation/Current/QUIDA_Window_CNN_LSTM_Progress_EN_2026-11-17.pptx';
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 pythonExecutable:runtime+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',
 ...[2,5,6,8,10].flatMap(n=>['--require-native-table-slide',String(n)])],
 explicitTotalSlideCount:14,requiredNativeTableOwnerSlides:[2,5,6,8,10],
 requiredNativeChartOwnerSlides:[3,4,9,11],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:['Segoe UI']},verifyArtifactToolImport:true,
 receiptPath:build+'/validation.json'});
console.log(JSON.stringify({final,result}));
