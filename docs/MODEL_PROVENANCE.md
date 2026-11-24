# Exact deployed model

- Primary V7, frozen `grouped_1`, selected residual weight0.5.
- Three seeds7/17/27; latent16; width32; depth1;20 training+validation animals and10 held-out animals;2,000 genes selected inside original training.
- Residual observation PCA and moment tokens; learned type embedding/token MLP/damped latent transition; fixed inverse PCA correction; Gaussian age backbone bandwidth3 weeks and genotype shrinkage0.25; marginal count-NB decoder.
- Direct: original source → target, one transition step. Recursive: previous predicted state → next selected age, four transition substeps per segment. Fixed context tokens; no RNA decoding/re-encoding handoff. Custom multi-segment schedules are new deterministic queries of the frozen transition, not new model fits or independently validated intermediate states.
- `public/model-manifest.json` includes checkpoint/preprocessor/panel hashes and all supported features. `assets/model-data.json` binds the neural weights to those identities; its hash is in the manifest. Binary model vectors are verified with SHA256 before inference.
- `public/verified-predictions/observed-*.json` uses only the fold's10 disjoint test mice, not training references. Each type/genotype/measured-age condition has one target mouse. Source encoding uses the earliest training populations. The latter are not the plotted held-out GT points.
- `shared-atlas.json` uses the **same deployed encoder and gene panel**, first two training-fitted residual-PC coordinates; generated reference RNA uses the same frozen neural ensemble. No new UMAP fitting, other checkpoint embedding or projection of each live sample is implied.
- Historical evaluation data retain per-fold labels. No metric from another fold or all-animal checkpoint is assigned to a current run.

Optional re-export, from the original project root using its scientific Python environment:

```text
python web01/scripts/export_verified_predictions.py --project-root .
python web01/scripts/validate_model_outputs.py
```

The exporter reads original artifacts and writes only inside web01. No original checkpoint/source/results are mutated. Runtime JavaScript needs only the included exported assets.
