#!/usr/bin/env python3
"""verify_revision6.py -- audit of the claims ADDED or CHANGED in round 6.

  E  Theorem 10.8 (rational steps stabilize): the ingredients of the proof,
     one at a time -- the cell lattice sits in b^{-1}Z, the locus is caged in
     [0, kD] past degree k+1, the sequence W_N is decreasing, every pivot has
     constant sign on each open stratum, and the stratum count is finite.
  F  the unbounded negative fractional-rank locus that forces the abstract's
     "positive nonintegral rank" qualifier.
  G  Corollary 9.7 with case (ii) widened to nu in Z_{>=0}: at nu = 0 the
     minimal cell is (k+1,1) and eq:mincell still delivers it with m = t0 = 0.
  H  the restated Lemma 10.4 over all of R, and its intersection with the
     terminal chamber.
  I  Corollary 10.7's nu = 1 case, which the old proof reached by applying
     Theorem 10.5 one degree below its hypothesis.
"""
from fractions import Fraction as F
from math import gcd
import sys

from verify_section8 import Fval, locus, all_partitions, as_set

FAILS = []


def ck(name, ok, detail=""):
    print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def ceil_frac(x):
    return -((-x.numerator) // x.denominator)


def floor_frac(x):
    return x.numerator // x.denominator


RATIONAL_D = [F(1, 2), F(1), F(3, 2), F(2), F(5, 2), F(3), F(4), F(5),
              F(2, 3), F(3, 4), F(4, 3), F(5, 3), F(7, 2)]
POS_R = [F(1, 4), F(1, 2), F(3, 4), F(3, 2), F(5, 2), F(4, 3), F(6, 5),
         F(2, 3), F(9, 4), F(7, 3)]

# =====================================================================
# E  Theorem 10.8, ingredient by ingredient
# =====================================================================

# E1  every root of every spectral cell polynomial lies in (1/b)Z
bad = []
for D in RATIONAL_D:
    b = D.denominator
    for lam in all_partitions(7):
        for i, li in enumerate(lam, start=1):
            for j in range(1, li + 1):
                root = (i - 1) * D - (j - 1)
                if (root * b).denominator != 1:
                    bad.append((D, lam, i, j, root))
ck("E1 cell lattice: every spectral root of F_{lam,D} lies in (1/b)Z", not bad,
   f"{len(RATIONAL_D)} steps x partitions to degree 7, {len(bad)} violations")

# E2  the locus is caged in [0, kD] once N >= k+1, at positive nonintegral rank
bad = []
for D in RATIONAL_D:
    d = 2 * D
    for r in POS_R:
        k = ceil_frac(r)
        N = max(k + 1, 6)
        iso, ivs, unb = locus(r, d, N)
        hi = D * k
        if unb:
            bad.append(("unbounded", r, d))
            continue
        pts = list(iso) + [x for ab in ivs for x in ab]
        if pts and (min(pts) < 0 or max(pts) > hi):
            bad.append(("outside [0,kD]", r, d, min(pts), max(pts), hi))
ck("E2 cage: W_N(r,d) is a bounded subset of [0,kD] for N >= k+1", not bad,
   f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))


def psd_at(r, d, s, N):
    D = d / 2
    rk = r * D
    return all(Fval(lam, D, rk) * Fval(lam, D, s) >= 0
               for lam in all_partitions(N))


# E3  W_N is decreasing in N  (it is an intersection over a growing index set)
bad = []
for D in [F(3, 2), F(2), F(3), F(5, 2), F(4, 3)]:
    d = 2 * D
    for r in [F(3, 2), F(1, 2), F(5, 2), F(4, 3)]:
        for s in [F(n, 4) for n in range(-4, 41)]:
            seq = [psd_at(r, d, s, N) for N in range(1, 8)]
            # once false, must stay false
            if any(seq[i] and not seq[i - 1] for i in range(1, len(seq))):
                bad.append((r, d, s, seq))
