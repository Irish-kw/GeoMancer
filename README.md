
This is the official repository for NeurIPS 2025 Paper [Toward a Unified Geometry Understanding: Riemannian Diffusion Framework for Graph Generation and Prediction].


### Python environment setup

```bash
conda create -n geomancer python=3.9
conda activate geomancer
pip install -U pip setuptools wheel
pip install -r requirements.txt
```

Or use the helper script (recreates the `geomancer` env and installs dependencies):

```bash
bash setup_env.sh
```

You should install torch=2.3.1+cu118, torch-geometric=2.6.1 and pytorch-lightning=2.4.0.

### Running the code

All training scripts assume the **current working directory is the GeoMancer project root** (the folder that contains `pretrain.py`, `train_diffusion.py`, and `cfg/`).

```bash
cd GeoMancer
conda activate geomancer
```

#### Graph classification (Amazon Photo example)

```bash
# Step 1: pretrain a Riemannian autoencoder
bash cfg/photo-encoder.sh

# Step 2: train diffusion; update the checkpoint path in cfg/photo-diffusion.yaml first
bash cfg/photo-diffusion.sh
```

The default checkpoint path is set in `cfg/photo-diffusion.yaml` (`model.first_stage_config`). Replace it with your encoder checkpoint, e.g. `results/photo-encoder/0/ckpt/599.ckpt`.

To use other datasets or models, edit the corresponding yaml under `cfg/` or create your own config file.

#### Other example commands in `cfg/`

| Task | Pretrain encoder | Train diffusion |
|------|------------------|-----------------|
| Amazon Photo | `bash cfg/photo-encoder.sh` | `bash cfg/photo-diffusion.sh` |
| Cora (node) | `bash cfg/cora-node-encoder.sh` | `bash cfg/cora-node-diffusion.sh` |
| ZINC | `bash cfg/zinc-encoder.sh` | `bash cfg/zinc-diffusion_ddpm.sh` |
| QM9 | `bash cfg/QM9_encoder.sh` | `bash cfg/QM9_diffusion.sh` |
| QM9 (full pipeline) | — | `bash cfg/QM9_full_pipeline.sh` |
| QM9 (k-means) | `bash cfg/QM9_encoder.sh` | `bash cfg/QM9_diffusion_kmeans.sh` |

#### Graph generation (QM9 molecules)

**One-shot pipeline** (encoder → auto best ckpt → diffusion):

```bash
bash cfg/QM9_full_pipeline.sh
```

By default this pipeline runs encoder pretraining for `50` epochs.  
You can override it, e.g. `ENCODER_MAX_EPOCH=80 bash cfg/QM9_full_pipeline.sh`.

Or run the two steps manually:

```bash
cd GeoMancer
conda activate geomancer

# Step 1: pretrain the Riemannian autoencoder on QM9
bash cfg/QM9_encoder.sh

# Step 2: set model.first_stage_config in cfg/QM9_diffusion.yaml to your encoder ckpt, then:
bash cfg/QM9_diffusion.sh
```

To pick the best encoder checkpoint automatically after manual encoder training:

```bash
python scripts/find_best_ckpt.py results/QM9_encoder/200
```

Optional: `bash cfg/QM9_diffusion_kmeans.sh` for the k-means variant.

Note: `cfg/QM9_diffusion.yaml` must include `diffusion.cluster` (set to `1` for unconditional mode).

**Outputs during training** (every `train.eval_period` epochs, default 100):

| Path | Content |
|------|---------|
| `{run_dir}/generated_molecules/val/` | PNG visualizations of generated graphs (val split) |
| `{run_dir}/generated_molecules/test/` | PNG visualizations (test split) |
| `{run_dir}/generated_molecules/reference/` | Ground-truth test molecules for comparison |
| `{run_dir}/generation_metrics/val_epoch_XXXX.json` | Quantitative metrics per val eval |
| `{run_dir}/generation_metrics/test_epoch_XXXX.json` | Quantitative metrics per test eval |
| `{run_dir}/val/stats.json` | Aggregated stats including generation metrics |

Set `train.generation_viz_samples` (default 20) in yaml to control how many graphs are plotted each eval.

**How to judge generation quality**

Graph generation has no single ground-truth graph to match. Quality is measured by **distribution-level metrics** vs the test set:

| Metric | Meaning | Better when |
|--------|---------|-------------|
| **Validity** | Fraction of chemically valid molecules (RDKit) | Higher (→ 1.0) |
| **Relaxed Validity** | Valid after minor valence fixes | Higher |
| **Uniqueness** | Non-duplicate among generated set | Higher |
| **Novelty** | Not seen in training SMILES | Higher (unless memorization is desired) |
| **FCD_Test** | Fréchet ChemNet Distance vs test SMILES | **Lower** (closer to real distribution) |
| **NSPDK_MMD** | Graph statistic MMD vs test graphs | **Lower** (closer graph distribution) |

At startup the run logs **ground-truth baselines** (`Ground truth test FCD`, `Ground truth test NSPDK MMD`). Good models should beat random generation and approach those baselines on FCD/MMD while keeping high validity.

Also inspect PNGs in `generated_molecules/` and compare with `reference/test_ground_truth_*.png`.

### Cite
Welcome to cite our work!


