const F='Segoe UI', INK='#142D4E', BLUE='#2165C5', TEAL='#168A88', GRAY='#52657D', LIGHT='#E9F1FB';
const names=['acc_cnn','acc_lstm','radar_cnn','radar_lstm'];
const labels=['ACC CNN','ACC LSTM','Radar CNN','Radar LSTM'];
const source='02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/';
const pct=x=>(x*100).toFixed(2)+'%';
const dec=x=>x.toFixed(4);

function text(s,t,x,y,w,h,size=22,color=INK,bold=false){
  const sh=s.shapes.add({geometry:'textbox',name:t.slice(0,45),position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=t;
  sh.text.style={typeface:F,fontSize:size+'pt',bold,color,verticalAlignment:'top',alignment:'left',insets:0,autoFit:'none'};
  return sh;
}
function slide(p,title,subtitle,notes){
  const s=p.slides.add(); s.size={width:1280,height:720}; s.background.fill='#FFFFFF';
  text(s,title,64,45,1152,76,34,INK,true);
  if(subtitle)text(s,subtitle,66,125,1144,58,18,GRAY);
  text(s,'QUIDA fall detection',66,675,700,23,11,GRAY);
  text(s,String(p.slides.items.length).padStart(2,'0'),1170,670,50,28,13,BLUE,true);
  s.speakerNotes.text=notes;
  return s;
}
function table(s,values,x,y,w,h,widths,size=20){
  const tb=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,columnWidths:widths});
  tb.borders.assign({fill:'#D4E0EF',width:1,style:'solid'});
  for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
    const cell=tb.getCell(r,c);cell.fill=r===0?INK:(r%2?'#FFFFFF':'#F3F7FC');
    cell.text.style={typeface:F,fontSize:size+'pt',bold:r===0,color:r===0?'#FFFFFF':INK};
  }
  return tb;
}
function item(s,num,title,detail,y){
  text(s,String(num).padStart(2,'0'),66,y,78,54,28,BLUE,true);
  text(s,title,158,y,1040,42,24,INK,true);
  text(s,detail,158,y+47,1020,62,19,GRAY);
}
const chartText={typeface:F,fontSize:21,fill:GRAY};
function bars(s,categories,series,pos,{max=1,format='0%',legend=false,labels=true}={}){
 return s.charts.add('bar',{position:pos,categories,series:series.map(s=>({...s,values:s.values.map(v=>Number(v.toFixed(6)))})),barOptions:{direction:'column',grouping:'clustered',gapWidth:105},hasLegend:legend,
 legend:{position:'bottom',overlay:false,textStyle:{...chartText,fontSize:21}},
 chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},
 xAxis:{textStyle:chartText,majorGridlines:null,line:{fill:'#CCD9E9',width:1}},
 yAxis:{min:0,max,majorUnit:max===1?.2:undefined,numberFormatCode:format,textStyle:chartText,majorGridlines:{fill:'#DCE6F2',width:1}},
 dataLabels:{showValue:labels,position:'outEnd',numberFormatCode:format,textStyle:{typeface:F,fontSize:21,fill:INK,bold:true}}});
}

