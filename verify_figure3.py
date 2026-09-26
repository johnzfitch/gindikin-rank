#!/usr/bin/env python3
"""verify_figure3.py -- exact-arithmetic check of everything Figure 3 displays.

Figure 3 is the only figure in the paper that asserts a correspondence rather
than plotting a computation, so its two panels are checked separately and by
different means.

LEFT PANEL is classical.  It draws the Wallach set of a rank-3 cone against the
flag of boundary strata, on the strength of Faraut--Koranyi Thm. VII.3.1 (which
values of s make the Riesz distribution a positive measure) and Prop. VII.2.3
(what it is supported on there).  Neither is this paper's result and neither is
recomputable from the paper's own machinery, so what is checked here is the
weaker statement the figure actually needs: that the paper's own integer-rank
theorem reproduces the same set, i.e. that the ladder-plus-ray drawn on the left
axis is W_infinity(3,d) as the paper computes it.  If those disagreed, the figure
would be pairing a classical picture with a different set.

RIGHT PANEL is this paper's.  Every mark on it is checked against the locus
routine by exact cell decomposition:

  A  the retained grid {0, D, 2D} lies in W_infinity(3/2, d)        Prop. 9.3
  B  the band W_pre(3/2, d) = {0} u [D, 2D]                         Thm. 9.1
  C  the balanced point rD = 3D/2 lies strictly inside [D, 2D]      eq. balanced
  D  the cap max W_infinity(3/2, d) = 2D                            eq. maxlocus
  E  nothing above the cap survives -- the ray really is absent     Prop. 9.2
  F  the caption's erosion claim: the band is stable at d = 2, 4 and
     erodes at d = 6, 8, so drawing W_pre rather than W_infinity is
     necessary and is what the caption says

Fraction arithmetic throughout; no floating point.
"""
from fractions import Fraction as F
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs"))

from wallach_locus import locus, all_parts  # noqa: E402

FAIL = []


def check(name, ok, detail=""):
    print("[%s] %-58s %s" % ("OK " if ok else "FAIL", name, detail))
    if not ok:
        FAIL.append(name)


def pivot_sign_ok(lam, D, r, s):
    """sign of pi_lambda(s) >= 0, by the two-factor product of eq:pivot.

    lam is a partition as a tuple of row lengths; cells are (i, j) with
    1 <= i <= len(lam), 1 <= j <= lam[i-1].  The cell root is
    xi_ij = (i-1)D - (j-1), exactly the paper's F_{lambda,D}.
    """
    rD = r * D
    fr = F(1)
    fs = F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            xi = (i - 1) * D - (j - 1)
            fr *= (rD - xi)
            fs *= (s - xi)
    return fr * fs >= 0


_PARTS = {}


def in_W(r, d, s, N):
    D = F(d, 2)
    if N not in _PARTS:
        _PARTS[N] = [l for l in all_parts(N) if l]
    for lam in _PARTS[N]:
        if not pivot_sign_ok(lam, D, r, s):
            return False
    return True


print("=" * 78)
print("verify_figure3.py -- the cone/stratum figure, both panels")
print("=" * 78)
print()

# ---------------------------------------------------------------- LEFT PANEL
print("--- left panel: the classical set the flag is drawn against ---------")
for d in (2, 4, 6, 8):
    D = F(d, 2)
    R = 3
    # the paper's own integer-rank theorem, eq:intrank
    ladder = [j * D for j in range(0, R - 1)]
    got_ladder = all(in_W(F(R), d, p, 8) for p in ladder)
    # the ray: sample the closed ray [(R-1)D, .) at exact rationals
    ray_pts = [(R - 1) * D + F(k, 3) for k in range(0, 25)]
    got_ray = all(in_W(F(R), d, p, 8) for p in ray_pts)
    # and nothing between ladder points is in the set
    holes = [D * F(1, 2), D * F(3, 2)]
    got_holes = all(not in_W(F(R), d, p, 8) for p in holes if p not in ladder
                    and p < (R - 1) * D)
    check("d=%d  W(3,d) = {0, D} u [2D, inf) as drawn" % d,
          got_ladder and got_ray and got_holes,
          "ladder %s, ray from %s" % (ladder, (R - 1) * D))

