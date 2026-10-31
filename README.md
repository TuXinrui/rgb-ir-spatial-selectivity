# Rethinking Spatial Selectivity in RGB–IR Detection

Companion measurements and CPU figure-reproduction code for the manuscript **Rethinking Spatial Selectivity in RGB–IR Detection**.

Uniform aggregation preserves near-native clean detection accuracy in the measured systems. Both near-uniform ICAFusion attention and heterogeneous C²Former attention show a small native–uniform difference on DroneVehicle. The low replacement cost recurs for ICAFusion on FLIR3c and VEDAI, while the effect of removing the whole returned output varies across data and metrics.

## Quick start

Python **3.11 or later**. The reference environment uses Python 3.11, NumPy 2.4.4 and Matplotlib 3.11.0.

```sh
git clone https://github.com/TuXinrui/rgb-ir-spatial-selectivity.git
cd rgb-ir-spatial-selectivity
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python make_figures.py --check
python make_figures.py
```

The script verifies all four data files and writes Figures 1–3 as PDF, SVG and PNG in `figures/`. Inputs are located relative to the script, so it also works from another working directory. Use `--output-dir PATH` to choose the output location. Figure 2 is a deterministic diagram; Figures 1 and 3 use the released measurements.

This initial release reproduces the figures and provides recorded results for inspection. Training, detector inference and AP recomputation are outside its scope. It requires no model weights, dataset images or GPU.

## Main intervention measurements

The table reports **mAP50–95 differences in percentage points**, with the displayed direction **state minus native**. DroneVehicle uses the common oriented-box evaluator M; FLIR3c/VEDAI use their native horizontal-box evaluation. Each difference is within a checkpoint and protocol.

| Setting | UNIFORM − native (pp) | ZERO − native (pp) |
|---|---:|---:|
| DroneVehicle · ICAFusion · seed 2 | +0.0016 | -0.4243 |
| DroneVehicle · ICAFusion · seed 3 | +0.0010 | -0.2575 |
| DroneVehicle · C²Former · learned sampling | -0.2903 | -5.0135 |
| DroneVehicle · C²Former · reference sampling | -0.1788 | — |
| FLIR3c · ICAFusion · seed 1 | -0.0015 | -0.0549 |
| VEDAI · ICAFusion · ten-fold mean | -0.0038 | +0.0110 |

The C²Former uniform differences hold the sampling grid fixed; `L_ZERO` uses learned RGB sampling. VEDAI values are arithmetic means of ten fold-level AP values, using one selected checkpoint per fold. The JSON records preserve explicitly named contrasts such as `native_minus_uniform`; interpret their signs according to those field names.

**Native** keeps trained attention. **UNIFORM** replaces its post-softmax weights with equal weights on the current values, before attention dropout. **ZERO** zeros the projected returned cross-attention outputs while retaining the surrounding paths. C²Former's L/R states use learned/reference RGB sampling with the same trained checkpoint; IR uses its reference grid in both.

The DroneVehicle data also include separately trained concat+C3k2 configurations on the same YOLO platform as ICAFusion. C²Former is a local two-stream ResNet-50/S²A-Net adaptation. ICAFusion cross-data runs use YOLO11m at 640 on FLIR3c and YOLO11s at 1,024 on VEDAI.

## Released files and units

| File | Contents |
|---|---|
| [dv_results.json](data/dv_results.json) | 13 DroneVehicle states, 10 contrasts, full recorded M values and labelled T18 companions; source protocol identity and evaluator description |
| [cross_dataset_results.json](data/cross_dataset_results.json) | FLIR3c three states; all ten VEDAI folds and three states each; selection epochs, seeds, splits, aggregates, HBB settings and intervention definitions |
| [icafusion_heads.csv](data/icafusion_heads.csv) | 96 head records indexed by seed, block, branch and head |
| [c2former_heads.csv](data/c2former_heads.csv) | 90 head records indexed by stage, direction and head |
| [make_figures.py](make_figures.py) | Figure generation and input identity checks |

