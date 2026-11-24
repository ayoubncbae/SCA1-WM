# Validation contract

The browser is an independent numerical implementation of the exact frozen neural hybrid. Tests cover original source encoding, all504 CPU Python references, original saved held-out predictions, both genotypes/all14 types, neural source/time dependence, deterministic recursion, fixed-seed NB sampling, gamma/Poisson moments and rejection of unsupported conditions.

Tolerance: maximum absolute channel error<1e-4 across all4,000 output coordinates. Recorded error is approximately9.1e-7. CP10K is the expm1 of the second channel; the absolute tolerance in the manifest is0.05 because exponential conversion changes absolute-error scale. Tests do not assert a fictitious biological accuracy target.

The encoded state feeds the actual learned transition; three-seed decoded means are averaged after nonnegative clipping, matching Python. The selected correction is0.5. The statistical backbone is retained as part of the proposed architecture, not substituted for it. Direct and recursive paths differ; the browser does not force agreement.

Count sampling uses the original marginal Gamma-Poisson NB construction and training library pools. The browser PRNG is independently specified and reproducible, not bit-identical to NumPy. Its mean/variance are tested for small and large Poisson rates. Cells are not animal replicates.

Observed values exist only at5,12,18,24,30 weeks. Effect metrics use all2,000 matched genes and log2[(SCA1CP10K+0.1)/(WTCP10K+0.1)]. Correlation and R2 areNA for zero-variance GT. The deployed fold has one GT mouse/genotype/age, so displayed gene-effect metrics are descriptive, not inferential FDR discoveries. The site reports no generated DE p values or significant DEGs.

E2E checks cover navigation, actual execution, gene/program filtering, missing GT, route comparison, CSV export and mobile overflow. Screenshots are actual browser captures. Static asset HTTP integration substitutes for a server API because no backend is required.
