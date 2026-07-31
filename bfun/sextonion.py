"""Split sextonions S (dim 6) inside split octonions (Zorn vector matrices),
the Jordan algebra H_3(S) (dim 21), its cubic norm, and the polarization rank."""
import sympy as sp

# ---- split octonions: Zorn vector matrices [[a, v],[w, b]], a,b scalars, v,w in k^3
def oct_mul(x, y):
    a, v, w, b = x; a2, v2, w2, b2 = y
    return (sp.expand(a*a2 + v.dot(w2)),
            sp.Matrix(3,1, lambda i,_: sp.expand((a*v2 + b2*v - w.cross(w2))[i])),
            sp.Matrix(3,1, lambda i,_: sp.expand((a2*w + b*w2 + v.cross(v2))[i])),
            sp.expand(b*b2 + w.dot(v2)))

def oct_norm(x):
    a, v, w, b = x
    return sp.expand(a*b - v.dot(w))

def oct_conj(x):
    a, v, w, b = x
    return (b, -v, -w, a)

def oct_trace(x):
    return sp.expand(x[0] + x[3])

# ---- S = H (+) N :  a, b, v1, w1 span split quaternions H; n2, m3 span the
#      2-dimensional nilpotent radical N (N.N = 0, H.N and N.H inside N).
def S_elt(c):
    """c = (a, b, v1, w1, n2, m3) -> octonion in the sextonion subalgebra"""
    a, b, v1, w1, n2, m3 = c
    return (a, sp.Matrix([v1, n2, 0]), sp.Matrix([w1, 0, m3]), b)

def check_subalgebra():
    """verify S is closed, N.N=0, and the norm has rank 4 on S (radical = N)"""
    c = sp.symbols('a b v1 w1 n2 m3');  c2 = sp.symbols('A B V1 W1 N2 M3')
    x, y = S_elt(c), S_elt(c2)
    p = oct_mul(x, y)
    closed = (p[1][2] == 0) and (p[2][1] == 0)     # v3 and w2 slots must stay 0
    # N.N = 0
    nz  = S_elt((0,0,0,0, c[4], c[5]))
    nz2 = S_elt((0,0,0,0, c2[4], c2[5]))
    pn = oct_mul(nz, nz2)
    nn0 = (sp.simplify(pn[0])==0 and sp.simplify(pn[3])==0
           and all(sp.simplify(t)==0 for t in pn[1]) and all(sp.simplify(t)==0 for t in pn[2]))
    # norm on S and its rank
    n = oct_norm(x)
    vars6 = list(c)
    Hs = sp.hessian(n, vars6)
    return closed, nn0, sp.expand(n), Hs.rank()

# ---- H_3(S): x1,x2,x3 scalars; a1,a2,a3 in S (6 params each) => 21 coordinates
def build_cubic():
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    A = []; names = []
    for k in (1, 2, 3):
        cs = sp.symbols(f'a{k}_0 a{k}_1 a{k}_2 a{k}_3 a{k}_4 a{k}_5')
        A.append(S_elt(cs)); names += list(cs)
    coords = [x1, x2, x3] + names
    a1, a2, a3 = A
    # N(x) = x1x2x3 - x1 n(a1) - x2 n(a2) - x3 n(a3) + t((a1 a2) a3)
    Nrm = (x1*x2*x3
           - x1*oct_norm(a1) - x2*oct_norm(a2) - x3*oct_norm(a3)
           + oct_trace(oct_mul(oct_mul(a1, a2), a3)))
    return sp.expand(Nrm), coords

def polarization_rank(Nrm, coords):
    """rank of x -> T(x,.,.), i.e. of the map sending x to sum_i x_i Hess(dN/du_i)"""
    n = len(coords)
    cols = []
    for i in range(n):
        Hi = sp.hessian(sp.diff(Nrm, coords[i]), coords)
        cols.append([Hi[r, c] for r in range(n) for c in range(n)])
    Amat = sp.Matrix(cols).T          # (n*n) x n
    return Amat.rank(), n

if __name__ == "__main__":
    closed, nn0, nrm, rk = check_subalgebra()
    print("S closed under octonion product :", closed)
    print("N . N = 0                       :", nn0)
    print("norm on S                       :", nrm)
    print("rank of norm form on S (dim 6)  :", rk, "(4 => radical N is 2-dimensional)")
    Nrm, coords = build_cubic()
    print("\ncubic norm on H_3(S): %d coordinates, %d monomials"
          % (len(coords), len(Nrm.as_ordered_terms())))
    r, n = polarization_rank(Nrm, coords)
    print("polarization map rank           :", r)
    print("kernel dimension                :", n - r)
    print("paper claims rank 15, kernel 6  :", (r == 15 and n - r == 6))
