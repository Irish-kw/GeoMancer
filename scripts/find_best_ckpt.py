#!/usr/bin/env python3
"""Find the best encoder checkpoint from val/stats.json."""

import argparse
import json
import sys
from pathlib import Path


def find_best_ckpt(run_dir, metric='mae', higher_is_better=False):
    run_dir = Path(run_dir)
    val_stats = run_dir / 'val' / 'stats.json'
    ckpt_dir = run_dir / 'ckpt'

    if not val_stats.is_file():
        raise FileNotFoundError(f'Missing val stats: {val_stats}')

    rows = []
    with val_stats.open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    if not rows:
        raise ValueError(f'No entries in {val_stats}')

    if metric not in rows[0]:
        raise KeyError(f"Metric '{metric}' not found in {val_stats}")

    if higher_is_better:
        best = max(rows, key=lambda r: r[metric])
    else:
        best = min(rows, key=lambda r: r[metric])

    best_epoch = best['epoch']
    ckpt_path = ckpt_dir / f'{best_epoch}.ckpt'

    if not ckpt_path.is_file():
        saved_epochs = sorted(int(p.stem) for p in ckpt_dir.glob('*.ckpt'))
        if not saved_epochs:
            raise FileNotFoundError(f'No checkpoints in {ckpt_dir}')
        prior = [e for e in saved_epochs if e <= best_epoch]
        use_epoch = max(prior) if prior else saved_epochs[0]
        ckpt_path = ckpt_dir / f'{use_epoch}.ckpt'
        print(
            f'Warning: no ckpt at epoch {best_epoch}, using epoch {use_epoch}',
            file=sys.stderr,
        )

    if not ckpt_path.is_file():
        raise FileNotFoundError(f'Checkpoint not found: {ckpt_path}')

    return ckpt_path, best_epoch, best[metric]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', help='Encoder run directory, e.g. results/QM9_encoder/200')
    parser.add_argument('--metric', default='mae', help='Metric in val/stats.json (default: mae)')
    parser.add_argument('--max', action='store_true', help='Pick highest metric instead of lowest')
    args = parser.parse_args()

    ckpt_path, best_epoch, best_val = find_best_ckpt(
        args.run_dir, metric=args.metric, higher_is_better=args.max)
    print(
        f'Best epoch {best_epoch}, val {args.metric}={best_val:.6f} -> {ckpt_path}',
        file=sys.stderr,
    )
    print(ckpt_path)


if __name__ == '__main__':
    main()