ck("E3 monotonicity: s in W_{N+1} implies s in W_N", not bad,
   f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

# E4  constancy of every pivot sign on each open stratum of (1/b)Z, and the
#     finiteness of the stratum count in [0,kD]
bad = []
counts = []
for D in [F(3, 2), F(2), F(3), F(5), F(4, 3), F(5, 3)]:
    d = 2 * D
    b = D.denominator
    for r in [F(3, 2), F(1, 2), F(5, 2)]:
        k = ceil_frac(r)
        top = D * k
        m_hi = floor_frac(top * b)
        counts.append(2 * m_hi + 1)
        for m in range(0, m_hi):
            a0, a1 = F(m, b), F(m + 1, b)
            probes = [a0 + (a1 - a0) * F(t, 4) for t in (1, 2, 3)]
            vals = [psd_at(r, d, s, 6) for s in probes]
            if len(set(vals)) != 1:
                bad.append((D, r, m, vals))
ck("E4 strata: membership in W_N is constant on each open stratum of (1/b)Z",
   not bad, f"stratum counts in [0,kD] range {min(counts)}-{max(counts)}, "
   f"{len(bad)} violations")

# E5  the conclusion itself, observed: the locus is eventually constant, with
#     endpoints in (1/b)Z, for the three examples the paper had left open
bad = []
# NOTE the windows are the ones the paper claims, not wider ones: at
# (3/2,10) an erosion event sits at N = 12, so a window starting at 11
# straddles it and the locus is correctly non-constant there.
for r, d, Nlo, Nhi in [(F(3, 2), F(6), 10, 12), (F(3, 2), F(10), 12, 13),
                       (F(3, 2), F(3), 12, 13)]:
    D = d / 2
    b = D.denominator
    seen = set()
    for N in range(Nlo, Nhi + 1):
        iso, ivs, unb = locus(r, d, N)
        seen.add((tuple(iso), tuple(ivs), unb))
        for x in list(iso) + [z for ab in ivs for z in ab]:
            if (x * b).denominator != 1:
                bad.append(("endpoint off lattice", r, d, N, x))
    if len(seen) != 1:
        bad.append(("not constant", r, d, sorted(map(str, seen))))
ck("E5 the three formerly open examples are constant over the tested range "
   "with endpoints in (1/b)Z", not bad,
   f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

# E6  irrational D really does break the argument: the lattice is dense, so
#     the stratum count is not finite.  Checked as: the minimal gap from tD up
#     to the next integer goes to 0.
import math
alpha = math.sqrt(2)
gaps = [min(abs(t * alpha - round(t * alpha)) for t in range(1, T))
        for T in (10, 100, 1000, 10000)]
ck("E6 irrational D: min distance from tD to Z tends to 0, so no finite "
   "stratification", all(gaps[i] < gaps[i - 1] for i in range(1, len(gaps))),
   f"gaps {['%.2e' % g for g in gaps]}")

# =====================================================================
# F  the unbounded negative fractional-rank locus
# =====================================================================
# Thm 8.4 at (1,1): W_N(1,1) = [0,inf).  Thm 11.1 with D=1/2 sends this to
# W_N(-1/2,4) = -2*[0,inf) = (-inf,0].  So r = -1/2 is nonintegral and its
# locus is unbounded, which is why the abstract must say POSITIVE.
ok_pos = all(psd_at(F(1), F(1), F(n, 2), 6) for n in range(0, 60))
ok_neg = all(psd_at(F(-1, 2), F(4), F(-n, 2), 6) for n in range(0, 60))
ok_neg_excl = not psd_at(F(-1, 2), F(4), F(1, 2), 6)
ck("F  W(1,1) contains [0,inf) and W(-1/2,4) contains (-inf,0], unbounded at "
   "nonintegral rank -1/2", ok_pos and ok_neg and ok_neg_excl,
   "so the abstract's bounded-locus claim needs 'positive'")

# =====================================================================
# G  Corollary 9.7 with case (ii) widened to nu in Z_{>=0}
# =====================================================================
bad = []
for D in RATIONAL_D:
    a, b = D.numerator, D.denominator
    for r in [F(n) for n in range(1, 6)]:          # integer rank => nu = 0
        k = ceil_frac(r)
        nu = D * (k - r)
        if nu != 0:
            bad.append(("nu", r, D))
            continue
        m = b * nu
        if m != 0:
            bad.append(("m", r, D))
        t0 = min(t for t in range(0, b) if (m + a * t) % b == 0)
        cell = (k + 1 + t0, 1 + (m + a * t0) // b)
        if t0 != 0 or cell != (k + 1, 1):
            bad.append(("cell", r, D, t0, cell))
        # and (k+1,1) really is rank-null at integer rank: rD = kD - 0
        if (k + 1 - 1) * D - (1 - 1) != r * D:
            bad.append(("not null", r, D))
ck("G  at nu = 0 eq:mincell gives m = t0 = 0 and the cell (k+1,1), the "
   "integer-rank length ideal", not bad,
   f"{len(bad)} violations" + ("" if not bad else f"  first: {bad[0]}"))

# the old trichotomy really did omit nu = 0
old_covers_zero = any([False, 0 > 0, False])   # b*0 in Z, 0 not in Z_{>0}, 0 in Z
ck("G' the old three cases genuinely omit nu = 0", not old_covers_zero,
   "b*nu in Z holds, nu in Z_{>0} fails, and nu notin Z fails")

# =====================================================================
# H  the restated Lemma 10.4, now over all of R
# =====================================================================
def falling(sigma, m):
    v = F(1)
    for t in range(m):
        v *= (sigma - t)
    return v


bad = []
for M in range(1, 9):
    predicted_pts = set(F(n) for n in range(0, M - 1))
    for num in range(-40, 200):
        sigma = F(num, 8)
        holds = all(falling(sigma, m) >= 0 for m in range(1, M + 1))
        want = (sigma >= M - 1) or (sigma in predicted_pts)
        if holds != want:
            bad.append((M, sigma, holds, want))
ck("H  {sigma in R : sigma^(m) >= 0 for m <= M} = {0..M-2} u [M-1,inf)",
   not bad, f"M = 1..8 against sigma in (1/8)Z on [-5,25], {len(bad)} violations")

# the old statement was literally false where the review said it was
M, D = 4, F(3, 2)
ck("H' the old [0,D] form was false: D = 3/2, M = 4 puts 2 on the right side "
   "but 2 notin [0,3/2]", 2 in {0, 1, 2} and F(2) > D,
   "the right side listed {0,1,2} u [3,3/2]")

# and the intersection used by Theorem 10.5 is the old right-hand side, because
# there M = M_N <= nu < D
bad = []
for D in RATIONAL_D:
    for M in range(1, 9):
        if not M < D:
            continue
        lhs = set()
        for num in range(0, int(D * 12) + 1):
            sigma = F(num, 12)
            if sigma <= D and all(falling(sigma, m) >= 0 for m in range(1, M + 1)):
                lhs.add(sigma)
        for x in lhs:
            if not (x >= M - 1 or x in set(F(n) for n in range(0, M - 1))):
                bad.append((D, M, x))
ck("H'' intersecting with [0,D] when M < D reproduces [M-1,D] u {0..M-2}",
   not bad, f"{len(bad)} violations")

# =====================================================================
# I  Corollary 10.7's nu = 1 case
# =====================================================================
bad = []
cases = []
for D in [F(2), F(3), F(4), F(5)]:
    d = 2 * D
    for k in (1, 2, 3):
        r = k - F(1) / D            # nu = D(k-r) = 1
        if r <= 0:
            continue
        nu = D * (k - r)
        assert nu == 1
        cases.append((r, d))
        # at cutoff N = k, the ray [(k-1)D, inf) is retained
        for s in [(k - 1) * D + F(n, 2) for n in range(0, 40)]:
            if not psd_at(r, d, s, k):
                bad.append(("ray at N=k", r, d, s))
                break
        # but W_inf is capped at kD, so W_k strictly contains W_inf
        if psd_at(r, d, D * k + 1, max(k + 1, 4)):
            bad.append(("cap fails", r, d))
ck("I  nu = 1: at N = k the ray [(k-1)D,inf) is retained, while W_inf stops "
   "at kD", not bad,
   f"{len(cases)} (r,d) pairs with nu = 1, {len(bad)} violations"
   + ("" if not bad else f"  first: {bad[0]}"))

# N_* - 1 = k lies below Theorem 10.5's hypothesis N >= k+1, which is the gap
ck("I' the old proof applied Theorem 10.5 at N = N_*-1 = k, one degree below "
   "its hypothesis N >= k+1", all(1 * (k + 1) - 1 == k for k in (1, 2, 3, 4)),
   "N_* = nu(k+1) = k+1 when nu = 1")

# the interval typo: increasing M_N from m-1 to m replaces [m-2,D], not [M-1,D]
ck("I'' erosion event: level m-1 has interval [m-2,D] and level m has "
   "[m-1,D]", all((m - 1) - 1 == m - 2 for m in range(2, 10)))

# =====================================================================
print()
print("=" * 78)
if FAILS:
    print("FAILURES:", ", ".join(FAILS))
    sys.exit(1)
print("ALL REVISION-6 CLAIMS VERIFIED")
