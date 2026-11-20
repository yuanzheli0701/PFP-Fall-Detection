# QUIDA Progress Report — Simple Speech Script

**Deck:** `QUIDA_Data_Cleaning_EN_WhiteBlue.pptx` (same folder)  
**Suggested time:** about 5-6 minutes  
**Focus:** completed work, preliminary results, and problems found

> Keep the tone simple. Do not read every number on the slides. The most important message is:
> the data foundation is ready, but the model scores are only preliminary.

## A. English Delivery Script

### Slide 1 — Cover | about 20 seconds

Good morning, Professor. I will give a short progress report on our QUIDA fall-detection project.
I will focus on three points: what we have cleaned, what we have tested, and the main problems
we found.

### Slide 2 — Executive Summary | about 35 seconds

The first stage is complete. We have 130 fixed ten-second clips: 99 with a fall and 31 without.
From them, we built 396 four-second windows and ten leave-one-subject-out folds. The independent
quality check passed all 130 tests. Two small baseline models also ran end to end. The results are
encouraging, but they are still preliminary.

### Slide 3 — Data Footprint | about 30 seconds

QUIDA has four sensors: accelerometer, radar, LiDAR, and a thermal camera. Their sampling rates
are very different, from 2.6 to 62.5 hertz. Therefore, we do not align the sensors by frame number;
we align everything on absolute time.

### Slide 4 — Synchronisation | about 30 seconds

The time alignment is good for 99 of 100 events. The only failure is subject 3, fall 2, with about
ten seconds of offset. We marked this event invalid. We did not force a label or hide the problem.

### Slide 5 — Cleaning Pipeline | about 30 seconds

Our cleaning pipeline has six steps: read the source files, cut fixed blocks, assign labels from
the index table, align clocks, preserve masks, and build model inputs. Each step is documented and
can be reproduced.

### Slide 6 — Class Structure | about 35 seconds

At clip level, the dataset is imbalanced: 99 fall clips and 31 no-fall clips. For the model windows,
we use a one-to-three ratio per subject. So we have 99 positive and 297 negative windows. We did not
relabel data to make the classes look balanced.

### Slide 7 — Data Anomalies | about 35 seconds

We had three important edge cases. Subject 8 clips 9 to 11 are not in time order, so we cut by fixed
625-sample blocks. Subject 3 clip 8 is kept as no-fall with a review flag. Radar has 1,377 empty
frames; we keep them as valid empty observations.

### Slide 8 — Window Protocol | about 30 seconds

For each valid fall, we take a four-second window centred on the event. We also keep a two-second
guard on each side. Negative windows cannot enter this guard. Finally, every subject is completely
held out in turn for LOSO evaluation.

### Slide 9 — Baseline Models | about 30 seconds

To test the full learning path, we used two deliberately simple models: a 1D-CNN on accelerometer
and an LSTM on radar. We did this first to check data shapes, training, prediction, and reporting
before comparing larger models.

### Slide 10 — Preliminary Results | about 35 seconds

On 396 held-out windows, the CNN reached an F1 score of 0.952, and the radar LSTM reached 0.946.
Recall is 1.000 and 0.970. These numbers show that the pipeline works. But they are not a final
generalisation claim.

### Slide 11 — Error Analysis | about 35 seconds

Most errors are on subjects 3 and 8. Both models have five false positives on S3 and three on S8.
The radar model also misses three falls from S1 and S2. Six of ten folds reach F1 equal to one,
which tells us the negative samples are still too easy.

### Slide 12 — Interpretation and Next Steps | about 40 seconds

Our conclusion is that the data foundation is solid, but the performance claim needs a harder test.
The main problems are the small sample size, the easy negative samples, and the limited model
comparison. Next, we will add hard negatives, test metric learning, try sensor fusion, and freeze
the final benchmark.

### Slide 13 — Backup | about 10 seconds

Slide 13 is a backup with data shapes and reproduction commands. I will not go through it unless
you would like more technical detail. Thank you. I am happy to take questions.

## B. 中文汇报版

### 第 1 页：封面

老师好，下面我简要汇报一下我们 QUIDA 跌倒检测项目的进度。我会重点讲三件事：我们完成了什么清洗、做了什么初步测试，以及目前遇到的问题。

### 第 2 页：总体进展

第一阶段已经完成。我们得到 130 个固定的 10 秒片段，其中 99 个有跌倒、31 个没有跌倒。随后我们构造了 396 个 4 秒窗口，并划分了 10 折留一受试者验证。独立质量检查的 130 项全部通过。两个小型基线模型也已经完整跑通。结果是积极的，但目前仍然只是初步结果。

### 第 3 页：数据构成

QUIDA 包含四种传感器：加速度计、毫米波雷达、LiDAR 和红外热像仪。它们的采样率差别很大，从 2.6 赫兹到 62.5 赫兹。因此我们没有按帧号对齐，而是全部按绝对时间对齐。

