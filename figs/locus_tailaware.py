import sympy as sp
s_=sp.Symbol('s')

def parts(n,maxp=None):
    if maxp is None: maxp=n
    if n==0: yield (); return
    for k in range(min(n,maxp),0,-1):
        for rest in parts(n-k,k): yield (k,)+rest
def all_parts(N):
    out=[]
    for m in range(0,N+1): out.extend(parts(m))
    return out
def conj(lam):
    if not lam: return ()
    return tuple(sum(1 for p in lam if p>=k) for k in range(1,lam[0]+1))
def Fpoly(lam,X,D):
    f=sp.Integer(1)
    for i,li in enumerate(lam,1):
        for j in range(1,li+1): f*=(X-(i-1)*D+(j-1))
    return f

def terms(r,D,N):
    """active (sign, spectral polynomial) pairs"""
    out=[]
    for lam in all_parts(N):
        if not lam: continue
        c=sp.nsimplify(Fpoly(lam,r*D,D))
        if c==0: continue
        out.append((sp.sign(c), sp.expand(Fpoly(lam,s_,D)), lam))
    return out

def locus(r,d,N):
    """exact PSD locus as (isolated_points, intervals) with sympy -oo/oo allowed"""
    D=sp.nsimplify(sp.Rational(d,2) if not isinstance(d,sp.Expr) else d/2)
    r=sp.nsimplify(r)
    T=terms(r,D,N)
    if not T: return ([], [(-sp.oo,sp.oo)], [])
    bps=sorted({sp.nsimplify(z) for sg,P,lam in T for z in sp.roots(sp.Poly(P,s_)) if z.is_real})
    def ok(v):
        for sg,P,lam in T:
            if sg*P.subs(s_,v)<0: return False
        return True
    lo=bps[0]-1; hi=bps[-1]+1
    grid=[lo]+bps+[hi]
    pts=[b for b in bps if ok(b)]
    ivs=[]
    for a,b in zip(grid,grid[1:]):
        if ok(sp.Rational(a+b,2) if (a+b).is_rational else (a+b)/2): ivs.append([a,b])
    # unbounded tails
    if ivs and ivs[0][0]==lo:
        ivs[0][0]=-sp.oo if ok(bps[0]-50) else lo
    if ivs and ivs[-1][1]==hi:
        ivs[-1][1]=sp.oo if ok(bps[-1]+50) else hi
    merged=[]
    for a,b in ivs:
        if merged and merged[-1][1]==a: merged[-1][1]=b
        else: merged.append([a,b])
    iso=[p for p in pts if not any(a<=p<=b for a,b in merged)]
    return (iso,[tuple(m) for m in merged],bps)

def fmt(r,d,N):
    iso,ivs,_=locus(r,d,N)
    out=[]
    if iso: out.append("{"+",".join(map(str,iso))+"}")
    for a,b in ivs:
        A="-inf" if a==-sp.oo else str(a); B="inf" if b==sp.oo else str(b)
        out.append(f"[{A},{B}]" if a!=b else f"{{{a}}}")
    return " U ".join(out) if out else "empty"
