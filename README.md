# The Barnes–Gindikin Symbol at Fractional Rank

Frozen archive accompanying the paper

> **The Barnes–Gindikin Symbol at Fractional Rank: Continuation Without a
> Determinant Carrier, Positivity Without a Cone**
> John Zachary Fitch, Independent Researcher

**DOI:** _(assigned on deposit — replace this line with the Zenodo badge)_
**Commit:** _(replace with the tagged commit hash this archive was cut from)_

---

## Quick start

```sh
python3 verify_positivity.py            # everything, ~30 s
python3 verify_positivity.py --quick    # core suite only
python3 verify_positivity.py --list     # what each suite covers
```

No third-party package is required. Every positivity decision is made in exact
rational arithmetic (`fractions.Fraction`); no floating point enters any of
them. Expected final line:

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
* the Borodin–Olshanski dictionary of Proposition 8.2;
* the finite-cutoff Gram determinant of Proposition 8.3;
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
| `recompute_table.py` | standalone regeneration of Table 1 |
| `figs/` | figure sources; `make_figures.py` regenerates all four |
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

See `BUILD.md`. In short: LuaLaTeX against the vendored Etch & Sketch kit,
three passes. On a stock TeX Live the one extra package needed is
`texlive-luatex`, after which the font database must be built once.

## Citing

See `CITATION.cff`. Please cite the paper; cite this archive by its DOI only
when referring to the code or data specifically.

## License

Paper: CC BY 4.0. Code: MIT. See `LICENSE`.
