"""Verify saved predictions and produce a compact Chinese benchmark report."""
import csv
import json
from pathlib import Path
import numpy as np
from train_preliminary_baselines import metrics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/four_model_comparison'
lines = ['# CNN/LSTM 双传感器对比结果', '', '日期：2026-11-17。', '',
         '全部指标来自每个窗口恰好一次的外层测试预测。四组模型共享划分；阈值固定 0.5。', '']
for protocol, title in [('window', '主实验：随机窗口分层五折（不按人或片段分组）'), ('loso', '补充实验：LOSO')]:
    folder = OUT / protocol
    summary = json.loads((folder / 'summary.json').read_text())
    with (folder / 'predictions.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    lines += [f'## {title}', '', '| 模型 | F1 | Recall | Specificity | Precision | Accuracy | AUROC | TN/FP/FN/TP |',
              '|---|---:|---:|---:|---:|---:|---:|---|']
    for name, result in summary['models'].items():
        selected = [r for r in rows if r['model'] == name]
        assert sorted(int(r['row']) for r in selected) == list(range(396))
        y, pred, prob = [np.array([float(r[k]) for r in selected]) for k in ('y_true', 'y_pred', 'probability')]
        assert np.array_equal(pred, prob >= .5)
        actual = metrics(y, pred, prob)
        for key, value in actual.items():
            assert np.isclose(value, result['pooled'][key]), (protocol, name, key)
        m = actual
        lines.append(f"| {name} | {m['f1']:.4f} | {m['recall']:.4f} | {m['specificity']:.4f} | {m['precision']:.4f} | {m['accuracy']:.4f} | {m['auroc']:.4f} | {m['tn']}/{m['fp']}/{m['fn']}/{m['tp']} |")
    lines += ['', '逐折 F1（均值 ± 总体标准差，仅描述折间变化）：', '']
    for name, result in summary['models'].items():
        lines.append(f"- {name}: {result['fold_f1_mean']:.4f} ± {result['fold_f1_std']:.4f}")
    lines.append('')
lines += ['## 解释与验证', '',
          '- 主实验仅使用窗口行号和跌倒/非跌倒标签随机分层划分，不按受试者或原始片段分组；身份信息仅用于结果追溯。',
          '- 全部 396 个窗口用于轮换测试，每个模型每个窗口恰好测试一次。',
          '- 重叠窗口可以跨训练/验证/测试集合，因此存在共享原始信号的情况；主实验衡量随机窗口分类表现，不能作为独立片段或新受试者泛化结论。',
          '- LOSO 每轮八人训练、一人验证、一人测试，测试受试者完全未见。',
          '- 两种协议都按验证集交叉熵选择 epoch，最多 45 轮；归一化与类别权重只来自训练集。',
          '- 数据量小、负样本活动有限；高分和小幅差异不能证明统计显著性，也不能代表真实部署效果。',
          '- 本轮未搜索模型超参数，未根据测试表现重新选择划分或阈值。每个模型/折使用一个固定初始化种子。',
          '- 新 CNN 使用掩码卷积与池化，旧 CNN 使用 BatchNorm 和 MaxPool，且新 LOSO 留出验证受试者，因此新旧成绩不宜直接归因于划分方式。',
          '- 已检查每折窗口行号互斥且覆盖全部窗口、类别覆盖，以及补充 LOSO 的受试者隔离；主实验不检查同片段隔离或受试者覆盖。',
          '- 每个训练后模型通过额外右侧填充不改变预测的检查；此报告重新计算并核对保存的逐窗口预测指标。',
          '', '实验详细设置见上级目录 `FOUR_MODEL_PROTOCOL.md`。旧片段分组实验存放在 `mixed/`，不作为本表主实验。', '']
diagnostics = json.loads((OUT / 'window/splits.json').read_text())['overlap_diagnostics']
lines += ['## 主实验重叠诊断', '', '| 折 | 测试窗口与训练窗口重叠配对数 | 与训练信号重叠的测试窗口数 |', '|---|---:|---:|']
for d in diagnostics:
    lines.append(f"| {d['fold']} | {d['train_test_overlapping_pairs']} | {d['test_windows_overlapping_training']} |")
(OUT / 'RESULTS_CN.md').write_text('\n'.join(lines), encoding='utf-8')
print('\n'.join(lines))
