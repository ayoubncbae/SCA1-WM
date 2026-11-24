# SCA1-WM WEB01 validation

Status: **PASS â€” working active-neural browser application**.

## Model identity

Frozen primary V7 `grouped_1`, seeds7/17/27, residual latent16, width32, depth1, selected correction0.5. This is the actual proposed neural hybrid; the zero-correction all-animal selection was not relabelled as neural. No original training code, results, manuscript or checkpoint was written. No model retraining was required.

## Executed checks

| Check | Result |
|---|---|
| Dependency installation | PASS; package-lock included |
| TypeScript type checking | PASS |
| ESLint | PASS; zero errors/warnings |
| Production Vite build | PASS |
| Python export validation | PASS; original checkpoints loaded on CPU |
| Unit/scientific tests | **13 passed** |
| Playwright workflow/static integration tests | **5 passed** |
| Original Python neural reference comparison | **504/504 conditions pass** |
| Saved original held-out comparison | PASS |
| Maximum absolute4,000-channel error | **9.0831e-7**, tolerance1e-4 |
| Source encoding | All28 type/genotype anchors match original encoder |
| Active neural contribution | Outputs differ from backbone and respond to source/time changes |
| RNA sampling | Fixed-seed reproducibility; NB moments tested |
| All14 types and both genotypes | PASS |
| Unsupported ages/routes/schedules | Rejected |
| Measured GT support | Only5/12/18/24/30; one held-out mouse/genotype/age |
| Downloads | CSV values equal run arrays; CSV,SVG andPNG browser downloads tested |
| Responsive browser QA | Desktop and390px mobile pass; screenshots saved |

Browser tests used installed Microsoft Edge/Chromium headlessly via Playwright. The optional separate Playwright Chromium download hit a local directory-lock timeout; the complete browser suite passed on the installed compatible browser. There is no Python API: health and static-model endpoints were integration-tested instead. The chart library emits a non-fatal bundle-size warning (~1.04MB minified/~343KB gzip); production build succeeds.

## Screenshots

`screenshots/simulator-desktop.png`, `routes-desktop.png`, `methods-desktop.png`, `overview-mobile.png`, `biology-mobile.png`. These are actual running browser captures, not mockups. Any final additional production screenshots are labelled separately.

## Scope limits

The active model has an age statistical backbone as one component, but source encoding, learned token context, latent dynamics and inverse-PCA residual decoding all execute with a nonzero correction. Custom recursive schedules are composed frozen-model queries, not independently validated intermediate-age observations. The stored state plot uses the same deployed residual PCA rather than another checkpoint's UMAP. RNA count noise uses a reproducible browser PRNG, not NumPy's bit stream. Full causal neurodegeneration, arbitrary uploaded-source inference, RNA re-entry, reverse cycles and superiority over baselines are not claimed. See docs/DEMO_LIMITATIONS.md.

Deployment results, when confirmed, are recorded separately in docs/DEPLOYMENT_RESULT.json. An expected URL is not a deployment-success claim. The GitHub-ready ZIP excludes tools, caches, credentials, node_modules and Git metadata.

## Confirmed private deployment

The native Sites deployment succeeded at https://sca1-wm-transcriptomic-lab.starryboar67.chatgpt.site . Deployment/version/commit identifiers are in docs/DEPLOYMENT_RESULT.json. Owner-private audience is preserved. The built production app additionally passed live browser inference at its static production preview, with no browser page errors (docs/PRODUCTION_BROWSER_CHECK.json).