AP fields labelled `fraction`, including `states_fraction`, `means_fraction` and fold-state values, are on a 0–1 scale. Fields ending in `_percent` are on a 0–100 scale; `_pp` fields are percentage-point differences. The displayed cross-data table is stored under `cross_dataset_table`, independently of manuscript table numbering.

Native V/H ratios are `mean(S_i) / mean(E_i)`: for each image and head, S is squared feature energy after within-channel spatial centering, and E is uncentered squared energy. Each diagnostic uses 256 training images. Figure 3 retains all 372 V/H observations and computes group median/IQR on the raw ratios before displaying them on the shared logarithmic axis.

The M evaluator uses highest-IoU matching over all same-class ground truths, a strict threshold comparison, duplicate-hit rejection and VOC all-point AP at 0.50:0.05:0.95. The HBB settings are in `evaluation_hbb`. C²Former T18 companion entries marked `HISTORICAL_4DP` are historical rounded values; the figure uses the full-precision M fields.

## VEDAI identity

VEDAI pairs RGB with **near-infrared**, whereas DroneVehicle and FLIR3c pair RGB with thermal infrared. This release uses the recorded local eight-class HBB configuration and the official ten folds: 980 training, 109 inner-validation and 121 outer-test images per fold; the test union is 1,210 disjoint images.

Local numeric IDs 0–7 map to official IDs **1, 2, 11, 4, 5, 10, 9, 31**: car, truck, pickup, tractor, camping car, other vehicle, van and plane. The old YAML display names are retained as `original_yaml_display_names`; `classes` contains the reconstructed semantics. Numeric class IDs and AP values are unchanged.

The `annotation_reconstruction` record gives the official archive URLs/hashes, exclusions and fixed geometry rule. All 3,517 retained boxes match exactly after axis-aligned conversion, normalization by 1,024 and clipping the two center coordinates while preserving width/height; 10 boxes have clipped centers. The official folds omit 36 annotated images (63 boxes); 177 boxes from the excluded classes are outside the retained task. The historical converter was unavailable, so this mapping was reconstructed from the official annotations.

## Provenance and versioning

Scores, seeds, epochs and CSV scientific columns retain their original precision. Public packaging replaces internal filesystem paths with opaque `record_id` / `source_record` identifiers, retains source SHA256 values and field pointers, and corrects the VEDAI class-name metadata. These record IDs identify archived measurements; they are not download URLs. The script pins the hashes of the released files.

Original recorded snapshot identities, before public metadata normalization:

| Released file | Original snapshot SHA256 |
|---|---|
| `dv_results.json` | `47a435672993e0300d3bd40fcd28d1b8305ddb80a96ea5aa79d3806c0bda7ad4` |
| `cross_dataset_results.json` | `f9befbc5a720103893588b8c3d02ee25354da18464ae6ec008ffeb9c26033fdc` |
| `icafusion_heads.csv` | `9cc9f8ac3ee1c98e369a316d901aae5c8c80920062f1877435f7eaf69dc61786` |
| `c2former_heads.csv` | `21228d8012158ee7fd67d2ed2a3ae0e200a02ae3d2625bd2540fefa1952ddf37` |

Use the `v0.1.0` tag for a fixed snapshot. This repository is a companion-material release; it does not indicate journal acceptance. Model code, checkpoints, original images and annotations are not redistributed here.

## Sources and license

- [ICAFusion](https://doi.org/10.1016/j.patcog.2023.109913)
- [C²Former](https://doi.org/10.1109/TGRS.2024.3376819)
- [VEDAI dataset and annotations](https://downloads.greyc.fr/vedai/), [dataset paper](https://doi.org/10.1016/j.jvcir.2015.11.002)

The code, documentation and released measurement files in this repository use the [MIT License](LICENSE). NumPy and Matplotlib retain their own licenses. Please cite the original method and dataset papers when building on those resources.
