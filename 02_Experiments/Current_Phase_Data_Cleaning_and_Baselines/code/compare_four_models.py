"""Paired four-model benchmark: shuffled window CV and supplementary LOSO."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold
from train_preliminary_baselines import metrics

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('acc_cnn', 'acc_lstm', 'radar_cnn', 'radar_lstm')


class CNN(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.layers = nn.ModuleList([nn.Conv1d(channels, 16, 5, padding=2),
                                     nn.Conv1d(16, 32, 5, padding=2),
                                     nn.Conv1d(32, 64, 3, padding=1)])
        self.head = nn.Sequential(nn.Dropout(.3), nn.Linear(64, 2))

    def forward(self, x, lengths):
        mask = (torch.arange(x.shape[1])[None, :] < lengths[:, None])[:, None, :]
        x = x.transpose(1, 2)
        for layer in self.layers:
            x = torch.relu(layer(x)) * mask
        return self.head(x.sum(-1) / lengths[:, None])


class LSTM(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.encoder = nn.LSTM(channels, 32, batch_first=True)
        self.head = nn.Sequential(nn.Dropout(.3), nn.Linear(32, 2))

    def forward(self, x, lengths):
        # Equal-length sequences need no packing; the dense CPU kernel is faster.
        if torch.all(lengths == lengths[0]):
            _, (hidden, _) = self.encoder(x[:, :int(lengths[0])])
            return self.head(hidden[-1])
        packed = nn.utils.rnn.pack_padded_sequence(x, lengths.cpu(), batch_first=True,
                                                   enforce_sorted=False)
        _, (hidden, _) = self.encoder(packed)
        return self.head(hidden[-1])


def grouped_folds(w, seed):
    """Select folds using labels/counts only, never model performance."""
    y, subjects = w['label'], w['subject']
    groups = subjects * 100 + w['clip']
    best = None
    for offset in range(200):
        splitter = StratifiedGroupKFold(5, shuffle=True, random_state=seed + offset)
        folds = [test for _, test in splitter.split(y, y, groups)]
        if any(len(np.unique(subjects[f])) != 10 or len(np.unique(y[f])) != 2 for f in folds):
            continue
        counts = np.array([np.bincount(y[f], minlength=2) for f in folds])
        per_subject = np.array([[np.sum(subjects[f] == s) for s in range(1, 11)] for f in folds])
        score = np.sum(((counts - counts.mean(0)) / counts.mean(0)) ** 2)
        score += np.sum(((per_subject - per_subject.mean(0)) / per_subject.mean(0)) ** 2)
        if best is None or score < best[0]:
            best = (score, folds, seed + offset)
    if best is None:
        raise ValueError('No five-fold split covers every subject and both labels.')
    return best[1], best[2]


def audit(w, train, val, test, protocol):
    parts = [train, val, test]
    joined = np.concatenate(parts)
    assert len(joined) == len(w['label']) and len(np.unique(joined)) == len(joined)
    assignments = np.empty(len(joined), dtype=int)
    for k, idx in enumerate(parts):
        assert len(np.unique(w['label'][idx])) == 2
        assignments[idx] = k
    for i in range(len(joined)):
        for j in range(i):
            same_clip = w['subject'][i] == w['subject'][j] and w['clip'][i] == w['clip'][j]
            if same_clip and protocol != 'window':
                assert assignments[i] == assignments[j], 'Source clip crossed partitions'
    if protocol == 'mixed':
        assert all(len(np.unique(w['subject'][idx])) == 10 for idx in parts)
    elif protocol == 'loso':
        assert all(not set(w['subject'][parts[i]]) & set(w['subject'][parts[j]])
                   for i in range(3) for j in range(i))


def prepare(w, sensor, train):
    x = w[sensor].copy()
    mask = w['radar_mask'] if sensor == 'radar' else np.ones(x.shape[:2], dtype=bool)
    assert np.all(mask.sum(1) > 0)
    assert np.all(mask == (np.arange(x.shape[1])[None, :] < mask.sum(1)[:, None]))
    values = x[train][mask[train]]
    mean, std = values.mean(0), values.std(0)
    std = np.where(std < 1e-7, 1., std)
    x = (x - mean) / std
    x[~mask] = 0
    return torch.tensor(x), torch.tensor(mask.sum(1)), mean, std


def run_model(w, name, train, val, test, epochs, seed, checkpoint):
    torch.manual_seed(seed)
    np.random.seed(seed)
    sensor, architecture = name.split('_')
    x, lengths, mean, std = prepare(w, sensor, train)
    y = torch.tensor(w['label'].astype(np.int64))
    model = (CNN if architecture == 'cnn' else LSTM)(x.shape[-1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    counts = np.bincount(w['label'][train], minlength=2)
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(len(train) / (2 * counts), dtype=torch.float32))
    validation_loss = nn.CrossEntropyLoss()
    generator = torch.Generator().manual_seed(seed)
    best_loss, best_epoch, state = float('inf'), 0, None
    start = time.perf_counter()
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.tensor(train)[torch.randperm(len(train), generator=generator)]
        for batch in order.split(32):
            optimizer.zero_grad()
            loss = criterion(model(x[batch], lengths[batch]), y[batch])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.)
            optimizer.step()
        model.eval()
        with torch.no_grad():
            loss = float(validation_loss(model(x[val], lengths[val]), y[val]))
        if loss < best_loss:
            best_loss, best_epoch, state = loss, epoch, copy.deepcopy(model.state_dict())
    model.load_state_dict(state)
    model.eval()
    with torch.no_grad():
        probability = torch.softmax(model(x[test], lengths[test]), 1)[:, 1].numpy()
        # Extra right-padding must not change predictions for either architecture.
        padded = nn.functional.pad(x[test], (0, 0, 0, 7))
        padded_probability = torch.softmax(model(padded, lengths[test]), 1)[:, 1].numpy()
        assert np.allclose(probability, padded_probability, atol=1e-6)
    torch.save({'state_dict': state, 'mean': mean.tolist(), 'std': std.tolist(),
                'model': name, 'seed': seed, 'best_epoch': best_epoch,
                'train_indices': train.tolist(), 'validation_indices': val.tolist(),
                'test_indices': test.tolist()}, checkpoint)
    result = {'best_epoch': best_epoch, 'validation_loss': best_loss,
              'seconds': time.perf_counter() - start,
              'parameters': sum(p.numel() for p in model.parameters()),
              'metrics': metrics(w['label'][test], (probability >= .5).astype(int), probability)}
    return result, probability


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=45)
    parser.add_argument('--seed', type=int, default=20261117)
    parser.add_argument('--protocol', choices=['window', 'mixed', 'loso', 'both'], default='both')
    args = parser.parse_args()
    assert args.epochs > 0
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    source = ROOT / 'data_processed/quida_windows_4s.npz'
    w = dict(np.load(source, allow_pickle=False))
    output = ROOT / 'results/four_model_comparison'
    output.mkdir(parents=True, exist_ok=True)
    for protocol in (['window', 'loso'] if args.protocol == 'both' else [args.protocol]):
        if protocol == 'mixed':
            folds, split_seed = grouped_folds(w, args.seed)
        elif protocol == 'window':
            # Labels only: neither subject nor source clip enters split selection.
            splitter = StratifiedKFold(5, shuffle=True, random_state=args.seed)
            folds = [test for _, test in splitter.split(np.zeros(len(w['label'])), w['label'])]
            split_seed = args.seed
        folder = output / protocol
        folder.mkdir(exist_ok=True)
        splits = []
        for fold in range(10 if protocol == 'loso' else 5):
            if protocol != 'loso':
                test, val = folds[fold], folds[(fold + 1) % 5]
                train = np.concatenate([folds[k] for k in range(5) if k not in (fold, (fold + 1) % 5)])
            else:
                test = np.flatnonzero(w['subject'] == fold + 1)
                val = np.flatnonzero(w['subject'] == (fold + 1) % 10 + 1)
                train = np.flatnonzero(~np.isin(w['subject'], [fold + 1, (fold + 1) % 10 + 1]))
            audit(w, train, val, test, protocol)
            splits.append({'fold': fold + 1, 'train': train.tolist(), 'validation': val.tolist(), 'test': test.tolist()})
        receipt = {'protocol': protocol, 'split_seed': split_seed if protocol != 'loso' else None,
                   'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'audit': ('PASS: exhaustive/disjoint window indices, both classes; no subject/clip grouping'
                             if protocol == 'window' else
                             'PASS: exhaustive/disjoint partitions, source-clip isolation, subject coverage/isolation, both classes'),
                   'splits': splits}
        if protocol == 'window':
            overlap = []
            for split in splits:
                test, train = np.array(split['test']), np.array(split['train'])
                involved, pairs = set(), 0
                for i in test:
                    for j in train:
                        if (w['subject'][i] == w['subject'][j] and w['clip'][i] == w['clip'][j]
                                and max(w['start_time'][i], w['start_time'][j]) < min(w['end_time'][i], w['end_time'][j])):
                            pairs += 1
                            involved.add(int(i))
                overlap.append({'fold': split['fold'], 'train_test_overlapping_pairs': pairs,
                                'test_windows_overlapping_training': len(involved)})
            receipt['overlap_diagnostics'] = overlap
        (folder / 'splits.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        rows, results = [], {name: [] for name in NAMES}
        for split in splits:
            train, val, test = [np.array(split[k]) for k in ('train', 'validation', 'test')]
            for model_index, name in enumerate(NAMES):
                seed = args.seed + split['fold'] * 100 + model_index
                result, probability = run_model(w, name, train, val, test, args.epochs, seed,
                                                folder / f"{name}_fold{split['fold']}.pt")
                results[name].append({'fold': split['fold'], 'seed': seed, **result})
                for idx, prob in zip(test, probability):
                    rows.append({'model': name, 'fold': split['fold'], 'row': int(idx),
                                 'subject': int(w['subject'][idx]), 'clip': int(w['clip'][idx]),
                                 'y_true': int(w['label'][idx]), 'probability': float(prob), 'y_pred': int(prob >= .5)})
                print(protocol, split['fold'], name, 'F1', round(result['metrics']['f1'], 4),
                      'epoch', result['best_epoch'], flush=True)
        summary = {**{k: v for k, v in receipt.items() if k != 'splits'},
                   'max_epochs': args.epochs, 'seed': args.seed, 'threshold': .5,
                   'selection': 'minimum unweighted validation cross-entropy; test evaluated once', 'models': {}}
        for name in NAMES:
            r = [r for r in rows if r['model'] == name]
            assert sorted(row['row'] for row in r) == list(range(len(w['label'])))
            pooled = metrics(np.array([i['y_true'] for i in r]), np.array([i['y_pred'] for i in r]),
                             np.array([i['probability'] for i in r]))
            summary['models'][name] = {'pooled': pooled, 'folds': results[name],
                'fold_f1_mean': float(np.mean([f['metrics']['f1'] for f in results[name]])),
                'fold_f1_std': float(np.std([f['metrics']['f1'] for f in results[name]]))}
        (folder / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        with (folder / 'predictions.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(protocol, 'POOLED', {n: round(v['pooled']['f1'], 4) for n, v in summary['models'].items()}, flush=True)


if __name__ == '__main__':
    main()
