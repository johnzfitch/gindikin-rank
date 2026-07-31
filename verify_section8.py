#!/usr/bin/env python3
"""Independent exact-arithmetic check of the Section 8 results.

Everything is Fraction arithmetic; no floating point anywhere. Loci are computed
by exact cell decomposition of the real line: the sign of every pivot is constant
on each open interval between consecutive spectral-factor zeros, so testing one
interior rational point per cell plus every breakpoint is exhaustive.

Conventions taken from the paper:
    D = d/2
    F_{lam,D}(x) = prod_{(i,j) in lam} ( x - (i-1)D + (j-1) )
    sign pi_lam(s) = sign( F(rD) * F(s) )      [ D^|lam| h_lam > 0 ]
    W_N(r,d) = { s real : pi_lam(s) >= 0 for all |lam| <= N }
    nu = D(ceil(r) - r)
"""
from fractions import Fraction as F
from math import gcd, factorial
import itertools, sys

FAIL = []


def check(name, ok, detail=""):
    print(f"[{'OK ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


# ---------------------------------------------------------------- partitions
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


def conjugate(lam):
    if not lam:
        return ()
    return tuple(sum(1 for p in lam if p >= j) for j in range(1, lam[0] + 1))


def Fval(lam, D, x):
    v = F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            v *= (x - (i - 1) * D + (j - 1))
    return v


# ------------------------------------------------------------------- the locus
def locus(r, d, N, lo=None, hi=None):
    """Exact W_N(r,d) as (isolated_points, closed_intervals, unbounded_above)."""
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

    # merge open cells + retained endpoints into maximal closed intervals
    ivs = []
    for a, b in good_open:
        if ivs and ivs[-1][1] == a and (a in good_bp or a in (lo, hi)):
            ivs[-1] = (ivs[-1][0], b)
        else:
            ivs.append((a, b))
    covered = set()
    for a, b in ivs:
        covered.add(a)
        covered.add(b)
    iso = sorted(p for p in good_bp if not any(a <= p <= b for a, b in ivs))
    return iso, [(a, b) for a, b in ivs], unbounded


def as_set(iso, ivs, unbounded):
    parts = [f"{{{a}}}" for a in iso] + [f"[{a},{b}]" for a, b in ivs]
    if unbounded:
        parts.append("[..,inf)")
    return " U ".join(parts) if parts else "empty"


def contains(iso, ivs, s, unbounded=False, hi=None):
    if s in iso or any(a <= s <= b for a, b in ivs):
        return True
    return bool(unbounded and hi is not None and s >= hi)


print("=" * 78)
print("SECTION 8 -- INDEPENDENT EXACT VERIFICATION")
print("=" * 78)

# --------------------------------------------------- Prop 8.18  (rank zero)
ok = all(Fval(lam, F(d, 2), F(0)) == 0
         for d in (1, 2, 3, 4, 6, 8) for lam in all_partitions(6) if lam)
check("Prop 8.18  r=0: every nonempty lambda is rank-null", ok)

# --------------------------------------------------- Lemma 8.9  (rank ideal)
ok = True
for d in (2, 4, 6, 8):
    D = F(d, 2)
    for r in (F(3, 2), F(5, 2), F(7, 3), F(3), F(1, 2)):
        for lam in all_partitions(7):
            direct = Fval(lam, D, r * D) == 0
            cellwise = any(r + 1 - i + F(1, 1) / D * (j - 1) == 0
                           for i, li in enumerate(lam, start=1)
                           for j in range(1, li + 1))
            if direct != cellwise:
                ok = False
check("Lemma 8.9  rank-null iff a cell has r+1-i+alpha(j-1)=0", ok)

# ideal property: closed downward-complement (upward closed in containment)
def contained(mu, lam):
    return len(mu) <= len(lam) and all(mu[i] <= lam[i] for i in range(len(mu)))

ok = True
for d in (2, 4, 6):
    D = F(d, 2)
    r = F(5, 2)
    nulls = [l for l in all_partitions(7) if Fval(l, D, r * D) == 0]
    for mu in nulls:
        for lam in all_partitions(7):
            if contained(mu, lam) and Fval(lam, D, r * D) != 0:
                ok = False
check("Lemma 8.9  the rank-null set is an ideal for containment", ok)

# --------------------------------------------------- Lemma 8.8  (null support)
ok = True
for d in (2, 3, 4, 8):
    D = F(d, 2)
    for s in (F(0), F(1), F(3, 2), F(2), F(5, 2), F(4), F(-1)):
        for lam in all_partitions(7):
            direct = Fval(lam, D, s) == 0
            rows = []
            for i in range(1, len(lam) + 2):
                ki = (i - 1) * D - s
                if ki.denominator == 1 and ki >= 0:
                    rows.append((i, int(ki)))
            union = any(i <= len(lam) and lam[i - 1] >= ki + 1 for i, ki in rows)
            if direct != union:
                ok = False
check("Lemma 8.8  spectral-null support equals the stated row union", ok)

# --------------------------------------------------- Lemma 8.11 (upper edge)
ok = True
for d in (2, 4, 6, 8):
    D = F(d, 2)
    for r in (F(3, 2), F(5, 2), F(7, 3), F(9, 4)):
        k = -((-r) // 1)          # ceil
        k = int(k)
        nu = D * (k - r)
        eps = F(1, 10**6)
        s = k * D - eps
        for t in range(0, 4):
            i = k + 1 + t
            for j in range(1, 12):
                u = j - 1 - t * D
                rf = (u - nu) / D
                sf = u - eps
                # paper's claimed factor values
                rf_true = r + 1 - i + F(j - 1) / D
                sf_true = s - (i - 1) * D + (j - 1)
                if rf != rf_true or sf != sf_true:
                    ok = False
                disagree = (rf * sf < 0)
                if disagree != (0 < u < nu):
                    ok = False
                if (rf == 0) != (u == nu):
                    ok = False
check("Lemma 8.11 cell factors (u-nu)/D and u-eps; disagreement iff 0<u<nu", ok)

# --------------------------------------------------- Prop 8.4  (upper cap)
ok, detail = True, ""
for d in (2, 3, 4, 6, 8):
    D = F(d, 2)
    for r in (F(1, 2), F(3, 2), F(5, 2), F(7, 3), F(9, 4), F(11, 5)):
        k = int(-((-r) // 1))
        M = k + 1
        iso, ivs, unb = locus(r, d, M)
        if unb:
            ok = False
        top = max([b for a, b in ivs] + iso) if (ivs or iso) else None
        bot = min([a for a, b in ivs] + iso) if (ivs or iso) else None
        if top is not None and (top > D * k or bot < 0):
            ok, detail = False, f"(r,d)=({r},{d}) locus exceeds [0,{D*k}]"
check("Prop 8.6   W_M subset [0, D*ceil(r)] for M >= ceil(r)+1", ok, detail)

# --------------------------------------------------- Thm 8.3  (initial band)
ok, detail = True, ""
for d in (2, 3, 4, 6, 8):
    D = F(d, 2)
    for r in (F(1, 2), F(3, 2), F(5, 2), F(7, 3), F(9, 4)):
        k = int(-((-r) // 1))
        m = int(r // 1)
        Wpre_iso = [j * D for j in range(0, m)]
        Wpre_iv = (m * D, k * D)
        # N_er by direct search over the band
        Ner = None
        for N in range(1, 11):
            lams = [l for l in all_partitions(N) if len(l) and sum(l) == N]
            bad = False
            bps = sorted({(i - 1) * D - (j - 1)
                          for l in all_partitions(N)
                          for i, li in enumerate(l, 1) for j in range(1, li + 1)})
            testpts = [p for p in bps if Wpre_iv[0] <= p <= Wpre_iv[1]]
            testpts += [(a + b) / 2 for a, b in zip(testpts, testpts[1:])]
            testpts += [Wpre_iv[0], Wpre_iv[1], (Wpre_iv[0] + Wpre_iv[1]) / 2]
            for lam in lams:
                rk = Fval(lam, D, r * D)
                for s in testpts:
                    if rk * Fval(lam, D, s) < 0:
                        bad = True
                        break
                if bad:
                    break
            if bad:
                Ner = N
                break
        if Ner is not None and Ner < k + 2:
            ok, detail = False, f"(r,d)=({r},{d}) N_er={Ner} < k+2={k+2}"
        top = Ner - 1 if Ner is not None else 10
        for N in range(k + 1, min(top, 9) + 1):
            iso, ivs, unb = locus(r, d, N)
            if unb or iso != Wpre_iso or ivs != [Wpre_iv]:
                ok, detail = False, (f"(r,d)=({r},{d}) N={N}: {as_set(iso,ivs,unb)} "
                                     f"!= pre-locus")
check("Thm 8.5    N_er >= k+2 and W_N = W_pre for k+1 <= N < N_er", ok, detail)

# --------------------------------------------------- Thm 8.8  (erosion / nu<=1/b)
ok, detail = True, ""
for d in (2, 4, 6, 8, 3, 5):
    D = F(d, 2)
    b = D.denominator
    for r in (F(3, 2), F(5, 2), F(7, 3), F(9, 4), F(11, 5), F(13, 6)):
        k = int(-((-r) // 1))
        nu = D * (k - r)
        lattice_free = all(
            not any(t * D < z < t * D + nu for z in range(-2, 200))
            for t in range(0, 30))
        if lattice_free != (nu <= F(1, b)):
            ok, detail = False, f"(r,d)=({r},{d}) nu={nu} b={b}"
        if lattice_free:
            # [rD, kD] should be inside every W_N
            for N in (6, 8):
                iso, ivs, unb = locus(r, d, N)
                hiB = max([b for _, b in ivs] + iso) if (ivs or iso) else None
                for s in (r * D, k * D, (r * D + k * D) / 2):
                    if not contains(iso, ivs, s, unb, hiB):
                        ok, detail = False, f"(r,d)=({r},{d}) s={s} left band at N={N}"
check("Thm 8.12   lattice condition <=> nu <= 1/b, and band retained when it holds",
      ok, detail)

# nu = 1 : critical rectangle rank-null ; nu > 1 : negative pivot below kD
ok, detail = True, ""
for d in (2, 4, 6, 8):
    D = F(d, 2)
    for r in [k - F(nu_num, int(D)) for k in (2, 3) for nu_num in (1, 2, 3)
              if F(nu_num, int(D)) not in (0,) and F(nu_num, int(D)) < 1 or True]:
        pass
for d, r, expect in [(2, F(3, 2), "nu<1"), (4, F(3, 2), "nu=1"), (6, F(3, 2), "nu>1"),
                     (8, F(3, 2), "nu>1"), (4, F(5, 2), "nu=1"), (6, F(7, 3), "nu=1")]:
    D = F(d, 2)
    k = int(-((-r) // 1))
    nu = D * (k - r)
    rect = tuple([2] * (k + 1))
    rk = Fval(rect, D, r * D)
    s = k * D - F(1, 10**6)
    sf = Fval(rect, D, s)
    if nu == 1 and rk != 0:
        ok, detail = False, f"(r,d)=({r},{d}) nu=1 but rectangle not rank-null"
    if nu > 1 and rk * sf >= 0:
        ok, detail = False, f"(r,d)=({r},{d}) nu={nu}>1 but rectangle pivot >= 0"
    if nu < 1 and rk * sf < 0:
        ok, detail = False, f"(r,d)=({r},{d}) nu={nu}<1 but rectangle pivot < 0"
check("Thm 8.12   critical rectangle (2^{k+1}): null at nu=1, negative at nu>1",
      ok, detail)

# --------------------------------------------------- Thm 8.9  (d = 2)
ok, detail = True, ""
for r in (F(1, 2), F(3, 2), F(5, 2), F(7, 2), F(7, 3), F(9, 4), F(11, 5)):
    m = int(r // 1)
    want_iso = [F(j) for j in range(0, m)]
    want_iv = [(F(m), F(m + 1))]
    for N in (6, 9, 12):
        iso, ivs, unb = locus(r, 2, N)
        if unb or iso != want_iso or ivs != want_iv:
            ok, detail = False, f"r={r} N={N}: {as_set(iso,ivs,unb)}"
check("Thm 8.13   W_inf(r,2) = {0..m-1} U [m,m+1]", ok, detail)

# positive definiteness on the open interval: no pivot vanishes there
ok = True
for r in (F(3, 2), F(5, 2), F(7, 3)):
    m = int(r // 1)
    D = F(1)
    for lam in all_partitions(8):
        if not lam:
            continue
        rk = Fval(lam, D, r * D)
        if rk == 0:
            continue
        for s in (F(m) + F(1, 7), F(m) + F(1, 2), F(m) + F(5, 7)):
            if rk * Fval(lam, D, s) <= 0:
                ok = False
check("Thm 8.13   pairing positive definite on m < s < m+1", ok)

# --------------------------------------------------- Thm 8.10 / 8.11 (stab, cut)
ok_s, det_s, ok_n, det_n = True, "", True, ""
WITNESS = []
cases = []
for d in (4, 6, 8, 10, 12):
    D = F(d, 2)
    for k in (1, 2, 3):
        for nu in range(1, int(D)):            # nu = D(ceil r - r) forces 0 < nu < D
            r = k - F(nu, 1) / D
            if r <= 0 or r.denominator == 1:
                continue
            assert int(-((-r) // 1)) == k and D * (k - r) == nu
            cases.append((r, d, D, k, nu))
for r, d, D, k, nu in cases:
    m = int(r // 1)
    want_iso = [j * D for j in range(0, m)] + \
               [r * D + l for l in range(2, nu + 1)]
    want_iv = [(m * D, r * D + 1)]
    Nstar = nu * (k + 1)
    for N in (Nstar, Nstar + 1, Nstar + 2):
        if N > 13:
            continue
        iso, ivs, unb = locus(r, d, N)
        if unb or sorted(iso) != sorted(want_iso) or ivs != want_iv:
            ok_s, det_s = False, (f"(r,d)=({r},{d}) nu={nu} N={N}: "
                                  f"{as_set(iso,ivs,unb)}  want "
                                  f"{as_set(sorted(want_iso),want_iv,False)}")
    if Nstar - 1 >= 1 and Nstar - 1 <= 13:
        iso0, ivs0, unb0 = locus(r, d, Nstar - 1)
        strictly_bigger = (unb0 or sorted(iso0) != sorted(want_iso) or ivs0 != want_iv)
        WITNESS.append((r, d, nu, k, Nstar,
                        "unbounded tail" if unb0 else "extra retained point(s)",
                        as_set(iso0, ivs0, unb0)))
        hi0 = max([b for _, b in ivs0] + iso0) if (ivs0 or iso0) else None
        supset = all(contains(iso0, ivs0, p, unb0, hi0) for p in want_iso) and \
                 all(contains(iso0, ivs0, a, unb0, hi0) and
                     contains(iso0, ivs0, b, unb0, hi0) for a, b in want_iv)
        if not (strictly_bigger and supset):
            ok_n, det_n = False, (f"(r,d)=({r},{d}) nu={nu} N*={Nstar}: "
                                  f"W_{{N*-1}}={as_set(iso0,ivs0,unb0)} not a "
                                  f"proper superset")
check("Thm 8.15   W_inf = ladder U [floor(r)D, rD+1] U {rD+l : 2<=l<=nu}",
      ok_s, det_s)
check("Thm 8.16   N_* = nu(k+1) is exact (stable at N_*, strictly larger at N_*-1)",
      ok_n, det_n)
print()
print("  what witnesses strictness at N_*-1:")
for r, d, nu, k, Ns, kind, w in WITNESS:
    print(f"    (r,d)=({r},{d})  nu={nu} k={k} N_*={Ns}  ->  {kind:24s} W_{{N_*-1}} = {w}")
print()

# --------------------------------------------------- Thm 8.12 (transpose)
ok = True
for d in (1, 2, 3, 4, 6, 8, 5):
    D = F(d, 2)
    Dv = 1 / D
    for lam in all_partitions(8):
        for y in (F(0), F(1), F(-3, 2), F(7, 3), F(5), F(-11, 4)):
            lhs = Fval(conjugate(lam), Dv, -y / D)
            rhs = (-1 / D) ** len(
                [1 for i, li in enumerate(lam, 1) for _ in range(li)]) * Fval(lam, D, y)
            if lhs != rhs:
                ok = False
check("Thm 8.17   F_{lam',1/D}(-y/D) = (-1/D)^{|lam|} F_{lam,D}(y)", ok)

ok, detail = True, ""
for d in (2, 4, 6, 8):
    D = F(d, 2)
    dv = F(4, d)
    for r in (F(3, 2), F(5, 2), F(7, 3)):
        for N in (5, 7):
            iso, ivs, unb = locus(r, d, N)
            rv = -r * D
            iso2, ivs2, unb2 = locus(rv, dv, N)
            want_iso = sorted(-p / D for p in iso)
            want_iv = sorted([tuple(sorted((-a / D, -b / D))) for a, b in ivs])
            if sorted(iso2) != want_iso or sorted(ivs2) != want_iv:
                ok, detail = False, (f"(r,d)=({r},{d}) N={N}: dual "
                                     f"{as_set(iso2,ivs2,unb2)} vs image "
                                     f"{as_set(want_iso,want_iv,False)}")
check("Thm 8.17   W_N(-rD, 4/d) = -(1/D) W_N(r,d)", ok, detail)

ok = all((lambda rv, dv: (-rv * (F(dv, 2)), F(4, dv)) == (r, d))(-r * F(d, 2), F(4, d).numerator if F(4,d).denominator==1 else None) if False else True
         for r in (F(3, 2),) for d in (4,))
# involution, done directly:
ok = True
for d in (1, 2, 4, 8):
    for r in (F(3, 2), F(5, 2), F(7, 3)):
        D = F(d, 2)
        rv, dv = -r * D, F(4, d)
        Dv = dv / 2
        rr, dd = -rv * Dv, 4 / dv
        if rr != r or dd != d:
            ok = False
check("Thm 8.17   (r,d) -> (-rD, 4/d) is an involution", ok)

# --------------------------------------------------- Prop 8.2 (z-measure form)
# pi_lam(s) = (z)_{lam,D} (z')_{lam,D} / H'(lam,D)   with z = rD, z' = s
# and  D^{|lam|} H_lam(D) = H'(lam,D),  H,H' the Borodin-Olshanski hooks.
def conj(lam):
    return conjugate(lam)


def BO_poch(lam, z, theta):
    v = F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            v *= (z + (j - 1) - (i - 1) * theta)
    return v


def BO_H(lam, theta, primed):
    lp = conj(lam)
    v = F(1)
    add = theta if primed else F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            v *= ((li - j) + (lp[j - 1] - i) * theta + add)
    return v


def hook_paper(lam, D):
    """H_lam(D) = prod_c ( a(c)/D + l(c) + 1 ), the monic Jack hook of eq. (54)."""
    lp = conj(lam)
    v = F(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li + 1):
            a = li - j
            l = lp[j - 1] - i
            v *= (F(a) / D + l + 1)
    return v


ok_poch = ok_hook = ok_pivot = True
for d in (1, 2, 3, 4, 6, 8):
    D = F(d, 2)
    for r in (F(1, 2), F(3, 2), F(5, 2), F(2), F(7, 3)):
        for s in (F(0), F(1), F(7, 2), F(5), F(-3, 2)):
            for lam in all_partitions(7):
                n = sum(lam)
                if BO_poch(lam, r * D, D) != Fval(lam, D, r * D):
                    ok_poch = False
                if BO_poch(lam, s, D) != Fval(lam, D, s):
                    ok_poch = False
                if D ** n * hook_paper(lam, D) != BO_H(lam, D, True):
                    ok_hook = False
                pivot = Fval(lam, D, r * D) * Fval(lam, D, s) / (D ** n * hook_paper(lam, D))
                bo = BO_poch(lam, r * D, D) * BO_poch(lam, s, D) / BO_H(lam, D, True)
                if pivot != bo:
                    ok_pivot = False
check("Prop 8.2   F_{lam,D}(x) equals the BO Pochhammer (x)_{lam,D}", ok_poch)
check("Prop 8.2   D^{|lam|} H_lam(D) = H'(lam,D)", ok_hook)
check("Prop 8.2   pi_lam(s) = (rD)_{lam,D}(s)_{lam,D} / H'(lam,D)", ok_pivot)

# and the normalized form pi = (rs)_n H(lam,D) / n! * M^{(n)}_{rD,s,D}(lam)
ok = True
for d in (2, 3, 4, 8):
    D = F(d, 2)
    for r in (F(3, 2), F(5, 2), F(7, 3)):
        for s in (F(1), F(7, 2), F(5)):
            t = r * s                                   # t = zz'/theta = rs
            for lam in all_partitions(6):
                n = sum(lam)
                poch_t = F(1)
                for m in range(n):
                    poch_t *= (t + m)
                if poch_t == 0:
                    continue
                M = (F(1) * factorial(n) * BO_poch(lam, r * D, D) * BO_poch(lam, s, D)
                     / (poch_t * BO_H(lam, D, False) * BO_H(lam, D, True)))
                rhs = poch_t * BO_H(lam, D, False) / factorial(n) * M
                lhs = Fval(lam, D, r * D) * Fval(lam, D, s) / (D ** n * hook_paper(lam, D))
                if lhs != rhs:
                    ok = False
check("Prop 8.2   pi_lam(s) = (rs)_n H(lam,D)/n! * M^{(n)}_{rD,s,D}(lam)", ok)

# BO conjugation symmetry is the paper's transpose involution on this slice
ok = True
for d in (1, 2, 3, 4, 8):
    D = F(d, 2)
    for r in (F(3, 2), F(5, 2), F(2, 3)):
        for s in (F(1), F(7, 2), F(-2)):
            z, zp, th = r * D, s, D
            zd, zpd, thd = -z / th, -zp / th, F(1) / th
            # the paper's map (r,d) -> (-rD, 4/d) sends rD -> -r and s -> -s/D
            if zd != -r or zpd != -s / D or thd != F(1) / D:
                ok = False
check("Prop 8.2   BO conjugation (z,z',th,lam) -> (-z/th,-z'/th,1/th,lam') is Thm 8.17",
      ok)

# --------------------------------------------------- Prop 8.7 (retained grid)
ok, detail = True, ""
for d in (1, 2, 3, 4, 5, 6, 8, 10):
    D = F(d, 2)
    for r in (F(1, 4), F(1, 2), F(2, 3), F(3, 4), F(1), F(6, 5), F(4, 3),
              F(3, 2), F(2), F(5, 2), F(7, 3), F(3), F(9, 4), F(7, 2)):
        k = int(-((-r) // 1))
        for lam in all_partitions(10):
            rk = Fval(lam, D, r * D)
            for j in range(0, k + 1):
                if rk * Fval(lam, D, j * D) < 0:
                    ok = False
                    detail = f"(r,d)=({r},{d}) j={j} lam={lam}"
check("Prop 8.7   jD in W_inf(r,d) for every 0 <= j <= ceil(r)", ok, detail)

# and the resulting sharp cap, max W = D ceil(r) for nonintegral r
ok, detail = True, ""
for d in (1, 2, 3, 4, 6, 8):
    D = F(d, 2)
    for r in (F(1, 4), F(1, 2), F(2, 3), F(3, 4), F(6, 5), F(4, 3), F(3, 2),
              F(5, 2), F(7, 3)):
        k = int(-((-r) // 1))
        for N in (max(k + 1, 6), 10):
            iso, ivs, unb = locus(r, d, N)
            top = max([b for _, b in ivs] + iso) if (ivs or iso) else None
            if unb or top != D * k:
                ok = False
                detail = f"(r,d)=({r},{d}) N={N} -> {as_set(iso,ivs,unb)}"
check("Prop 8.7   max W_N(r,d) = D*ceil(r) at nonintegral r  (eq. maxlocus)",
      ok, detail)

# --------------------------------------------------- Prop 8.10 (rank-null ideal)
def minimal_rank_null_cell(r, D):
    """coordinatewise minimal (i0,j0) with rD = (i0-1)D - (j0-1), else None."""
    for p_ in range(0, 500):
        q = p_ * D - r * D
        if q.denominator == 1 and q >= 0:
            return (p_ + 1, int(q) + 1)
    return None


ok_exist = ok_ideal = ok_prog = True
detail = ""
for d in (1, 2, 3, 4, 5, 6, 8, 9, 10):
    D = F(d, 2)
    a, b = D.numerator, D.denominator
    for r in (F(1, 4), F(1, 3), F(1, 2), F(2, 3), F(3, 4), F(1), F(6, 5),
              F(4, 3), F(3, 2), F(2), F(5, 2), F(7, 3), F(3), F(9, 4), F(2, 5)):
        cell = minimal_rank_null_cell(r, D)
        if (cell is not None) != ((r * a).denominator == 1):
            ok_exist = False
            detail = f"(r,d)=({r},{d})"
            continue
        for lam in all_partitions(10):
            direct = Fval(lam, D, r * D) == 0
            if cell is None:
                pred = False
            else:
                i0, j0 = cell
                pred = len(lam) >= i0 and lam[i0 - 1] >= j0
            if direct != pred:
                ok_ideal = False
                detail = f"(r,d)=({r},{d}) lam={lam}"
        if cell is not None:
            i0, j0 = cell
            W = 40
            actual = {(i, j) for i in range(1, W) for j in range(1, W)
                      if (i - 1) * D - (j - 1) == r * D}
            pred = {(i0 + t * b, j0 + t * a) for t in range(0, W)}
            pred = {c for c in pred if c[0] < W and c[1] < W}
            if not pred.issubset(actual):
                ok_prog = False
                detail = f"(r,d)=({r},{d})"
            interior = {c for c in actual if c[0] < W - b and c[1] < W - a}
            if not interior.issubset(pred):
                ok_prog = False
                detail = f"(r,d)=({r},{d})"
check("Prop 8.10  a rank-null cell exists iff a*r in Z  (D = a/b lowest terms)",
      ok_exist, detail)
check("Prop 8.10  rank-null cells are exactly (i0+tb, j0+ta), t >= 0", ok_prog, detail)
check("Prop 8.10  rank-null partitions = principal ideal { lam : lam_{i0} >= j0 }",
      ok_ideal, detail)

# --------------------------------------------------- Table 1 and the inertia line
TABLE = {
    (F(3, 2), 2): {4: "{0} U [1,2]", 6: "{0} U [1,2]", 8: "{0} U [1,2]",
                   9: "{0} U [1,2]", 10: "{0} U [1,2]"},
    (F(3, 2), 4): {4: "{0} U [2,4]", 6: "{0} U [2,4]", 8: "{0} U [2,4]",
                   9: "{0} U [2,4]", 10: "{0} U [2,4]"},
    (F(3, 2), 6): {4: "{0} U [3,6]", 6: "{0} U {6} U [3,5]", 8: "{0} U {6} U [3,5]",
                   9: "{0} U {3} U {6} U [4,5]", 10: "{0} U {3} U {6} U [4,5]"},
    (F(3, 2), 8): {4: "{0} U [4,8]", 6: "{0} U {8} U [4,7]", 8: "{0} U {8} U [4,7]",
                   9: "{0} U {8} U [4,7]", 10: "{0} U {8} U [4,7]"},
    (F(5, 2), 8): {4: "{0} U {4} U [8,12]", 6: "{0} U {4} U [8,12]",
                   8: "{0} U {4} U {12} U [8,11]", 9: "{0} U {4} U {12} U [8,11]",
                   10: "{0} U {4} U {12} U [8,11]"},
}
ok, detail = True, ""
for (r, d), cols in TABLE.items():
    for N, want in cols.items():
        got = as_set(*locus(r, d, N))
        if got != want:
            ok = False
            detail = f"(r,d)=({r},{d}) N={N}: got {got}, table says {want}"
check("Table 1    every entry, including (5/2,8) at N=4 and the N=9 column",
      ok, detail)

# the erosion degrees quoted in the Table 1 caption
first = {}
for (r, d) in TABLE:
    prev, changes = None, []
    for N in range(4, 13):
        cur = as_set(*locus(r, d, N))
        if prev is not None and cur != prev:
            changes.append(N)
        prev = cur
    first[(r, d)] = changes
ok = (first[(F(3, 2), 2)] == [] and first[(F(3, 2), 4)] == []
      and first[(F(3, 2), 6)] == [6, 9] and first[(F(3, 2), 8)] == [6]
      and first[(F(5, 2), 8)] == [8])
check("Table 1    erosion degrees in the caption: none / none / 6 and 9 / 6 / 8",
      ok, str(first))

# inertia and nullity at (3/2,8), stated for cutoff N = 6
D6, r6 = F(4), F(3, 2)
lams6 = all_partitions(6)
inertia = set()
for s in (F(29, 4), F(15, 2), F(31, 4)):
    pos = sum(1 for l in lams6 if Fval(l, D6, r6 * D6) * Fval(l, D6, s) > 0)
    neg = sum(1 for l in lams6 if Fval(l, D6, r6 * D6) * Fval(l, D6, s) < 0)
    inertia.add((pos, neg))
nulls7 = [l for l in lams6 if Fval(l, D6, r6 * D6) * Fval(l, D6, F(7)) == 0]
check("Sec 8.10   at (3/2,8), cutoff N=6: inertia (29,1) throughout 7 < s < 8",
      inertia == {(30 - 1, 1)}, str(sorted(inertia)))
check("Sec 8.10   at (3/2,8), s=7, cutoff N=6: the unique null mode is (2,2,2)",
      nulls7 == [(2, 2, 2)], str(nulls7))

print()
print("=" * 78)
if FAIL:
    print(f"{len(FAIL)} FAILURES:")
    for f in FAIL:
        print("  " + f)
    sys.exit(1)
print("ALL SECTION 8 CLAIMS VERIFIED")
