# The Barnes–Gindikin Symbol at Fractional Rank

Frozen archive accompanying the paper

> **The Barnes–Gindikin Symbol at Fractional Rank: Continuation Without a
> Determinant Carrier, Positivity Without a Cone**
> John Zachary Fitch, Independent Researcher
> [![ORCID](https://img.shields.io/badge/ORCID-0009--0007--7953--1531-a6ce39?logo=orcid&logoColor=white)](https://orcid.org/0009-0007-7953-1531)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21713316.svg)](https://doi.org/10.5281/zenodo.21713316)

**DOI:** [10.5281/zenodo.21713316](https://doi.org/10.5281/zenodo.21713316) (all versions; resolves to the latest). Version DOIs: [10.5281/zenodo.22987448](https://doi.org/10.5281/zenodo.22987448) is `v1.1.1`, [10.5281/zenodo.22975670](https://doi.org/10.5281/zenodo.22975670) is `v1.1.0`, and [10.5281/zenodo.21713317](https://doi.org/10.5281/zenodo.21713317) is `v1.0.0`.
**Release:** [`v1.1.1`](https://github.com/johnzfitch/gindikin-rank/releases/tag/v1.1.1) (commit [`1a54cc0`](https://github.com/johnzfitch/gindikin-rank/commit/1a54cc0c53452538a44c8a26d7c9abcb338e1dbc)), the proofread September 2026 revision of the paper; its code and data are those of [`v1.1.0`](https://github.com/johnzfitch/gindikin-rank/releases/tag/v1.1.0) (commit [`4602947`](https://github.com/johnzfitch/gindikin-rank/commit/4602947d239e4cc2d9a0b6bd51679faf063225a5)). The July 2026 archive is [`v1.0.0`](https://github.com/johnzfitch/gindikin-rank/releases/tag/v1.0.0) (commit [`05f8878`](https://github.com/johnzfitch/gindikin-rank/commit/05f88789e6db22d5ba6413880f3c3ef4256078e6)).

## What changed in v1.1.1

* **The paper only.** A proofreading pass over the September 2026 revision: prose,
  typesetting and one citation title. No mathematics, statement, proof or number changed, and
  every theorem, proposition, lemma, corollary, equation and citation number is the same as in
  v1.1.0. `BUILD.md` lists each change. Still 60 pages.
* **Code and data are unchanged** from v1.1.0; the paper's supplementary-material note still
  points to v1.1.0, which remains accurate for the scripts.

## What changed in v1.1.0

* **The paper** is the September 2026 revision: revision 10 of the source (August 2026) with a
  typesetting and presentation pass. Theorem, proposition, lemma, corollary and equation numbers
  are unchanged from revision 10. It is typeset with Etch & Sketch v2.5; see `BUILD.md`.
* **New scripts.** `ancillary_census.py` emits the three quantitative receipts that Section 9.5
  leaves to the supplement. `verify_figure3.py` checks every claim displayed in Figure 3 and the
  collapse proposition (Proposition 8.7). `verify_positivity.py` is updated and now runs the
  Figure 3 suite as well.
* **Figures.** Figure 3 (cone strata) is new, so the positivity-loci and erosion-staircase figures
  are now Figures 4 and 5 (`figs/fig4-positivity-loci.pdf`, `figs/fig5-erosion-staircase.pdf`).
* **Housekeeping.** Compiled `__pycache__` files that v1.0.0 committed by mistake are removed.

---

## Quick start

```sh
python3 verify_positivity.py            # everything, ~30 s
python3 verify_positivity.py --quick    # core suite only
python3 verify_positivity.py --list     # what each suite covers
```

Every suite except `figure` needs only the standard library, and `--quick` runs
the core suite alone. The `figure` suite (`verify_figure3.py`) and
`ancillary_census.py` also need SymPy (`pip install sympy==1.14.0`), which
`figs/wallach_locus.py` uses for exact root-finding; without it the full run
ends with `FAILED SUITES: figure`.
Every positivity decision is made in exact arithmetic (`fractions.Fraction`,
or SymPy's exact algebraic numbers in the locus routine); no floating point
enters any of them. The one floating-point computation is the Remark 8.2
counterexample in `verify_figure3.py`, a concavity check done with mpmath at 30
digits. Expected final line:

```
ALL COMPUTATIONAL CLAIMS OF SECTIONS 8-11 VERIFIED
```

## What is verified, and what is not

`verify_positivity.py` recomputes, from scratch:

* every displayed positivity locus in Sections 8–11;
* every entry of Table 1, and the erosion degrees quoted in its caption;
* the erosion thresholds and stabilization degrees at integral defect;
* the ingredients of Theorem 10.8 (rational steps stabilize), separately;
* the conjugation duality of Theorem 11.1, cutoff by cutoff;
* the Borodin–Olshanski dictionary of Proposition 8.3;
* the finite-cutoff Gram determinant of Proposition 8.2;
* the separation corollary of Section 12.

Each locus is obtained by algebraic cell decomposition of the real line and
then checked against exhaustive enumeration of all partitions up to the
relevant degree. Nothing is sampled.

**Not verified here:** the analytic results — the Barnes regularization of
Section 2, the functional equations of Section 4, the growth and normalization
results of Section 7 — are proofs about meromorphic functions on `C^2` and are
not exercised by these scripts. Neither are the identifications with the
literature. The scripts check the stated computational instances; that is a
narrower claim than correctness of the paper.

## Layout

| path | contents |
|---|---|
| `gindikin-rank.tex`, `gindikin-rank.pdf` | paper source and compiled PDF |
| `verify_positivity.py` | **entry point**; runs everything below |
| `verify_section8.py` | core suite: pivots, chambers, band/cap/grid, ideals, staircase, duality, Table 1 |
| `verify_revision5.py` | negative-rank grid, defect factors, cap points, character indices |
| `verify_revision6.py` | Theorem 10.8 ingredients, falling-factorial lemma, ν=1 case |
| `verify_figure3.py` | every claim displayed in Figure 3, and Proposition 8.7 |
| `ancillary_census.py` | standalone: the three quantitative receipts Section 9.5 leaves to the supplement |
| `recompute_table.py` | standalone regeneration of Table 1 |
| `figs/` | figure sources; `make_figures.py` regenerates all five |
| `bfun/` | Bernstein–Sato inputs for the sextonionic cubic |
| `BUILD.md` | toolchain, revision history, and what each round changed |
| `MANIFEST.md` | SHA-256 of every file |
| `requirements.txt` | pinned environment |

## Reproducing the figures

Figure regeneration needs `matplotlib` **and** a LuaLaTeX installation with TeX
Gyre Schola and Libertinus Math, because figure labels are typeset through
matplotlib's PGF backend so that they match the document body exactly:

```sh
pip install -r requirements.txt
cd figs && python3 make_figures.py
```

## Rebuilding the paper

See `BUILD.md`. In short: two or three LuaLaTeX passes with the Etch & Sketch
LaTeX kit (v2.5), which this archive does not include. On a stock TeX Live the
one extra package needed is `texlive-luatex`, after which the font database
must be built once.

## Citing

See `CITATION.cff`. Please cite the paper; cite this archive by its DOI only
when referring to the code or data specifically.

## License

Paper: CC BY 4.0. Code: MIT. See `LICENSE`.
