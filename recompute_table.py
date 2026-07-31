#!/usr/bin/env python3
"""Exact recomputation of Table 1 and of the two new Section 8 propositions.

All arithmetic is Fraction; no floating point. Reuses the cell-decomposition
locus routine of verify_section8.py.
"""
from fractions import Fraction as F
from math import gcd
import sys

sys.setrecursionlimit(10000)


def partitions(n, maxpart=None):
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest


def all_partitions(N):
    return [l for n in range(0, N + 1) for l in partitions(n)]


def Fval(lam, D, x):
    v = F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            v *= (x - (i - 1) * D + (j - 1))
    return v


def locus(r, d, N, lo=None, hi=None):
    D = F(d, 2) if isinstance(d, int) else F(d) / 2
    r = F(r)
    lams = all_partitions(N)
    rank = {lam: Fval(lam, D, r * D) for lam in lams}

    bps = set()
    for lam in lams:
        for i, li in enumerate(lam, start=1):
            for j in range(1, li + 1):
                bps.add((i - 1) * D - (j - 1))
    bps = sorted(bps)

    def ok(s):
        for lam in lams:
            if rank[lam] * Fval(lam, D, s) < 0:
                return False
        return True

    lo = min(bps) - 2 if lo is None else lo
    hi = max(bps) + 2 if hi is None else hi
    pts = [lo] + [b for b in bps if lo < b < hi] + [hi]

    good_bp = [b for b in bps if lo < b < hi and ok(b)]
    good_open = []
    for a, b in zip(pts, pts[1:]):
        if ok((a + b) / 2):
            good_open.append((a, b))

    unbounded = ok(hi + F(1, 3)) and ok(hi + 11) and ok(hi + 101)

    ivs = []
    for a, b in good_open:
        if ivs and ivs[-1][1] == a and (a in good_bp or a in (lo, hi)):
            ivs[-1] = (ivs[-1][0], b)
        else:
            ivs.append((a, b))
    iso = sorted(p for p in good_bp if not any(a <= p <= b for a, b in ivs))
    return iso, [(a, b) for a, b in ivs], unbounded


def fmt(x):
    return str(x) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def as_set(t):
    iso, ivs, unb = t
    parts = [f"{{{fmt(a)}}}" for a in iso] + [f"[{fmt(a)},{fmt(b)}]" for a, b in ivs]
    if unb:
        parts.append("[..,inf)")
    return " U ".join(parts) if parts else "empty"


ROWS = [(F(3, 2), 2), (F(3, 2), 4), (F(3, 2), 6), (F(3, 2), 8), (F(5, 2), 8)]
COLS = [4, 6, 8, 9, 10]

print("=" * 78)
print("TABLE 1 -- exact loci")
print("=" * 78)
table = {}
for r, d in ROWS:
    for N in COLS:
        table[(r, d, N)] = locus(r, d, N)
    print(f"(r,d)=({fmt(r)},{d})")
    for N in COLS:
        print(f"    N={N:2d}  {as_set(table[(r,d,N)])}")

print()
print("Which columns actually differ from the previous listed column?")
for r, d in ROWS:
    prev = None
    marks = []
    for N in COLS:
        cur = as_set(table[(r, d, N)])
        marks.append(f"N={N}:{'CHANGE' if cur != prev else 'same  '}")
        prev = cur
    print(f"  ({fmt(r)},{d}): " + "  ".join(marks))

# where exactly does (3/2,6) make its second erosion?
print()
print("(3/2,6) by degree:")
prev = None
for N in range(4, 13):
    cur = as_set(locus(F(3, 2), 6, N))
    print(f"    N={N:2d}  {cur}" + ("   <-- changed" if cur != prev else ""))
    prev = cur

print()
print("(5/2,8) by degree:")
prev = None
for N in range(4, 11):
    cur = as_set(locus(F(5, 2), 8, N))
    print(f"    N={N:2d}  {cur}" + ("   <-- changed" if cur != prev else ""))
    prev = cur

