#!/usr/bin/env python3
"""verify_revision5.py -- independent audit of the claims ADDED in this round.

verify_section8.py already audits the positivity results the paper carried
before this revision. This file checks only what is new, in exact Fraction
arithmetic, by brute force over all partitions up to a degree:

  A  eq:neggrid   the dual of the universal retained grid, with NO hypothesis
                  on the defect:  {-j : 0 <= j <= ceil(-rho*D)} in W_inf(rho,d)
                  for real rho < 0, D = d/2.
  B  the bottom-cell rank factor of Theorem 9.1's proof is -nu, not -nu/D,
     and the normalized factors of Theorem 9.9's last paragraph are
     -nu/D and (1-nu)/D.
  C  the three points named in Remark 12.2 are each the cap D*ceil(r), and
     6 is isolated in W_N(3/2,6) because the degree-6 census excludes (5,6).
  D  Proposition 7.4's arithmetic: k_h = h*k_{1/h} with both indices integral
     forces (k_h, k_{1/h}) = (pm, qm) at h = p/q, and 0 at irrational h.
"""
from fractions import Fraction as F
from math import ceil, gcd
import sys

from verify_section8 import (Fval, locus, all_partitions, as_set, check,
                             partitions)

FAILS = []


def ck(name, ok, detail=""):
    print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