export function build(p,d){
 if(p.slides.items.length)p.slides.delete(p.slides.items.map(s=>s.id));
 p.theme.defaultFont=F;
 let s=slide(p,'','','');
 text(s,'PFP PROJECT PROGRESS',68,74,1100,42,17,BLUE,true);
 text(s,'Fall detection with\nCNN and LSTM',66,194,1120,190,48,INK,true);
 text(s,'A comparison on accelerometer and radar windows',68,425,1110,65,25,GRAY);
 text(s,'QUIDA dataset\n17 November 2026',68,551,1000,77,18,GRAY);
 s.speakerNotes.text='Today we present the experiment completed after the previous review. We now apply both CNN and LSTM to both sensors. Our main experiment predicts fall versus no fall from randomly mixed four-second windows. We retain leave-one-subject-out evaluation as a supplementary experiment. We will explain the protocol, compare the results and present the next experiments. Sources: '+source+'FOUR_MODEL_PROTOCOL.md and results/four_model_comparison/{window,loso}/summary.json.';

 s=slide(p,'What we completed','The comparison now separates the effect of the model from the effect of the sensor.',
 'Previously, we had one accelerometer CNN and one radar LSTM. That comparison changed the sensor and architecture together. We have now completed all four sensor-model combinations using shared splits. We also completed a window-based protocol and kept LOSO as a supplementary evaluation. Sixty trained models support these two current protocols: twenty for random windows and forty for LOSO. The earlier grouped-window experiment remains archived. Source: '+source+'results/four_model_comparison/window/summary.json and loso/summary.json.');
 table(s,[['Sensor','CNN','LSTM'],['Accelerometer','Completed','Completed'],['Radar','Completed','Completed']],66,213,1148,233,[428,360,360],25);
 text(s,'20',72,498,220,76,44,BLUE,true);text(s,'main-experiment models',72,580,490,43,20,GRAY);
 text(s,'40',678,498,220,76,44,TEAL,true);text(s,'supplementary LOSO models',678,580,530,43,20,GRAY);

 s=slide(p,'Data preparation','We reused the cleaned dataset and its existing fall annotations.',
 'The dataset covers ten subjects and 130 fixed ten-second clips. Cleaning preserves raw files, aligns sensor data on absolute timestamps and handles invalid annotations and radar padding explicitly. There are 99 valid fall events. The processed window dataset contains 99 fall and 297 no-fall windows. The cleaning verifier passed 130 checks with no failures. Other modalities are stored, but this comparison uses only the accelerometer and radar. Sources: '+source+'data_processed/dataset_metadata.json, qa_report.json and code/build_clean_dataset.py.');
 text(s,'396',70,214,520,120,66,BLUE,true);text(s,'four-second windows',72,342,510,55,27,INK,true);
 text(s,'10 subjects\n130 original ten-second clips\n130 data checks passed',72,438,540,170,23,GRAY);
 bars(s,['Fall','No fall'],[{name:'Windows',values:[99,297],fill:BLUE}],{left:650,top:207,width:560,height:375},{max:320,format:'0'});
 text(s,'99 fall windows and 297 no-fall windows',666,604,540,38,17,GRAY);

 s=slide(p,'Each window carries a binary label','The model receives sensor values and predicts fall = 1 or no fall = 0.',
 'The processed NPZ file already stores the label for each window. Positive windows come from valid annotated falls. Negative windows avoid the annotated fall buffer and use the existing sampling procedure. The two charts show real z-axis accelerometer data from one fall window and one no-fall window, selected from subject 1. Subject identity is not an input feature. These are examples of the stored labels, not new manually inferred labels. Source: '+source+'data_processed/quida_windows_4s.npz. Example array rows: '+d.examples.map(e=>e.row).join(', ')+'. Signal units follow the stored dataset values.');
 for(let k=0;k<2;k++){
  const e=d.examples[k]; const y=204+k*209;
  text(s,k===0?'Fall window   Label 1':'No-fall window   Label 0',67,y,500,39,21,k===0?BLUE:TEAL,true);
  s.charts.add('line',{position:{left:550,top:y-5,width:650,height:177},categories:e.time.filter((_,i)=>i%5===0).map(t=>t.toFixed(1)),series:[{name:'ACC z-axis',values:e.values.filter((_,i)=>i%5===0).map(v=>Number(v.toFixed(5))),line:{fill:k===0?BLUE:TEAL,width:2.5},marker:{symbol:'none'}}],hasLegend:false,chartFill:'#FFFFFF',xAxis:{textStyle:{...chartText,fontSize:14},majorGridlines:null},yAxis:{textStyle:{...chartText,fontSize:14},majorGridlines:{fill:'#E3EBF5',width:1}}});
  text(s,k===0?'A valid annotated fall defines\nthe positive window.':'Existing negative sampling defines\nthe no-fall window.',68,y+57,460,101,20,GRAY);
 }
 text(s,'Example signal: accelerometer z-axis across approximately 4 seconds',553,630,660,30,14,GRAY);

 s=slide(p,'Random window evaluation','We shuffle the labelled windows without grouping by person or source clip.',
 'We use StratifiedKFold with five folds, shuffle enabled and random seed 20261117. Only the labels and window row positions enter split selection. Labels remain attached to the matching sensor values. In each round, three folds train, the next fold validates and the current fold tests. This gives approximately sixty percent training, twenty percent validation and twenty percent testing. Every one of the 396 windows contributes exactly one out-of-fold test prediction per model. Overlapping windows may appear across partitions. Source: '+source+'results/four_model_comparison/window/splits.json and code/compare_four_models.py.');
 const splitRows=d.splits.splits.map(f=>[String(f.fold),String(f.train.length),String(f.validation.length),String(f.test.length)]);
 table(s,[['Round','Train','Validation','Test'],...splitRows],66,211,1148,335,[257,297,297,297],23);
 text(s,'396 test predictions per model after five rounds',69,582,1130,52,26,BLUE,true);

 s=slide(p,'Four models, two sensor representations','Within each architecture, we change the input channel count for the sensor.',
 'The accelerometer input has 250 time steps and three channels. Radar uses up to 42 time steps with 22 aggregated features, although actual valid lengths range from 26 to 34 frames. The radar mask distinguishes padding from valid observations, including valid empty detections. CNN has three convolution layers with 16, 32 and 64 channels and masked average pooling. LSTM has one layer and 32 hidden units. Both use dropout 0.3 and a two-class output. Sources: '+source+'code/compare_four_models.py and data_processed/quida_windows_4s.npz. Parameter counts come from the saved summary.');
 table(s,[['Model','Input per window','Trainable parameters'],...names.map((n,i)=>[labels[i],n.startsWith('acc')?'250 × 3':'Up to 42 × 22',d.window.models[n].folds[0].parameters.toLocaleString('en-US')])],66,214,1148,303,[325,433,390],23);
 text(s,'CNN: 3 convolution layers + masked average pooling',69,552,1140,42,22,INK,true);
 text(s,'LSTM: 1 recurrent layer with 32 hidden units',69,604,1140,42,22,INK,true);

 s=slide(p,'Shared training and scoring rules','The test labels support final scoring only.',
 'All four models use Adam with a learning rate of 0.001, weight decay of 0.0001, batch size 32 and up to 45 epochs. We calculate normalisation statistics and class weights from training windows only. We choose the epoch with the minimum unweighted validation cross-entropy. The decision threshold stays at 0.5. Each model and fold uses a fixed initialisation seed, but this is not a multiple-seed stability study. We score accuracy, precision, recall, specificity, F1, balanced accuracy and AUROC. Source: '+source+'code/compare_four_models.py.');
 text(s,'Training',68,211,510,46,27,BLUE,true);
 text(s,'Adam, learning rate 0.001\nBatch size 32\nUp to 45 epochs\nDropout 0.3',68,285,510,235,23,INK);
 text(s,'Evaluation',675,211,535,46,27,TEAL,true);
 text(s,'Training-only normalisation\nTraining-only class weights\nValidation loss selects the epoch\nFixed prediction threshold: 0.5',675,285,535,235,23,INK);
 text(s,'One shared split for a fair comparison of all four models',68,582,1140,60,25,BLUE,true);

 s=slide(p,'Main results on all 396 test windows','Random window evaluation, pooled across the five test folds.',
 'This table pools the out-of-fold test predictions, not training predictions. Radar CNN gives the highest accuracy and F1 in this run. Accuracy alone is insufficient because three quarters of windows have the no-fall label, so we also report F1, recall and precision. These numbers describe the selected dataset and random window protocol. We have not tested whether the small differences are statistically significant. Source: '+source+'results/four_model_comparison/window/summary.json and predictions.csv.');
 table(s,[['Model','Accuracy','F1','Recall','Precision'],...names.map((n,i)=>{const m=d.window.models[n].pooled;return[labels[i],pct(m.accuracy),dec(m.f1),pct(m.recall),pct(m.precision)];})],66,220,1148,319,[310,210,190,219,219],23);
 text(s,'Radar CNN: 98.74% accuracy and F1 = 0.9751',69,590,1140,53,27,BLUE,true);

 s=slide(p,'Radar CNN has the highest F1 in this run','The four scores use the same labelled windows and the same test assignments.',
 'The chart uses the full F1 range from zero to one. Radar CNN reaches 0.9751, accelerometer CNN and radar LSTM both reach 0.9510, and accelerometer LSTM reaches 0.9378. The best-to-lowest F1 gap is approximately 0.0373. With only one initialisation per model and fold, we treat this as an observed ranking rather than a stable architecture advantage. Source: '+source+'results/four_model_comparison/window/summary.json.');
 bars(s,labels,[{name:'F1',values:names.map(n=>d.window.models[n].pooled.f1),fill:BLUE}],{left:67,top:206,width:1143,height:365},{format:'0.0000'});
 text(s,'Observed ranking only. Repeated seeds will test how stable it is.',71,606,1135,43,22,GRAY);

 s=slide(p,'Errors behind the scores','The test set contains 99 fall windows and 297 no-fall windows.',
 'For each model, detected and missed falls add up to 99. Correct no-fall predictions and false alarms add up to 297. Radar CNN detects 98 of 99 falls and produces four false alarms. Accelerometer LSTM also detects 98 falls, but produces twelve false alarms. This shows why recall alone does not identify the best overall classifier. These are counts per selected window, not false alarms per hour in continuous use. Source: '+source+'results/four_model_comparison/window/summary.json and predictions.csv.');
 table(s,[['Model','Detected falls','Missed falls','False alarms','Correct no fall'],...names.map((n,i)=>{const m=d.window.models[n].pooled;return[labels[i],String(m.tp),String(m.fn),String(m.fp),String(m.tn)];})],66,219,1148,320,[290,214,214,214,216],21);
 text(s,'Radar CNN: 1 missed fall and 4 false alarms',69,588,1140,53,27,BLUE,true);

 s=slide(p,'Supplementary LOSO evaluation','F1 comparison with leave-one-subject-out (LOSO) testing.',
 'Each LOSO round uses eight people for training, one for validation and one for testing. Subject identities do not overlap across these sets. Every window again receives one test prediction. We use the same four model architectures and training settings. The chart compares pooled F1 values. The two protocols train on different quantities of windows, so their differences do not isolate subject generalisation alone. Radar CNN remains highest by pooled F1 in both protocols, but some LOSO scores exceed random-window scores. There is no requirement that one protocol always give a higher score. Source: '+source+'results/four_model_comparison/{window,loso}/summary.json.');
 bars(s,labels,[{name:'Random windows',values:names.map(n=>d.window.models[n].pooled.f1),fill:BLUE},{name:'LOSO',values:names.map(n=>d.loso.models[n].pooled.f1),fill:TEAL}],{left:67,top:207,width:1145,height:381},{format:'0.000',legend:true});
 text(s,'LOSO per round: 8 people train, 1 validates, 1 tests',70,621,1136,37,21,GRAY);

 const overlap=d.splits.overlap_diagnostics.reduce((a,b)=>a+b.test_windows_overlapping_training,0);
 s=slide(p,'What the current results can tell us','Random windows measure classification under a mixed-window sampling protocol.',
 'The main protocol intentionally ignores person and source-clip grouping. Across the five folds, '+overlap+' of the 396 tested windows overlap in time with at least one training window from the same person and source clip. Each tested window appears once in this total. This shared raw signal limits independence, especially for the sampled no-fall windows. We preserve this protocol because it directly answers the current window classification question. LOSO provides a separate subject-isolated view. Dataset size, limited non-fall activity and a single initialisation per fold also limit the conclusions. Sources: '+source+'results/four_model_comparison/window/splits.json, FOUR_MODEL_PROTOCOL.md and data_processed/quida_windows_4s.npz.');
 text(s,overlap+' / 396',69,222,620,109,56,BLUE,true);
 text(s,'test windows overlap\nwith training signals',72,346,570,107,29,INK,true);
 text(s,'Shared signal can raise test scores.\nThe window index sets remain disjoint.',72,511,590,99,21,GRAY);
 text(s,'Other limits',754,224,440,45,26,INK,true);
 text(s,'Only 10 subjects\nLimited non-fall activities\nOne training seed per model/fold\nNo continuous-use evaluation yet',754,302,440,253,22,GRAY);

 s=slide(p,'Next experiments','The next phase will test stability and inspect the remaining errors.',
 'These are proposed next steps, not completed experiments. First, rerun fixed folds with multiple initialisation seeds and report mean and standard deviation. Second, inspect the missed-fall and false-alarm waveforms and review their annotations. Third, compare the current protocol with non-overlapping windows and harder no-fall activities if those are available, while keeping random-window results as the main reference. Fourth, test accelerometer-radar fusion against the best single-sensor model. Metric learning can follow as a separate extension after the supervised benchmark is stable. No additional activity data or fusion result is claimed here.');
 item(s,1,'Repeated training seeds','Report mean F1 and its variation on the same frozen folds.',204);
 item(s,2,'Review the error windows','Inspect missed falls, false alarms and their source annotations.',317);
 item(s,3,'Harder and more independent test windows','Compare non-overlapping sampling and available difficult no-fall motions.',430);
 item(s,4,'Accelerometer and radar fusion','Compare a two-sensor model with the best single-sensor baseline.',543);

 s=slide(p,'Current conclusion and next milestone','We now have a complete supervised comparison for both sensors.',
 'The completed work includes data validation, window labels, shared random-window splits, all four supervised model combinations and supplementary LOSO. Radar CNN currently leads the random-window results at 98.74 percent accuracy and 0.9751 F1. The main experiment intentionally mixes windows without grouping by identity. Our next milestone is a repeated-seed benchmark with an error review and a clear comparison of window sampling choices. Fusion and later metric learning should build on that stable benchmark. The current results support this experimental comparison, but not a deployment claim. Sources: '+source+'results/four_model_comparison/{window,loso}/summary.json and FOUR_MODEL_PROTOCOL.md.');
 text(s,'98.74%',69,220,620,106,60,BLUE,true);
 text(s,'Radar CNN accuracy\nF1 = 0.9751',72,345,570,104,28,INK,true);
 text(s,'Next milestone',754,225,450,47,27,TEAL,true);
 text(s,'Training across multiple seeds\nwith reviewed error windows\nand sampling comparisons',754,314,450,189,25,INK);
 text(s,'Completed: 4 model combinations, 396 test windows per model, supplementary LOSO',72,585,1135,59,21,GRAY);
 if(p.slides.items.length!==14)throw Error('Expected 14 slides');
 return {slides:p.slides.items.length};
}
