import json
import logging
import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def _json_safe(value):
    """Convert numpy scalars/containers to JSON-serializable Python types."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def save_nx_graphs(graphs, save_dir, prefix, max_samples=None):
    """Save networkx graphs as PNG files."""
    os.makedirs(save_dir, exist_ok=True)
    n = len(graphs) if max_samples is None else min(len(graphs), max_samples)
    saved = []
    for i in range(n):
        G = graphs[i]
        out_path = os.path.join(save_dir, f'{prefix}_sample_{i}.png')
        labels = nx.get_node_attributes(G, 'label')
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(6, 6))
        nx.draw(G, pos, with_labels=False, node_size=300)
        if labels:
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
        plt.tight_layout()
        plt.savefig(out_path, dpi=120)
        plt.close()
        saved.append(out_path)
    logging.info('Saved %d graph plots to %s', len(saved), save_dir)
    return saved


def save_generation_metrics(metrics, save_dir, split, epoch):
    """Persist generation quality metrics for one eval epoch."""
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f'{split}_epoch_{epoch:04d}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(_json_safe(metrics), f, indent=2)
    logging.info('Saved generation metrics to %s', path)
    return path