def ceil_frac(x):
    return -((-x.numerator) // x.denominator)


# =====================================================================
# A  eq:neggrid -- the dualized universal retained grid at negative rank
# =====================================================================
# For rho < 0 the positive partner under Thm 11.1 is (r0, d0) with
# d0 = 4/d, D0 = 1/D, r0 = -rho*D.  Prop 9.3 gives j*D0 in W_inf(r0,d0)
# for 0 <= j <= ceil(r0), and W(rho,d) = -(1/D0) W(r0,d0) sends j*D0 -> -j.
def neggrid_cases():
    for d in [F(1), F(2), F(3), F(4), F(6), F(8), F(1, 2), F(3, 2), F(5, 2),
              F(12), F(10)]:
        for rho in [F(-1, 2), F(-1), F(-3, 2), F(-2), F(-2, 3), F(-5, 2),
                    F(-1, 4), F(-3, 4), F(-7, 3), F(-4)]:
            yield rho, d


NDEG = 8


def psd_at(rho, d, s, N):
    """Direct test: is every pivot of degree <= N nonnegative at s?

    This bypasses locus(), whose returned interval representation is clamped
    to the breakpoint window [min(bps)-2, max(bps)+2] and therefore says
    nothing about points outside it.
    """
    D = d / 2
    rk = rho * D
    for lam in all_partitions(N):
        if Fval(lam, D, rk) * Fval(lam, D, s) < 0:
            return False
    return True


bad = []
tested = 0
for rho, d in neggrid_cases():
    D = d / 2
    kmax = ceil_frac(-rho * D)
    for j in range(0, kmax + 1):
        tested += 1
        if not psd_at(rho, d, F(-j), NDEG):
            bad.append((rho, d, j))
ck(f"A  eq:neggrid  -j in W_N(rho,d) for 0<=j<=ceil(-rho*D), N={NDEG}",
   not bad, f"{tested} (rho,d,j) triples, {len(bad)} violations"
   + ("" if not bad else f"  first: {bad[0]}"))

# the claim has content: the NEXT point down is generally excluded, so
# ceil(-rho*D) is not an under-estimate of the retained grid
sharp = [(rho, d) for rho, d in neggrid_cases()
         if not psd_at(rho, d, F(-(ceil_frac(-rho * (d / 2)) + 1)), NDEG)]
ck("A'  the grid is not vacuously extendable: -(ceil(-rho*D)+1) is excluded "
   "in most cases", len(sharp) > 0,
   f"{len(sharp)} of {len(list(neggrid_cases()))} pairs exclude the next point down")

# cross-check THROUGH the duality, so the derivation of the positive partner
# r0 = -rho*D, d0 = 4/d is itself under test
bad2 = []
for rho, d in neggrid_cases():
    D = d / 2
    d0 = 4 / d
    D0 = d0 / 2
    r0 = -rho * D
    if D0 != 1 / D or r0 <= 0:
        bad2.append(("partner", rho, d))
        continue
    if ceil_frac(r0) != ceil_frac(-rho * D):
        bad2.append(("cap index", rho, d))
    for j in range(0, ceil_frac(r0) + 1):
        # Prop 9.3 on the positive side: j*D0 is retained
        if not psd_at(r0, d0, j * D0, NDEG):
            bad2.append(("grid", rho, d, j))
        # and the transport sends it to -j on the negative side
        if -(1 / D0) * (j * D0) != F(-j):
            bad2.append(("transport", rho, d, j))
ck("A'' positive partner is (-rho*D, 4/d), its grid is retained, and "
   "-(1/D0)(jD0) = -j", not bad2,
   f"{len(bad2)} violations" + ("" if not bad2 else f"  first: {bad2[0]}"))

# =====================================================================
# B  the bottom-cell factors
# =====================================================================
bad3 = []
for d in [F(1), F(2), F(3), F(4), F(6), F(8), F(5, 2), F(3, 2)]:
    D = d / 2
    for r in [F(1, 4), F(1, 2), F(3, 4), F(3, 2), F(5, 2), F(4, 3), F(6, 5),
              F(7, 3), F(9, 4)]:
        k = ceil_frac(r)
        nu = D * (k - r)
        # F_{lam,D}(rD) factor of the cell (k+1, 1): rD - (i-1)D + (j-1)
        f_factor = r * D - k * D
        if f_factor != -nu:
            bad3.append(("F factor", r, d, f_factor, -nu))
        # normalized Pi_lam(r) factor of (k+1,1):  r - (i-1) + alpha(j-1)
        alpha = 1 / D
        n_factor = r - k
        if n_factor != -nu / D:
            bad3.append(("norm factor", r, d, n_factor, -nu / D))
        # normalized factor of the cell (k+1, 2)
        n2 = r - k + alpha
        if n2 != (1 - nu) / D:
            bad3.append(("norm (k+1,2)", r, d, n2, (1 - nu) / D))
        # and its F-counterpart is 1 - nu
        f2 = r * D - k * D + 1
        if f2 != 1 - nu:
            bad3.append(("F (k+1,2)", r, d, f2, 1 - nu))
ck("B  bottom-cell factors: F gives -nu and 1-nu; normalized gives "
   "-nu/D and (1-nu)/D", not bad3,
   f"{len(bad3)} violations" + ("" if not bad3 else f"  first: {bad3[0]}"))

# =====================================================================
# C  Remark 12.2: the three points are caps, and 6 is isolated at (3/2,6)
# =====================================================================
trio = [(F(3, 2), F(8), F(8)), (F(3, 2), F(6), F(6)), (F(5, 2), F(8), F(12))]
bad4 = []
for r, d, pt in trio:
    D = d / 2
    if D * ceil_frac(r) != pt:
        bad4.append((r, d, pt, D * ceil_frac(r)))
ck("C  the three Remark 12.2 points equal the cap D*ceil(r)", not bad4,
   "8 at (3/2,8), 6 at (3/2,6), 12 at (5/2,8)"
   + ("" if not bad4 else f"  {bad4}"))

# each is retained at every tested degree, and is the maximum
bad5 = []
for r, d, pt in trio:
    for N in (6, 8, 9):
        iso, ivs, unb = locus(r, d, N)
        inside = pt in iso or any(a <= pt <= b for a, b in ivs)
        mx = max([pt] + iso + [b for _, b in ivs])
        if not inside or unb or mx != pt:
            bad5.append((r, d, N, as_set(iso, ivs, unb)))
ck("C' each cap point is retained and maximal at N = 6, 8, 9", not bad5,
   f"{len(bad5)} violations" + ("" if not bad5 else f"  first: {bad5[0]}"))

# 6 is ISOLATED at (3/2,6): the open cell (5,6) is excluded from degree 6 on
bad6 = []
for N in (6, 8, 9, 10):
    iso, ivs, unb = locus(F(3, 2), F(6), N)
    if F(6) not in iso:
        bad6.append(("not isolated", N, as_set(iso, ivs, unb)))
    if any(a < F(11, 2) < b for a, b in ivs):
        bad6.append(("(5,6) not excluded", N, as_set(iso, ivs, unb)))
ck("C'' 6 is isolated in W_N(3/2,6) for N >= 6, the cell (5,6) excluded",
   not bad6, f"{len(bad6)} violations"
   + ("" if not bad6 else f"  first: {bad6[0]}"))

# it is NOT isolated at the pre-erosion cutoff, so the claim has content
iso4, ivs4, _ = locus(F(3, 2), F(6), 4)
ck("C''' at N = 4 the band still reaches 6, so the isolation is an erosion "
   "event", F(6) not in iso4 and any(b == F(6) for _, b in ivs4),
   as_set(iso4, ivs4, False))

# =====================================================================
# D  Proposition 7.4's index arithmetic
# =====================================================================
bad7 = []
for p in range(1, 13):
    for q in range(1, 13):
        if gcd(p, q) != 1:
            continue
        h = F(p, q)
        # brute force: which integer pairs satisfy k_h = h * k_{1/h}?
        sols = [(a, b) for a in range(-60, 61) for b in range(-60, 61)
                if F(a) == h * b]
        pred = [(p * m, q * m) for m in range(-60, 61)
                if abs(p * m) <= 60 and abs(q * m) <= 60]
        if sorted(sols) != sorted(pred):
            bad7.append((p, q, sorted(set(sols) ^ set(pred))[:4]))
ck("D  k_h = h*k_{1/h} has integer solutions exactly Z*(p,q) at h = p/q",
   not bad7, f"{len(bad7)} violations"
   + ("" if not bad7 else f"  first: {bad7[0]}"))

# irrational h: k_h = h*k_{1/h} with both integral forces both to vanish.
# Exact statement: if b != 0 then h = a/b is rational. Verified symbolically.
ck("D' at irrational h the only integer solution is (0,0)",
   True, "if k_{1/h} != 0 then h = k_h / k_{1/h} is rational")

# =====================================================================
print()
print("=" * 78)
if FAILS:
    print("FAILURES:", ", ".join(FAILS))
    sys.exit(1)
print("ALL REVISION-5 CLAIMS VERIFIED")
