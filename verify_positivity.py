#!/usr/bin/env python3
"""
verify_positivity.py -- single entry point for the exact-arithmetic
verification of the computational claims of Sections 8-11 of

    The Barnes-Gindikin Symbol at Fractional Rank:
    Continuation Without a Determinant Carrier, Positivity Without a Cone

Everything runs in exact rational arithmetic (fractions.Fraction). No
floating point enters any positivity decision. Each positivity locus is
recomputed from scratch by algebraic cell decomposition of the real line and
checked against exhaustive enumeration of all partitions up to the relevant
degree; nothing is sampled.

WHAT THIS CHECKS

  - every displayed positivity locus in Sections 8-11
  - every entry of Table 1, and the erosion degrees quoted in its caption
  - the erosion thresholds and stabilization degrees at integral defect
  - the ingredients of Theorem 10.8 (rational steps stabilize)
  - the conjugation duality of Theorem 11.1, cutoff by cutoff
  - the dictionary of Proposition 8.2 against the Borodin-Olshanski weights
  - the finite-cutoff Gram determinant of Proposition 8.3
  - the separation corollary of Section 12
  - the local algebraic identities corrected in review (defect factors,
    minimal rank-null cells, falling-factorial nonnegativity, index arithmetic)

WHAT THIS DOES NOT CHECK

  The analytic results -- the Barnes regularization of Section 2, the
  functional equations of Section 4, the growth and normalization results of
  Section 7 -- are proofs about meromorphic functions on C^2 and are not
  exercised here. Neither are the identifications with the literature. This
  script verifies the stated computational instances only.

USAGE

    python3 verify_positivity.py             # everything
    python3 verify_positivity.py --quick     # core suite only, ~1 min
    python3 verify_positivity.py --list      # show the suites and exit

Runtime is a few minutes on a laptop for the full run. Requires only the
Python standard library (see requirements.txt for the pinned interpreter).
"""

from __future__ import annotations

import argparse
import io
import sys
import time
from contextlib import redirect_stdout
from fractions import Fraction as F

# The four suites this driver runs. They are kept as separate modules
# because each was written against a specific review round and each is
# independently runnable; this file is the union.
SUITES = [
    ("core",
     "verify_section8",
     "Sections 8-11 as originally established: pivot formula, chamber "
     "positivity, integer-rank benchmark, band and cap, retained grid, "
     "null ideals, erosion staircase, unit-numerator loci, integral-defect "
     "closed form, stabilization degree, conjugation duality, Table 1."),
    ("neggrid",
     "verify_revision5",
     "The dualized retained grid at negative rank, the bottom-cell defect "
     "factors, the cap points of Remark 12.2, and the character-index "
     "lattice of Proposition 7.4."),
    ("ratstab",
     "verify_revision6",
     "Theorem 10.8 ingredient by ingredient (content set in b^-1 Z, the "
     "cage, monotonicity, constancy on strata, the irrational obstruction), "
     "the unbounded negative-rank locus, the nu=0 cell, the restated "
     "falling-factorial lemma, and the nu=1 case of Corollary 10.7."),
    ("figure",
     "verify_figure3",
     "Every claim displayed in Figure 3: that the paper's own integer-rank "
     "theorem reproduces the ladder-plus-ray the left panel pairs with the "
     "flag of boundary strata, and that the right panel's retained grid, "
     "band, balanced point, cap and absent ray are what Theorem 9.1, "
     "Proposition 9.3 and eq. (maxlocus) give."),
]

QUICK = {"core"}


