#!/usr/bin/env python3
"""ancillary_census.py -- the receipts Section 9.5 points at.

Three quantitative items were moved out of Section 9.5 so that the three
conceptual archetypes could be read without arithmetic in the way. Each moved
item is named in the text as living "in the ancillary data" or "in the ancillary
census", and this script is what that phrase refers to. Nothing here is a new
claim; each item is a computation the text states the conclusion of.

  1. The rank factor F_{(3,3,3,3), 3/2}(9/4) of Remark 9.1, whose exact value is
     a large positive rational.
  2. The full inertia of the Gram form at (3/2, 8), cutoff 6, throughout the open
     cell 7 < s < 8, together with the null mode at s = 7.
  3. The threshold census: pairs on either side of the defect threshold at each
     of d < 4 and d > 4, which is the evidence for the sentence that the
     governing quantity is the defect together with the arithmetic of D, and not
     the multiplicity by itself.

Exact rational arithmetic throughout.
"""
from fractions import Fraction as F
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))

from wallach_locus import all_parts, locus  # noqa: E402


def Fval(lam, D, x):
    """F_{lambda,D}(x) = prod over cells of (x - xi_ij), xi_ij = (i-1)D - (j-1)."""
    v = F(1)
    for i, li in enumerate(lam, 1):
        for k in range(1, li + 1):
            v *= (x - ((i - 1) * D - (k - 1)))
    return v


def pivot_sign(lam, D, r, s):
    return Fval(lam, D, r * D) * Fval(lam, D, s)


def ceil_frac(x):
    return -((-x) // 1)


print("=" * 78)
print("ancillary_census.py -- the receipts Section 9.5 points at")
print("=" * 78)

# ------------------------------------------------------------------ item 1
print()
print("1. Remark 9.1: the rank factor of the witness rectangle")
print("   (r, d) = (3/2, 3), so D = 3/2 and rD = 9/4; lambda = (3,3,3,3).")
D = F(3, 2)
r = F(3, 2)
lam = (3, 3, 3, 3)
val = Fval(lam, D, r * D)
print("   F_{(3,3,3,3), 3/2}(9/4) = %s" % val)
print("   positive: %s" % (val > 0))
print("   The spectral factor is negative on 5/2 < s < 3, so the pivot is")
print("   negative there:")
for s in (F(21, 8), F(11, 4), F(23, 8)):
    print("      s = %-5s  F_{lambda,D}(s) = %-22s  pivot sign = %+d"
          % (s, Fval(lam, D, s), (1 if pivot_sign(lam, D, r, s) > 0 else -1)))

# ------------------------------------------------------------------ item 2
print()
print("2. Section 9.5: the full inertia at (3/2, 8), cutoff N = 6")
r, d, N = F(3, 2), 8, 6
D = F(d, 2)
# The Gram matrix on V_N is indexed by every |lambda| <= N, the empty
# partition included; pi_empty = 1 > 0 as an empty product. Dropping it
# undercounts the positive directions by exactly one.
parts = all_parts(N)
seen = set()
for num, den in ((57, 8), (29, 4), (59, 8), (15, 2), (61, 8), (31, 4), (63, 8)):
    s = F(num, den)
    pos = sum(1 for l in parts if pivot_sign(l, D, r, s) > 0)
    neg = sum(1 for l in parts if pivot_sign(l, D, r, s) < 0)
    zer = sum(1 for l in parts if pivot_sign(l, D, r, s) == 0)
    seen.add((pos, neg, zer))
    print("   s = %-6s  inertia (pos, neg, zero) = (%d, %d, %d)" % (s, pos, neg, zer))
print("   constant across the open cell: %s" % (len(seen) == 1))
s7 = F(7)
null = [l for l in parts if pivot_sign(l, D, r, s7) == 0]
print("   at s = 7 the null modes are: %s" % (null,))
print("   unique: %s" % (len(null) == 1))

# ------------------------------------------------------------------ item 3
print()
print("3. Section 9.5: the threshold census on either side of d = 4")
print("   Erosion is read as a change in the locus between cutoff 4 and 12.")
print()
print("   %-12s %-6s %-7s %-6s %s" % ("(r, d)", "D", "nu", "side", "edge erodes"))
print("   " + "-" * 52)
rows = [(F(6, 5), 3), (F(3, 2), 3), (F(3, 2), 2),
        (F(3, 4), 8), (F(3, 2), 8), (F(1, 4), 8)]
for rr, dd in rows:
    DD = F(dd, 2)
    nu = DD * (ceil_frac(rr) - rr)
    eroded = locus(rr, dd, 4)[:2] != locus(rr, dd, 12)[:2]
    print("   %-12s %-6s %-7s %-6s %s"
          % ("(%s, %s)" % (rr, dd), DD, nu, "d<4" if dd < 4 else "d>4",
             "yes" if eroded else "no"))
print()
print("   Reading. At (6/5, 3) the defect exceeds 1 and the edge erodes even")
print("   though d < 4; at (3/4, 8) the defect equals 1 and the edge holds even")
print("   though d > 4. So the multiplicity does not govern. Neither does the")
print("   defect alone: (3/2, 3) has nu = 3/4 < 1 and still erodes, because")
print("   D = 3/2 is not an integer and the trichotomy of Theorem 9.9 needs")
print("   D in Z. The governing quantity is the defect together with the")
print("   arithmetic of D, which is what the text says.")

print()
print("=" * 78)
print("done")
print("=" * 78)
