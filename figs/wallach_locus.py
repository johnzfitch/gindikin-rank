import sympy as sp
from itertools import count

def partitions(n, maxpart=None):
    if maxpart is None: maxpart = n
    if n == 0: yield (); return
    for k in range(min(n, maxpart), 0, -1):
        for rest in partitions(n-k, k):
            yield (k,) + rest

def all_parts(N):
    out=[]
    for m in range(0, N+1):
        out.extend(partitions(m))
    return out

def Pnum(lam, r, alpha):
    """numerator of P_lambda(1^r): prod over cells of (r - (i-1) + alpha*(j-1))"""
    f = sp.Integer(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li+1):
            f *= (r - (i-1) + alpha*(j-1))
    return sp.expand(f)

def Poch(lam, s, alpha):
    """generalized Pochhammer (s)_lambda^{(alpha)} = prod_i (s-(i-1)/alpha)_{lambda_i}"""
    f = sp.Integer(1)
    for i, li in enumerate(lam, start=1):
        for j in range(1, li+1):
            f *= (s - (i-1)/alpha + (j-1))
    return sp.expand(f)

def locus(r, d, N, s=sp.Symbol('s')):
    """exact PSD locus: all pivot signs >= 0, pivot ~ Pnum(lam,r)*Poch(lam,s)"""
    alpha = sp.Rational(2, d)
    r = sp.nsimplify(r)
    terms=[]
    for lam in all_parts(N):
        if not lam: continue
        c = Pnum(lam, r, alpha)
        if c == 0:            # permanently null: in the carrier ideal
            continue
        terms.append((lam, sp.sign(c), sp.factor(Poch(lam, s, alpha))))
    # breakpoints
    bps=set()
    for lam,sg,P in terms:
        for root in sp.roots(sp.Poly(P, s)).keys():
            if root.is_real: bps.add(sp.nsimplify(root))
    bps = sorted(bps)
    def ok(val):
        for lam,sg,P in terms:
            v = P.subs(s, val)
            if sg*v < 0: return False
        return True
    # test points and open intervals
    pieces=[]
    lo = bps[0]-1 if bps else sp.Integer(-1)
    hi = bps[-1]+1 if bps else sp.Integer(1)
    grid = [lo] + list(bps) + [hi]
    good_pts = [b for b in bps if ok(b)]
    good_int = []
    for a,b in zip(grid, grid[1:]):
        mid = sp.Rational(a+b, 2) if (a+b).is_rational else (a+b)/2
        if ok(sp.nsimplify(mid)): good_int.append((a,b))
    return good_pts, good_int, bps

def fmt(pts, ints, tail_ok):
    """render as union of points and closed intervals"""
    ivs=[]
    for a,b in ints:
        ivs.append([a,b])
    merged=[]
    for iv in ivs:
        if merged and merged[-1][1]==iv[0]: merged[-1][1]=iv[1]
        else: merged.append(iv)
    out=[]
    used=set()
    for a,b in merged:
        out.append(f"[{a},{b}]" if b!=sp.oo else f"[{a},inf)")
        used.add(a); used.add(b)
    iso=[p for p in pts if not any(a<=p<=b for a,b in merged)]
    return "{"+",".join(str(p) for p in iso)+"} U " + " U ".join(out) if iso else " U ".join(out)

if __name__ == "__main__":
    s=sp.Symbol('s')
    print("=== integer controls (must reproduce classical Wallach sets) ===")
    for (r,d) in [(2,2),(2,4),(2,8),(3,8),(3,6)]:
        pts,ints,bps = locus(r,d,6)
        print(f"  (r,d)=({r},{d}) N=6:  isolated={pts}  intervals={[(str(a),str(b)) for a,b in ints]}")
