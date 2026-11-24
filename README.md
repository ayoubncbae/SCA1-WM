# SCA1-WM | Interactive Transcriptomic World Model

Cell-type-resolved simulation of transcriptomic states across SCA1 progression.

## What actually runs

This is **live browser inference of the proposed primary V7 neural model**, not a static prediction lookup or a renamed statistical model. It exports the frozen `grouped_1` three-seed ensemble (7,17,27), its residual PCA16 encoder, learned population-token MLP, conditional neural state transition, inverse-PCA decoder and training-fitted marginal NB sampler. Its inner-selected neural correction is **0.5**. The chronological statistical backbone remains a component of that neural hybrid.

The separate final all-animal model selected correction0; it is **not** the deployed neural checkpoint. No checkpoints, original training code, manuscripts or result files were modified. This checkpoint was chosen to demonstrate the implemented active neural architecture at the user's request, not by choosing a new winner from held-out scores. Global neural superiority is not established.

Private live demo: https://sca1-wm-transcriptomic-lab.starryboar67.chatgpt.site

## Local execution

Prerequisites: Node22+, npm, and a modern browser. Exported artifacts are included: no Python, GPU, original datasets or server are needed to run the app.

```powershell
cd web01
npm ci
npm run dev
```

Open **http://localhost:5173**. To serve the production build:

```powershell
npm run build
npm run preview
```

If Node is not globally installed, this workspace has an ignored checksum-verified runtime at `.tools/node-v22.15.0-win-x64`. In PowerShell prepend it to PATH:

```powershell
$env:PATH = (Join-Path (Get-Location) '.tools/node-v22.15.0-win-x64') + ';' + $env:PATH
npm run dev
```

## Reproduce verification

```powershell
npm run typecheck
npm run lint
npm test
npx playwright install chromium
npm run test:e2e
npm run build
```

An already installed Chrome/Edge browser can be used without downloading another browser:

```powershell
$env:PLAYWRIGHT_EXECUTABLE_PATH = 'your-installed-browser-executable'
npm run test:e2e
```

Playwright starts its own local server and saves real screenshots in `screenshots/`. Browser tests exercise desktop/mobile, neural simulation, GT handling, route comparison and downloads. `tests/fixtures/` contains original Python references for all504 type/genotype/age/route combinations and the actual saved held-out prediction arrays. Unit tests reproduce mean-expression channels with maximum absolute difference about9.1e-7, below the declared1e-4 tolerance. NB sampling is deterministic for a fixed JavaScript seed but intentionally does not promise NumPy-identical random streams.

## Reviewer walkthrough

1. Open Overview; enter **World model**.
2. Select Purkinje cell, SCA1, source5 weeks, target30 weeks and a route. The source anchor is training-derived; other source ages are not deployed.
3. Choose intermediate measured/unmeasured ages, genes or a documented program; set nuclei and seed; run.
4. Inspect actual computed states, WT/SCA1 expression, held-out measured references, disease effects, program coverage and the same-checkpoint residual-PC reference projection.
5. Inspect **Temporal routes** for actual direct/recursive schedule differences.
6. Download the displayed trajectories, observed reference, generated counts, effects and complete run metadata.
7. Read **Architecture & evidence** and exact hashes. The held-out distribution table keeps other historical folds explicitly separate; only grouped_1 matches the deployed checkpoint.

Example config: `{ "type":12,"genotype":"SCA1","sourceAge":5,"targetAge":30,"route":"recursive","steps":[12,18,24],"nuclei":32,"seed":97 }`.

## Scientific scope

Thirty source mice,20 training/validation mice and10 disjoint GT-reference mice for this fold;14 cell types;2,000 exact training-selected genes;five measured ages;two genotypes;query ages5,9,12,15,18,21,24,27,30. At a measured age there is one held-out mouse/genotype for this fold. This is animal-disjoint prediction at ages seen during training, not forward-age validation. Unmeasured ages have no GT. Recursive custom schedules are model predictions, with no intermediate experimental observations inferred. RNA re-entry/backward cycles are unavailable.

All data are author-provided derived mouse RNA/model artifacts. The code license grants **no additional data redistribution rights**. Keep hosted release owner-private until the researcher confirms appropriate public-data permissions. Original private paths, mouse IDs, credentials and raw nuclei are not served. Derived reference means and training population profiles are necessarily exported to support local model inference.

## Deployment

See `docs/DEPLOYMENT.md`. The site is static and needs no API/backend: `/health.json` describes the deployed inference mode. GitHub Pages can execute it in the browser. No Python service or API key is required. The included `.openai/hosting.json` is for the private Sites deployment; remove the project identity when creating an unrelated Site.

All new source, exported data, tests, docs, screenshots and packaging tools are inside `web01`. Re-exporting from the original study is optional and requires the original Python environment; see `docs/MODEL_PROVENANCE.md`.

## Upload the ZIP to your own GitHub repository

Extract SCA1_WM_WEB01_GITHUB_READY.zip into a fresh directory (without the private Sites .git metadata). Then run:

```text
git init
git add .
git commit -m "Add verified SCA1-WM neural web demo"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

The Pages workflow is manual-only (`workflow_dispatch`) so uploading source does not silently publish research data. Confirm model/data redistribution rights and configure Pages before triggering it.