print()
print("=" * 78)
print("NEW PROP: universal retained grid   jD in W_infty(r,d) for 0<=j<=ceil(r)")
print("=" * 78)
bad = []
for d in (1, 2, 3, 4, 5, 6, 8, 10):
    D = F(d, 2)
    for r in (F(1, 4), F(1, 2), F(2, 3), F(3, 4), F(1), F(6, 5), F(4, 3), F(3, 2),
              F(2), F(5, 2), F(7, 3), F(3), F(9, 4), F(7, 2)):
        k = int(-((-r) // 1))
        for N in (6, 10, 12):
            lams = all_partitions(N)
            for j in range(0, k + 1):
                s = j * D
                for lam in lams:
                    if Fval(lam, D, r * D) * Fval(lam, D, s) < 0:
                        bad.append((d, r, j, N, lam))
print(f"  counterexamples over all tested (d,r,j,N,lambda): {len(bad)}")
if bad:
    print("  ", bad[:5])

print()
print("  max W_N(r,d) == D*ceil(r) for nonintegral r  (finite-cutoff check, N>=ceil(r)+1):")
bad2 = []
for d in (1, 2, 3, 4, 6, 8):
    D = F(d, 2)
    for r in (F(1, 4), F(1, 2), F(2, 3), F(3, 4), F(6, 5), F(4, 3), F(3, 2), F(5, 2), F(7, 3)):
        k = int(-((-r) // 1))
        for N in (max(k + 1, 6), 10):
            iso, ivs, unb = locus(r, d, N)
            hi = max([b for _, b in ivs] + iso) if (ivs or iso) else None
            if unb or hi != D * k:
                bad2.append((d, fmt(r), N, as_set((iso, ivs, unb))))
print(f"  violations: {len(bad2)}")
for b in bad2[:8]:
    print("   ", b)

print()
print("=" * 78)
print("NEW PROP: complete rank-null ideal")
print("=" * 78)


def minimal_cell(r, D):
    """Coordinatewise minimal (i0,j0) with rD = (i0-1)D-(j0-1), or None."""
    for p in range(0, 400):
        q = p * D - r * D
        if q.denominator == 1 and q >= 0:
            return (p + 1, int(q) + 1)
    return None


bad3 = []
for d in (1, 2, 3, 4, 5, 6, 8, 9, 10):
    D = F(d, 2)
    a, b = D.numerator, D.denominator
    for r in (F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(1), F(6, 5), F(4, 3),
              F(3, 2), F(2), F(5, 2), F(7, 3), F(3), F(9, 4), F(2, 5)):
        cell = minimal_cell(r, D)
        exists_pred = (r * a).denominator == 1
        if (cell is not None) != exists_pred:
            bad3.append(("existence", d, fmt(r), cell, exists_pred))
            continue
        lams = all_partitions(10)
        for lam in lams:
            direct = Fval(lam, D, r * D) == 0
            if cell is None:
                pred = False
            else:
                i0, j0 = cell
                pred = len(lam) >= i0 and lam[i0 - 1] >= j0
            if direct != pred:
                bad3.append(("ideal", d, fmt(r), cell, lam, direct, pred))
        # progression check
        if cell is not None:
            i0, j0 = cell
            sols = set()
            for i in range(1, 60):
                for j in range(1, 60):
                    if (i - 1) * D - (j - 1) == r * D:
                        sols.add((i, j))
            pred_sols = {(i0 + t * b, j0 + t * a) for t in range(0, 60)}
            pred_sols = {c for c in pred_sols if c[0] < 60 and c[1] < 60}
            actual = {c for c in sols if c[0] < 60 and c[1] < 60}
            # restrict predicted to the same window
            if not pred_sols.issubset(actual) or not {c for c in actual if c[0] < 60 - b and c[1] < 60 - a}.issubset(pred_sols):
                bad3.append(("progression", d, fmt(r), cell, sorted(actual)[:6], sorted(pred_sols)[:6]))
print(f"  violations: {len(bad3)}")
for x in bad3[:8]:
    print("   ", x)

print()
print("  worked examples:")
for r, d in [(F(3, 2), 8), (F(5, 2), 8), (F(3, 2), 2), (F(3, 2), 6), (F(3, 2), 10),
             (F(3, 2), 3), (F(4, 3), 3), (F(2, 3), 3)]:
    D = F(d, 2)
    a, b = D.numerator, D.denominator
    cell = minimal_cell(r, D)
    print(f"    (r,d)=({fmt(r)},{d})  D={fmt(D)}  a={a} b={b}  a*r={fmt(r*a)}  "
          f"minimal cell={cell}  k=ceil(r)={int(-((-r)//1))}  nu={fmt(D*(int(-((-r)//1))-r))}")

print()
print("=" * 78)
print("INERTIA at (3/2,8), N=6, on 7<s<8")
print("=" * 78)
D, r = F(4), F(3, 2)
lams = all_partitions(6)
for s in (F(15, 2), F(29, 4), F(31, 4)):
    pos = neg = zer = 0
    for lam in lams:
        v = Fval(lam, D, r * D) * Fval(lam, D, s)
        if v > 0:
            pos += 1
        elif v < 0:
            neg += 1
        else:
            zer += 1
    print(f"    s={fmt(s)}:  #partitions={len(lams)}  pos={pos} neg={neg} zero={zer}")
nulls = [l for l in lams if Fval(l, D, r * D) * Fval(l, D, F(7)) == 0]
print(f"    s=7 null modes at N=6: {nulls}")
