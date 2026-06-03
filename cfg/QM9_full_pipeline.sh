#!/usr/bin/env bash
# Train QM9 encoder, then diffusion using the best encoder checkpoint.
set -euo pipefail

cd "$(dirname "$0")/.."

SEED="${SEED:-0}"
ENCODER_RUN_DIR="${ENCODER_RUN_DIR:-results/QM9_encoder/200}"
METRIC="${METRIC:-mae}"
ENCODER_MAX_EPOCH="${ENCODER_MAX_EPOCH:-50}"

echo "=== Step 1/2: QM9 encoder pretrain ==="
python pretrain.py --cfg cfg/QM9_encoder.yaml --repeat 1 "seed" "$SEED" wandb.use False \
  optim.max_epoch "$ENCODER_MAX_EPOCH"

echo ""
echo "=== Resolving best encoder checkpoint ==="
ENCODER_CKPT="$(python scripts/find_best_ckpt.py "$ENCODER_RUN_DIR" --metric "$METRIC")"
echo "Using: $ENCODER_CKPT"

echo ""
echo "=== Step 2/2: QM9 unconditional diffusion ==="
python qm9_unconditional.py --cfg cfg/QM9_diffusion.yaml "seed" "$SEED" wandb.use False \
  diffusion.first_stage_config "$ENCODER_CKPT"

echo ""
echo "=== Pipeline complete ==="
echo "Encoder results: $ENCODER_RUN_DIR"
echo "Diffusion results: results/QM9_diffusion/"