### 第 4 页：时间同步

100 个事件里有 99 个通过同步检查。唯一失败的是 S3 的第 2 次跌倒，大约有 10 秒偏差。我们把这个事件标记为无效，没有强行改标签，也没有隐藏这个问题。

### 第 5 页：清洗流程

我们的清洗流程有六步：读取原始文件、切成固定块、根据索引表分配标签、对齐时间、保留有效掩码，以及生成模型输入。每一步都有记录，可以重复生成。

### 第 6 页：类别结构

在 10 秒片段层面，数据是不平衡的：99 个跌倒片段，31 个非跌倒片段。在 4 秒窗口层面，我们按受试者构造 1 比 3 的正负样本比例，因此得到 99 个正样本和 297 个负样本。我们没有通过修改标签来让数据看起来平衡。

### 第 7 页：数据异常

数据里有三个关键异常。第一，S8 的第 9 到第 11 个片段时间顺序错乱，所以我们使用固定的 625 个采样点切分。第二，S3 的第 8 个片段保留为非跌倒，但加上复核标记。第三，雷达有 1377 个空帧，我们保留它们，而不是直接删除。

### 第 8 页：窗口协议

对每一次有效跌倒，我们取一个以事件为中心的 4 秒窗口，并在两侧各保留 2 秒保护间隔。负样本不能进入这个保护区域。最后，每名受试者会依次完全留出，做留一受试者验证。

### 第 9 页：基线模型

为了验证整条学习流程，我们用了两个故意设计得很简单的模型：加速度计上的 1D-CNN，以及雷达上的 LSTM。目的不是追求复杂模型，而是先确认数据形状、训练、预测和报告流程都能跑通。

### 第 10 页：初步结果

在 396 个留出窗口中，CNN 的 F1 是 0.952，雷达 LSTM 的 F1 是 0.946。召回率分别是 1.000 和 0.970。这个结果说明流程是可行的，但还不能作为最终的泛化结论。

### 第 11 页：错误分析

错误主要集中在 S3 和 S8。两个模型在 S3 上都有 5 个假阳性，在 S8 上都有 3 个假阳性。雷达模型还漏掉了 S1 和 S2 的 3 次跌倒。10 折里有 6 折的 F1 达到 1.000，这说明当前负样本仍然比较简单。

### 第 12 页：结论与下一步

我们的结论是：数据基础已经比较扎实，但性能结论还需要更严格的测试。当前主要问题是样本量小、负样本偏简单，而且模型比较还不完整。下一步我们会加入困难负样本，测试度量学习，尝试传感器融合，并固定最终评测协议。

### 第 13 页：备份

第 13 页是数据形状和复现命令的备份页。如果老师不需要技术细节，这一页可以快速带过。我的汇报到这里，谢谢老师，欢迎提问。

## C. Short Answers for Likely Questions

### 1. Why are there 99 falls, not 100?

There are 100 raw annotations. Subject 3, fall 2, has about ten seconds of disagreement between
the annotation and the sensor timestamps. We marked it invalid. The other 99 events are valid.

### 2. Why are there 31 no-fall clips?

There are 130 fixed clips in total, and 99 of them contain a valid fall. Therefore, 31 clips are
no-fall clips. Subject 3 has four no-fall clips because it has nine valid falls, while the other
subjects have three.

### 3. Why are there 297 negative windows if there are only 31 no-fall clips?

The 31 no-fall clips are clip-level negatives. The 297 values are four-second windows used for
training. They are constructed with a one-to-three ratio per subject. Most come from no-fall clips,
and some come from safe parts of fall clips outside the two-second guard. They are overlapping
training windows, not 297 independent non-fall events.

### 4. Why are the scores so high?

The current negative windows come mainly from walking and other limited activity. Six of ten folds
reach F1 equal to one. The scores show that the pipeline is correct, but they may be optimistic.
We still need hard negatives and a final benchmark.

### 5. Why did you test only accelerometer and radar?

All four modalities are cleaned and stored. We used one inertial model and one radar model to check
two different data paths first. LiDAR, thermal data, and fusion will be tested in the next stage.

### 6. What was the biggest problem?

The main data problems were subject 8's clip order, subject 3's invalid event, variable-length
sensor rows, and empty radar frames. We handled each one explicitly. The main scientific problem
that remains is the small sample size and the limited variety of negative actions.

## D. Delivery Tips

- Speak more slowly on slides 2, 10, and 12. These contain the main progress, result, and caveat.
- Do not read the table on slide 13 unless the teacher asks for reproducibility details.
- When you say the F1 scores, always add: **"These are preliminary pipeline-validation results."**
- If you are short on time, skip slides 3 and 13 and keep slides 2, 6, 10, 11, and 12.
