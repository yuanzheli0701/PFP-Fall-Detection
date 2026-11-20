# 随机窗口四组对比与 LOSO 补充实验

日期：2026-11-17。此方案按最新要求替代之前的原始片段分组方案。

## 主实验

全部 396 个四秒窗口已有标签：跌倒=1（99 个），非跌倒=0（297 个）。标签与窗口绑定，两种传感器使用相同窗口行号和标签。

使用 `StratifiedKFold(n_splits=5, shuffle=True, random_state=20261117)` 随机分层划分。仅使用窗口数量和分类标签，不使用受试者或片段编号来限制划分。身份信息只保留用于追溯和重叠诊断，不输入模型，也不要求各集合覆盖所有受试者。

每轮三个折训练、下一折验证、当前折测试，约为 60%/20%/20%。四组模型共享划分，五轮后每个窗口恰好测试一次，共 396 个外层测试预测/模型。训练使用训练标签，验证标签用于选择 epoch，测试标签仅用于最终评分。

允许同一受试者、同一原始片段和时间重叠窗口跨集合。现有窗口有 925 对同片段内时间重叠，训练与测试可能共享原始信号；本实验表示随机窗口分类表现，不代表独立片段或新受试者泛化能力。逐折跨训练/测试重叠情况记录在划分文件中，不用于修改划分。

## 模型和训练

- 四组：加速度计 CNN、加速度计 LSTM、雷达 CNN、雷达 LSTM。
- 输入：加速度计 250×3；雷达最多 42×22，有效长度 26–34 帧，保留掩码。
- CNN：卷积通道 16/32/64，核宽 5/5/3，ReLU，带掩码全局平均池化，Dropout 0.3，二分类输出。
- LSTM：单层，32 隐藏单元，Dropout 0.3，二分类输出。变长序列打包，等长序列裁至有效长度后使用标准批处理核。
- 同一架构跨传感器仅调整输入通道数。身份、窗口编号和标签不作为输入特征。
- 每折标准化和类别权重只来自训练窗口；填充帧不参与统计。
- Adam，学习率 0.001，weight decay 0.0001，batch size 32，最多 45 epochs，梯度裁剪 5。
- 按最小验证集无权重交叉熵选择 epoch，分类阈值固定 0.5。初始化前设置种子，使用确定性 CPU 运算。
- 每模型/折一个初始化种子，折间标准差不等于初始化随机性的不确定度。
- 报告准确率、精确率、召回率、特异度、F1、平衡准确率、AUROC 和混淆矩阵。

## 补充 LOSO

保留已完成的四组 LOSO：十轮，每轮一人测试、下一个编号的人验证，其余八人训练。各集合受试者完全隔离，模型与训练设置和主实验一致。

旧初步基线使用九人训练且没有验证集，CNN 结构也不同，不将其成绩与本轮新增模型直接拼接。

## 复现与输出

从本实验目录运行：

```powershell
D:\Anaconda\python.exe code\compare_four_models.py --protocol window
D:\Anaconda\python.exe code\report_four_models.py
```

默认运行随机窗口和 LOSO；`--protocol loso` 仅重跑 LOSO。对应协议的重跑会覆盖该协议目录。

- `results/four_model_comparison/window/`：当前随机窗口主实验。
- `results/four_model_comparison/loso/`：保留的补充 LOSO。
- `results/four_model_comparison/mixed/`：旧原始片段分组实验归档，`--protocol mixed` 可复现。
- 每个协议包含 `splits.json`、`summary.json`、`predictions.csv`、`*_fold*.pt` 权重（含归一化参数与划分）。
- `results/four_model_comparison/RESULTS_CN.md`：当前结果汇总。
- `GROUPED_PROTOCOL_ARCHIVE.md` 和 `results/four_model_comparison/GROUPED_RESULTS_ARCHIVE_CN.md`：旧方案与旧汇总。

原始数据、窗口数组、分类标签和历史初步基线保留。