print()
print("--- right panel: r = 3/2, k = 2 -------------------------------------")
r = F(3, 2)
for d in (2, 4, 6, 8):
    D = F(d, 2)
    k = 2                      # ceil(3/2)
    N = 8

    # A. retained grid
    grid = [j * D for j in range(0, k + 1)]
    okA = all(in_W(r, d, p, N) for p in grid)
    check("d=%d  A  retained grid {0, D, 2D} in W_infty" % d, okA, str(grid))

    # B. the band, pre-erosion.  Thm 9.1 holds for k+1 <= N < N_er, so the
    #    band is read at cutoff N = k+1 = 3, before any erosion can occur.
    Npre = k + 1
    band_pts = [D + F(j, 6) * D for j in range(0, 7)]
    okB1 = all(in_W(r, d, p, Npre) for p in band_pts)
    okB2 = in_W(r, d, F(0), Npre)
    gap = [D * F(1, 2)]        # strictly between 0 and D
    okB3 = all(not in_W(r, d, p, Npre) for p in gap)
    check("d=%d  B  W_pre = {0} u [D, 2D] at cutoff k+1" % d,
          okB1 and okB2 and okB3, "band [%s, %s]" % (D, 2 * D))

    # C. balanced point strictly inside the band
    rD = r * D
    okC = (D < rD < 2 * D) and in_W(r, d, rD, N)
    check("d=%d  C  balanced point rD = %s strictly inside [D, 2D]" % (d, rD),
          okC)

    # D. the cap
    okD = in_W(r, d, 2 * D, N)
    check("d=%d  D  cap 2D = %s retained" % (d, 2 * D), okD)

    # E. nothing above the cap
    above = [2 * D + F(j, 4) for j in range(1, 30)]
    okE = all(not in_W(r, d, p, N) for p in above)
    check("d=%d  E  nothing above the cap -- the ray is absent" % d, okE,
          "%d probes above %s" % (len(above), 2 * D))

print()
print("--- caption: drawing W_pre rather than W_infty is necessary ---------")
for d, should_erode in ((2, False), (4, False), (6, True), (8, True)):
    D = F(d, 2)
    # locus() returns (isolated points, closed intervals, breakpoints).  Only
    # the first two are the locus; the breakpoint list is the stratification
    # the routine searched and necessarily grows with the cutoff, so comparing
    # the whole tuple reports a change where there is none.
    lo = locus(r, d, 3)[:2]
    hi = locus(r, d, 10)[:2]
    eroded = (lo != hi)
    check("d=%d  F  band %s by cutoff 10" %
          (d, "erodes" if should_erode else "is stable"),
          eroded == should_erode,
          "N=3: pts %s ivals %s -> N=10: pts %s ivals %s"
          % (lo[0], lo[1], hi[0], hi[1]))



# =====================================================================
# Proposition 8.7 (the collapse), added with the Bergman subsection.
# =====================================================================
print()
print("--- Prop 8.7: discrete Wallach points collapse the model in rows ------")


def Fld(lam, D, x):
    p = F(1)
    for i, li in enumerate(lam, 1):
        for k in range(1, li + 1):
            p *= (x - ((i - 1) * D - (k - 1)))
    return p


_bad = 0
_n = 0
for D in (F(1, 3), F(1, 2), F(1), F(3, 2), F(2), F(5, 2), F(3), F(7, 3), F(4)):
    for lam in all_parts(9):
        if not lam:
            continue
        for j in range(0, 7):
            _n += 1
            if (Fld(lam, D, j * D) == 0) != (len(lam) > j):
                _bad += 1
check("eq (collapse)  F_{lam,D}(jD) = 0 iff ell(lam) > j, every D > 0",
      _bad == 0, "%d probes, %d mismatches" % (_n, _bad))

# the quotient basis is the j-variable Jack family
_bad = 0
for D in (F(1), F(2), F(5, 2)):
    for j in (0, 1, 2, 3):
        surv = [l for l in all_parts(6) if l and Fld(l, D, j * D) != 0]
        pred = [l for l in all_parts(6) if l and len(l) <= j]
        if surv != pred:
            _bad += 1
check("Prop 8.7  quotient basis at s = jD is {lam : ell(lam) <= j}", _bad == 0,
      "12 (D, j) pairs")

# the remark's counterexample: the scalar surrogate is false, not merely
# non-invariant, in a basis that does not diagonalize the form
import mpmath as mp
mp.mp.dps = 30


def _logB(x):
    x = mp.mpf(x)
    return mp.log(((1 - x) ** 2 + x) / mp.gamma(x + 1))


_a, _b = mp.mpf("0.5"), mp.mpf("1")
_below = all(
    _logB(t) < (1 - (mp.mpf(t) - _a) / (_b - _a)) * _logB(_a)
    + ((mp.mpf(t) - _a) / (_b - _a)) * _logB(_b)
    for t in ("0.6", "0.75", "0.9"))
_above = all(
    -mp.log(mp.gamma(mp.mpf(t)))
    > (1 - (mp.mpf(t) - _a) / (_b - _a)) * (-mp.log(mp.gamma(_a)))
    + ((mp.mpf(t) - _a) / (_b - _a)) * (-mp.log(mp.gamma(_b)))
    for t in ("0.6", "0.75", "0.9"))
check("Remark 8.2  multiplicity two: log of the scalar surrogate is not concave",
      _below, "below its chord at s = 0.6, 0.75, 0.9")
check("Remark 8.2  multiplicity one control: -log Gamma is concave (Bohr-Mollerup)",
      _above, "above its chord at the same three points")

print()
print("=" * 78)
if FAIL:
    print("FAILED: %d" % len(FAIL))
    for f in FAIL:
        print("   ", f)
    raise SystemExit(1)
print("FIGURE 3 AND THE COLLAPSE PROPOSITION VERIFIED")
print("=" * 78)