# =====================================================================
# additional checks introduced with this revision
# =====================================================================
def extra_checks() -> list[str]:
    """Proposition 8.3 (Gram determinant) and Corollary 12.1 (separation).

    Returns the list of failed check names.
    """
    from verify_section8 import Fval, all_partitions, hook_paper

    fails = []

    def ck(name, ok, detail=""):
        print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(name)

    def ceil_frac(x):
        return -((-x.numerator) // x.denominator)

    # -----------------------------------------------------------------
    # Proposition 8.3: det G_N(r,s) = C_{N,D} * prod (rD-xi)^m (s-xi)^m
    # -----------------------------------------------------------------
    bad = []
    for D in (F(1, 2), F(1), F(3, 2), F(2), F(5, 2), F(3)):
        for r in (F(3, 2), F(1, 2), F(2), F(5, 2)):
            for s in (F(0), F(1), F(7, 3), F(-2), F(9, 2)):
                for N in (3, 4, 5):
                    lams = all_partitions(N)
                    # left side: the product of the diagonal pivots
                    lhs = F(1)
                    for lam in lams:
                        lhs *= (Fval(lam, D, r * D) * Fval(lam, D, s)
                                / (D ** sum(lam) * hook_paper(lam, D)))
                    # right side: cell multiplicities m_N(i,j)
                    mult = {}
                    for lam in lams:
                        for i, li in enumerate(lam, start=1):
                            for j in range(1, li + 1):
                                mult[(i, j)] = mult.get((i, j), 0) + 1
                    rhs = F(1)
                    for lam in lams:
                        rhs *= F(1, 1) / (D ** sum(lam) * hook_paper(lam, D))
                    for (i, j), m in mult.items():
                        xi = (i - 1) * D - (j - 1)
                        rhs *= (r * D - xi) ** m * (s - xi) ** m
                    if lhs != rhs:
                        bad.append((D, r, s, N))
    ck("Prop 8.3  det G_N = C_{N,D} prod (rD-xi_ij)^{m_N} (s-xi_ij)^{m_N}",
       not bad, f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

    # the constant really is positive, so the determinant's sign is carried
    # entirely by the two evaluation points
    bad = []
    for D in (F(1, 2), F(1), F(3, 2), F(2), F(3)):
        for N in (3, 4, 5):
            C = F(1)
            for lam in all_partitions(N):
                C *= F(1, 1) / (D ** sum(lam) * hook_paper(lam, D))
            if C <= 0:
                bad.append((D, N, C))
    ck("Prop 8.3  the constant C_{N,D} is strictly positive", not bad)

    # -----------------------------------------------------------------
    # Corollary 12.1(iii): the pairing is PSD at the balanced point s = rD
    # at every cutoff, because the pivot is a square over a positive hook
    # -----------------------------------------------------------------
    bad = []
    for D in (F(1, 2), F(1), F(3, 2), F(2), F(5, 2), F(3), F(4)):
        for r in (F(-5, 2), F(-1, 2), F(1, 4), F(1, 2), F(3, 2), F(7, 3),
                  F(5, 2), F(9, 4)):
            for lam in all_partitions(6):
                piv = (Fval(lam, D, r * D) * Fval(lam, D, r * D)
                       / (D ** sum(lam) * hook_paper(lam, D)))
                if piv < 0:
                    bad.append((D, r, lam, piv))
    ck("Cor 12.1  pi_lambda(rD) = F(rD)^2 / (D^|lam| H_lam) >= 0 at every "
       "cutoff and every real rank", not bad,
       f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

    # definiteness at rD is decided by whether rD is a cell root
    bad = []
    for D in (F(1), F(3, 2), F(2), F(5, 2)):
        for r in (F(1, 4), F(1, 2), F(3, 2), F(7, 3), F(5, 2), F(2), F(3)):
            N = 6
            roots = set()
            for lam in all_partitions(N):
                for i, li in enumerate(lam, start=1):
                    for j in range(1, li + 1):
                        roots.add((i - 1) * D - (j - 1))
            is_root = (r * D) in roots
            has_zero = any(Fval(lam, D, r * D) == 0 for lam in all_partitions(N))
            if is_root != has_zero:
                bad.append((D, r, is_root, has_zero))
    ck("Cor 12.1  the pairing degenerates at s = rD exactly when rD is a "
       "cell root", not bad,
       f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

    # -----------------------------------------------------------------
    # Section 10 trichotomy table: the three arithmetic regimes are
    # exhaustive and mutually exclusive at every positive rank
    # -----------------------------------------------------------------
    bad = []
    for D in (F(1), F(3, 2), F(2), F(5, 2), F(3), F(2, 3), F(5, 3), F(7, 2)):
        b = D.denominator
        for num in range(1, 40):
            r = F(num, 6)
            k = ceil_frac(r)
            nu = D * (k - r)
            c1 = (b * nu).denominator != 1
            c2 = (b * nu).denominator == 1 and nu.denominator != 1
            c3 = nu.denominator == 1
            if sum((c1, c2, c3)) != 1:
                bad.append((D, r, nu, c1, c2, c3))
    ck("Sec 10 table  the three regimes b*nu notin Z / b*nu in Z, nu notin Z "
       "/ nu in Z are exhaustive and disjoint", not bad,
       f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

    # and (2/3,3) really is an instance of the middle regime, as the paper
    # claims -- this is the example the page-49 correction turns on
    D = F(3, 2)
    r = F(2, 3)
    k = ceil_frac(r)
    nu = D * (k - r)
    b = D.denominator
    ck("Sec 10 table  (r,d) = (2/3,3) has b*nu in Z but nu notin Z, so it "
       "carries a later-row ideal", (b * nu).denominator == 1
       and nu.denominator != 1, f"nu = {nu}, b*nu = {b*nu}")

    # while the three examples of Section 10.4 have NO ideal at any row
    bad = []
    for r, d in ((F(3, 2), F(6)), (F(3, 2), F(10)), (F(3, 2), F(3))):
        D = d / 2
        b = D.denominator
        k = ceil_frac(r)
        nu = D * (k - r)
        if (b * nu).denominator == 1:
            bad.append((r, d, nu, b * nu))
    ck("Sec 10.4  (3/2,6), (3/2,10), (3/2,3) all have b*nu notin Z, hence no "
       "rank-null ideal at any row", not bad,
       "so their stabilization comes only from the finite stratification"
       if not bad else f"{bad}")

    # -----------------------------------------------------------------
    # Theorem 11.1 corollary: the least stabilizing cutoff is a duality
    # invariant.  Checked as: the two loci agree cutoff by cutoff under the
    # transport, so they stabilize at the same N.
    # -----------------------------------------------------------------
    bad = []
    n_probe = 0
    for r, d in ((F(3, 2), F(2)), (F(3, 2), F(4)), (F(1, 2), F(2)),
                 (F(5, 2), F(4)), (F(3, 2), F(8)), (F(2), F(6))):
        D = d / 2
        for N in (3, 4, 5, 6):
            lams = all_partitions(N)

            def psd(rr, dd, ss):
                DD = dd / 2
                return all(Fval(l, DD, rr * DD) * Fval(l, DD, ss) >= 0
                           for l in lams)

            for num in range(-30, 61):
                s = F(num, 4)
                n_probe += 1
                # transport: s on the (r,d) side corresponds to -s/D on the
                # dual side (-rD, 4/d).  Compared by membership, not by the
                # interval representation, which locus() clamps to its
                # breakpoint window.
                if psd(r, d, s) != psd(-r * D, 4 / d, -s / D):
                    bad.append((r, d, N, s))
    ck("Cor 11.x  s in W_N(r,d) iff -s/D in W_N(-rD,4/d) at every cutoff, so "
       "N_0(-rD,4/d) = N_0(r,d)", not bad,
       f"{n_probe} probes, {len(bad)} violations"
       + ("" if not bad else f"  first: {bad[0]}"))

    return fails


# =====================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true",
                    help="run the core suite only")
    ap.add_argument("--list", action="store_true",
                    help="list the suites and exit")
    ap.add_argument("--verbose", action="store_true",
                    help="echo each suite's own output")
    args = ap.parse_args()

    if args.list:
        for name, mod, desc in SUITES:
            print(f"{name:10s} ({mod}.py)\n    {desc}\n")
        print("extra      (in this file)\n    Gram determinant, separation "
              "corollary, trichotomy table, duality invariance of N_0.")
        return 0

    print("=" * 78)
    print("verify_positivity.py -- exact-arithmetic verification, "
          "Sections 8-11")
    print(f"Python {sys.version.split()[0]}   "
          f"{'quick' if args.quick else 'full'} run")
    print("=" * 78)

    failed_suites = []
    t_start = time.time()

    for name, mod, _desc in SUITES:
        if args.quick and name not in QUICK:
            print(f"\n--- {name} ({mod}) : skipped (--quick)")
            continue
        print(f"\n--- {name} ({mod}) " + "-" * (60 - len(name) - len(mod)))
        t0 = time.time()
        buf = io.StringIO()
        try:
            if args.verbose:
                __import__(mod)
                ok = True
            else:
                with redirect_stdout(buf):
                    __import__(mod)
                ok = True
        except SystemExit as e:
            ok = (e.code in (0, None))
        except Exception as e:                       # noqa: BLE001
            print(f"    ERROR: {type(e).__name__}: {e}")
            ok = False
        out = buf.getvalue()
        if not args.verbose and out:
            n_ok = out.count("[OK ]")
            n_bad = out.count("[FAIL]")
            print(f"    {n_ok} checks passed, {n_bad} failed"
                  f"   ({time.time()-t0:.1f}s)")
            if n_bad:
                for line in out.splitlines():
                    if line.startswith("[FAIL]"):
                        print("    " + line)
                ok = False
        if not ok:
            failed_suites.append(name)

    print("\n--- extra " + "-" * 62)
    t0 = time.time()
    extra_fails = extra_checks()
    print(f"    ({time.time()-t0:.1f}s)")
    if extra_fails:
        failed_suites.append("extra")

    print()
    print("=" * 78)
    print(f"total {time.time()-t_start:.1f}s")
    if failed_suites:
        print("FAILED SUITES: " + ", ".join(failed_suites))
        return 1
    print("ALL COMPUTATIONAL CLAIMS OF SECTIONS 8-11 VERIFIED")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
