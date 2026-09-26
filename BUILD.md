# Building `gindikin-rank.tex`

Requires LuaLaTeX (TeX Live 2023+) and the Etch & Sketch kit, **v5 or later**.

```bash
export TEXINPUTS=".:/path/to/etch-and-sketch:/path/to/etch-and-sketch/vendor/texmf/tex/lualatex/lualatex-math:"
export OSFONTDIR="/path/to/etch-and-sketch/fonts//"
lualatex gindikin-rank.tex
lualatex gindikin-rank.tex   # second pass for cross-references
```

Figures are pre-built vector PDFs in `figs/`. To regenerate:
`OSFONTDIR=".../fonts//" python3 figs/make_figures.py` (matplotlib, PGF backend, LuaLaTeX).
`figs/wallach_locus.py` independently recomputes every locus in Section 8.

## Environment notes

1. **`luaotfload` + `lualibs` must be present**, or no OpenType font loads.
   On Debian/Ubuntu: `apt-get install texlive-luatex`, then build the font DB once with
   `texlua $(kpsewhich luaotfload-tool.lua) --update`.
2. **Put only the `lualatex-math` leaf on `TEXINPUTS`**, not the whole vendor tree, or the
   vendored `luaotfload` shadows the system copy.
3. **Install the bundled fonts** so the math-font autodetect finds Libertinus Math:
   `cp etch-and-sketch/fonts/libertinus/*.otf etch-and-sketch/fonts/kalam/*.ttf ~/.fonts/ && fc-cache -f`.
   Body text is TeX Gyre Schola; math is Libertinus Math (Scale=MatchUppercase). Both are the
   kit's intended pairing.

## Kit-version note

This document targets Etch & Sketch v5. Building against v4 or earlier reintroduces a rendering
fault: under v4 the two `\underbrace`s in the proof of the cocycle (Section 4) typeset as the
literal characters `z { | }` with solid black bars, because `mathtools` overwrites
`unicode-math`'s `\underbrace`/`\overbrace` with a plain-TeX construction that reads brace
pieces from family-3 slots holding different glyphs under an OpenType math font. Kit v1.12
restores the correct meanings. Two further workarounds needed under v3 are also no longer
required and have been removed from the preamble:
- v4's `etch-schematic` self-loads `decorations.pathreplacing` (brace decorations); v3 did not,
  and braces failed silently.
- v4 makes inline `\tfrac` content-aware, so a `\tfrac` inside a display no longer collapses to
  a script-size slashed fraction.

One preamble line is still needed: the kit gives `definition` its own per-section counter, so
`\Definition 8.1` and `\Lemma 8.1` would collide in a section with both. The preamble aliases
the definition counter onto the shared theorem/lemma counter.

## Revision note (this build)

Built and verified with Etch & Sketch v6 under TeX Live 2023 (`lualatex`), two passes:
0 errors, 0 undefined or multiply-defined references, 0 overfull boxes, 0 underfull
boxes, 45 pages. `tools/pagecheck.py` reports 2 stranded headings (p12, p32); the
pre-revision source reported 3. On a stock Debian/Ubuntu TeX Live the only extra
package needed was `texlive-luatex` (for `lualibs`/`luaotfload`); the vendored
`lualatex-math` leaf on `TEXINPUTS` and `OSFONTDIR` pointing at `fonts/` were
otherwise sufficient.

Two preamble additions this round, both document-local:

- `\captionsetup{font={normalsize,it}}`. The kit sets captions at `\small`, which at an
  11pt body reads as fine print under a full-width figure. The italic body plus
  upright-bold label still separates a caption from body text. Measured cost: zero pages.
- `\tcbset{... title after break={\kvtcb@title\ (continued)}}` on both boxed-theorem
  styles, so a theorem box split across a page names itself again on the continuation.
  `\tcbtitletext` does **not** work here -- tcolorbox `\let`s it to `\@empty` when the
  title is attached, so the continuation bar would print a bare "(continued)". The title
  survives in `\kvtcb@title`, hence the `\makeatletter` wrapper.

### What this round changed

The review asked for one precise patch pass. Sections 4 and 5 lost their branch language
(every functional equation is now stated as a global meromorphic identity) and Section 5
no longer claims the symbol becomes rational at integer rank -- only its spectral
unit-shift quotient does. Section 8 gained three results and one subsection:

- **Prop. 8.2** (new subsection 8.2, *Relation with Jack z-measures*) identifies the
  pivots with the Borodin--Olshanski z-measure weights on the slice
  `(z, z', theta) = (rD, s, D)`, and the surrounding prose attributes chamber positivity
  to their complementary series and the transpose duality to their conjugation symmetry.
  What remains new -- fixed-rank closed semidefinite loci, finite-degree erosion, the
  integral-defect classification, the exact stabilization degree -- is isolated there.
- **Prop. 8.7** (*The universal retained grid*) proves `jD` in `W_inf(r,d)` for every
  `0 <= j <= ceil(r)`, which with Prop. 8.6 gives `max W_inf = D ceil(r)` unconditionally.
  This replaces a sentence that had conjectured the equality from a finite sweep.
- **Prop. 8.10** (*The complete rank-null ideal*) replaces the first-subdiagonal-only
  discussion: a rank-null cell exists iff `rD` is in `Lambda_D` (equivalently `ar` in Z
  for `D = a/b` in lowest terms), the cells form one arithmetic progression, and the
  rank-null partitions are the principal ideal generated by a single rectangle.

Table 1 was rebuilt: the `(5/2,8)` entry at `N=4` was a dash and is in fact
`{0,4} u [8,12]`; the `N=9` column is now present, since that is where the second
erosion of `(3/2,6)` first appears; and every "unchanged" is replaced by the repeated
locus, so no cell depends on the one to its left. The body is set `\footnotesize` --
the six-column form overflows by 10.07pt at `\small`. The paragraph beneath the table
narrating the epistemic status of the sweep was deleted; the standing supplementary-
material sentence covers it.

Three pre-existing box faults, not raised by the review, were also cleared: a 47.18pt
overfull in the cocycle proof and a 7.42pt overfull in the Faulhaber step (both fixed by
displaying a long inline formula) and an underfull in the `blem:dummy` statement.

### Verification

`verify_review3.py` checks that this round landed. Each of 24 defect strings is asserted
absent from the revised source **and present in the pre-revision source**, so no check
can pass vacuously through a typo; 43 required repairs are asserted present. Set `NEW`
and `OLD` at the top of the file to the post- and pre-revision `.tex` paths. All 67 pass.

`verify_edits.py` is the previous round's equivalent and is kept for the record; its
paths refer to that session's layout.

`verify_section8.py` is an independent exact-rational audit of the Section 8 results.
It recomputes positivity loci by exact cell decomposition of the real line -- Fraction
arithmetic throughout, no floating point -- and checks each stated closed form, the
lattice criterion, the stabilization cutoff, and the transpose duality against brute
force over all partitions up to the relevant degree. This round it was renumbered to the
post-revision labels and extended with checks for the three new results: the
Borodin--Olshanski normalization in both forms, the retained grid and the resulting sharp
cap, the rank-null existence criterion, cell progression and principal ideal, every
Table 1 entry (including the corrected `(5/2,8)` at `N=4` and the new `N=9` column), the
erosion degrees quoted in the Table 1 caption, and the inertia `(29,1)` and unique null
mode `(2,2,2)` at `(3/2,8)`, cutoff `N=6`. All checks pass.

`recompute_table.py` is the scratch recomputation used to settle the table entries and
the two new propositions before they were written; it is redundant with
`verify_section8.py` and is included only as a shorter standalone reproduction.

## Prose and typography pass

A clause-by-clause read of the whole paper, plus a pass on the white space.

**Prose.** Roughly fifty sentences were reworded where a clause was doing no
work, a word was repeated inside its own sentence, or a construction had drifted
out of the journal register. The substantive ones:

- The Introduction still said "Section 4 derives four" for a section that derives
  five identities, and still said the shift quotient's pole and zero
  progressions "never finish cancelling" when in fact they never meet.
- Section 6.1 used `r` for the rank of a simple Euclidean Jordan algebra, against
  the convention fixed in Section 1.1 (`N` for an integer rank, `r` for a complex
  one). Equation (26), the degree, the root list, and the Albert pair now all
  use `N`. Section 8's opening paragraph had the same clash and now uses `R`, the
  symbol Theorem 8.4 already uses.
- Equation (6) ended in a comma and was followed by a new sentence.
- The justification of (54) and the content of (54) were each stated twice in
  consecutive paragraphs; the duplicate is gone.
- The list of Peirce multiplicities of simple Euclidean Jordan algebras appeared
  verbatim in both Section 7.3 and Remark 8.5. Section 7.3's copy is gone; it was
  a digression there, and Remark 8.5 is where the scope claim belongs.
- "we state its scope carefully", "the positivity census", "is retained because",
  "no causal or independently measured link" and "any finite-window slope fitted
  to" were drafting or lab-report register, not journal register.

**White space.** The complaint was short lines stranded before display equations.
`whitespace_audit.py` and `ws.py` locate them: they measure every text line's
right edge against the modal right edge of the text block and report the ones
that fall short by more than a threshold, separating lines that precede a display
from paragraph-final lines. Before the pass there were 18 body-prose lead-ins
leaving a hole wider than 380pt on a 468pt measure, and 25 paragraph-final lines
of one or two words. After it there are 4 and 15, and of the 4, three are
extraction artifacts (a tall inline formula is reported as its own line, so the
text above it is scored as a stranded lead-in). The two spots that were
photographed -- the abstract's "Fix h > 0. We define" and Section 2.1's
"Definition 2.2. Write" -- are both gone.

Note that this is whack-a-mole by nature: lengthening a lead-in moves every
break after it, so three of the fixes had to be redone after the first attempt
made a neighbouring line worse. Re-run `ws.py <threshold>` after any further
edit. `microtype` is already loaded by `etch-math` with protrusion and LuaTeX
font expansion, so the global lever is on; what remains is per-sentence.

The build is unchanged in size at 45 pages, with 0 overfull and 0 underfull
boxes, and `pagecheck` still reports 2 stranded headings.

## Chart-review pass (Section 8.10 rewrite and scope narrowing)

Built with Etch & Sketch under TeX Live 2023 (`lualatex`), two passes: 0 errors,
0 undefined or multiply-defined references, 0 overfull boxes, 0 underfull boxes,
47 pages. `pagecheck` reports one residual `thin-box-segment` on p39.

### The mathematics was verified before it was written

`verify_review_810.py` checks the reviewer's proposed replacement for Sections
8.10--8.11 against brute force, in exact `Fraction` arithmetic, before any of it
was committed to the source:

- **A** the terminal falling-factorial reduction
  `pi_lambda(kD - sigma) = C_lambda(sigma) * fall(nu,m) * fall(sigma,m)`, with
  `C_lambda > 0` on `0 <= sigma < D` and `>= 0` at `sigma = D`, and the interior
  sign law -- 12 integral-defect `(d,r)` cases, all partitions to degree
  `4(k+1)`, sigma on a sixth-integer grid;
- **B** the one-variable intersection
  `{sigma in [0,D] : fall(sigma,m) >= 0 for m <= M} = [M-1,D] u {0,...,M-2}`;
- **C** the boxed finite-cutoff staircase against the independent cell-decomposition
  locus routine, 78 `(d,r,N)` combinations;
- **D** the all-degree corollary and the exactness of `N_* = nu(k+1)`;
- **E** the defect-form corollary: `ar = ak - b*nu`, existence iff `b*nu` in Z,
  and the minimal-cell formula via the least `t_0` with `m + a t_0 = 0 mod b`.

All five pass with zero violations. That is why the two-page row-parity census
could be deleted rather than merely rearranged.

### What changed

**Required fixes.** Lemma 8.11's epsilon-condition did not imply `D - epsilon > 0`,
which the proof needs for the cell `(k,1)`; it is now "for all sufficiently small
epsilon > 0" with the two conditions named in the proof. The abstract, the
statement of results, and Theorem 7.2's title no longer claim *every*
multiplicative ambiguity -- only cocycle-compatible deformations with an entire
logarithm. Proposition 7.3 now says in its own statement that `2 pi p` is the type
of the two fundamental harmonics, not of the ambiguity space. `H_3(S)` and
`J_3(S)` are unified to `J_3(S)`, defined once at first use. Boas, Macdonald,
Stanley and a local Faraut--Koranyi citation are now cited in the body. The
nonintegral-defect stabilization language states its tested range, verified
stable across `10 <= N <= 14`, `12 <= N <= 14`, `12 <= N <= 14`. Remark 8.4 no
longer says an ideal erodes anything.

**Sections 8.10--8.11 replaced.** Now: the terminal falling-factorial reduction
(Lemma), the one-variable intersection (Lemma), the exact finite-cutoff erosion
staircase (boxed Theorem), and two corollaries recovering the all-degree locus
`eq:stab` and the stabilization degree `eq:ncut`. The staircase also dates every
erosion event: level `m` first appears at `m(k+1)`, each event lowers the
continuous endpoint one unit and leaves an isolated point behind. `thm:stab` and
`thm:ncut` keep their labels but are now corollaries, so `\Cref` renders them as
Corollary; this was confirmed as acceptable.

**Structure.** Section titles advance the argument rather than filing it.
Section 7.6 is gone, folded into 7.5 as one synthesis paragraph, which also
removes the unexplained centred rule. Section 8 went from fourteen subsections to
eight. Section 6 states its scope once, and Proposition 6.1's proof no longer
replays Theorem 5.1. A bridge paragraph now connects the two halves through the
shared affine-root-product mechanism, and the paper ends on the three-notions
conclusion instead of trailing off in scope remarks.

**Figures.** `figs/make_figures.py` gained `figure_four`, the integral-defect
erosion staircase in the terminal coordinate `sigma = kD - s`, drawn for `D = 4`,
`r = 1/4` so that `k = 1`, `nu = 3`, levels arrive at `N = 2, 4, 6` and the
bottom row reads `s in [0,2] u {3,4}` -- literally equation `eq:half8`. Note that
the file already contained a `figure_four` parameterised for `k+1 = 4`, which
contradicts the paper's own `N_* = 6` at `(1/4, 8)`; it was corrected, not
duplicated. Figure 3 now labels each row with the locus it shows
(`W_10` vs `W_infinity`) and marks the finite-cutoff row with a dashed rule, so
the distinction is on the axis rather than in the fifth sentence of the caption.
Figure 1's caption now says the factor picture is the integer-rank model whose
identity continues meromorphically.

### Not done

The Mellin/Watson half-sector derivation is still in the main text rather than an
appendix, and the optional cutoff-evolution, rank-null-lattice, cell-chamber and
rank-asymptotic figures were not drawn.


## Revision 5 (this build)

Two review passes applied: `gindikin9` (a precision pass on stale or overbroad
statements) and `gindikin-9polish` (a structural pass on the section hierarchy,
titles and theorem-box headers). Built with Etch & Sketch under TeX Live 2023
(`lualatex`), three passes: **50 pages, 0 errors, 0 overfull boxes, 0 underfull
boxes, 0 undefined or multiply-defined references.** `pdffonts` reports no Type 3
fonts. `tools/pagecheck.py` reports one residual `thin-box-segment` on p26.

On a stock Debian/Ubuntu TeX Live the only extra package needed is
`texlive-luatex`; the font database must then be built once with
`texlua $(kpsewhich luaotfload-tool.lua) --update` with `OSFONTDIR` pointing at
the kit's `fonts/`, or every OpenType load fails at
`! Font \TU/lmr/m/n/10.95 ... not loadable`.

### Structure

The paper went from eight sections to twelve. The positivity half was a single
twenty-page Section 8 with eight subsections; it is now Sections 8-12, because it
is four distinct chapters and one conclusion, not four subsections. Every section
title now advances the argument, and read consecutively they state it. The two
solitary subsections (the old 3.1 and 5.1) were deleted -- hierarchy without
structure -- and the numbered `Organization` subsection became one unnumbered
paragraph at the end of the introduction.

Two blocks moved for narrative rather than cosmetic reasons. The old subsection
`Fractional Rank: Defect, Balance, and the Initial Band` was split: the balanced
point closes the chamber-positivity story in 8.3, the defect opens the erosion
story in 9.1. And Figure 3 with Table 1 moved into the new 9.5, because Figure 3
previously appeared *before* the trichotomy its own caption invokes.

Sixteen theorem and proposition box titles were changed from inventory labels to
mathematical statements (`Rank addition and reflection` ->
`Interval splitting gives the rank cocycle`, and so on). Seven that already
stated facts were left alone.

### Mathematics changed

- **New Lemma 7.2** (`lem:mult2add`) closes the advertised classification: an
  arbitrary entire multiplicative cocycle is nowhere zero, hence has an entire
  logarithm on the simply connected `C^2`, and the normalization `D(0,s)=0` is
  licensed because `D_0(0,s)` is a continuous `2*pi*i*Z`-valued function of `s`
  and therefore a single constant. Theorem 7.3 is retitled accordingly.
- **New Proposition 7.4** (`prop:charcouple`) proves that reciprocal-step
  covariance forces `k_h = h k_{1/h}`, so at `h = p/q` the admissible character
  index pairs are the rank-one lattice `Z*(p,q)`, and at irrational step both
  vanish. Remark 4.1's conclusion that reciprocity is "not an additional
  constraint" was false at the function level and is corrected.
- **New equation `eq:neggrid`**: the universal retained grid dualizes with *no*
  hypothesis on the defect, `{-j : 0 <= j <= ceil(-rho D)}` in
  `W_inf(rho,d)` for `rho < 0`. The old claim that a negative-rank cell "is
  settled exactly when its dual is a positive cell of integer defect" was false:
  Theorem 11.1 transports every positive-rank result, and what needs integral
  defect is only the closed form.
- The bottom-cell rank factor in Theorem 9.1's proof is `-nu`, not `-nu/D`;
  Theorem 9.9's last paragraph now says *normalized* rank factors.
- Remark 12.2 no longer withholds an all-degree assertion at `(3/2,6)`: all three
  displayed points are the cap `D ceil(r)`, retained by Proposition 9.3.
- The bounded-band narrative is qualified everywhere: the all-degree locus is
  bounded, and at rational steps contains a closed cell chamber, but the initial
  finite-cutoff band may erode *or fragment* -- at irrational `D` there is no
  nondegenerate chamber at all.

Front matter gained an affiliation, a contact address, keywords, the 2020 MSC,
and a pointer to the verification code. Two bibliography initials were wrong
(E. Friedman, not S.; L. Tizzano, not F.).

### Verification

`verify_section8.py` is unchanged and still passes end to end -- the
restructuring moved no mathematics, and that is the check which proves it.

`verify_revision5.py` is new and audits only what this round added, in exact
`Fraction` arithmetic:

- **A** `eq:neggrid`, over 538 `(rho,d,j)` triples at cutoff 8, plus the
  cross-check that the positive partner really is `(-rho D, 4/d)` and that
  `-(1/D_0)(j D_0) = -j`. Note that the test evaluates pivots **directly**
  rather than through `locus()`: `locus()` clamps its interval representation to
  the breakpoint window `[min(bps)-2, max(bps)+2]`, so a point below that window
  is reported absent when it was simply never examined. The first version of this
  test failed for exactly that reason and the paper's claim was fine.
- **B** the bottom-cell factors, `F` giving `-nu` and `1-nu` against normalized
  `-nu/D` and `(1-nu)/D`.
- **C** the three Remark 12.2 points equal `D ceil(r)`, are retained and maximal
  at `N = 6, 8, 9`, and `6` is isolated at `(3/2,6)` from `N = 6` on but *not* at
  `N = 4`, so the isolation is a genuine erosion event.
- **D** the character-index lattice, brute-forced over all coprime `(p,q)` with
  `p,q <= 12` and all index pairs in `[-60,60]^2`.

All pass.

### Figures

`figs/make_figures.py` was rewritten against the kit's matplotlib companion,
which is now vendored beside it (`es_figure.py`, `etch-and-sketch.mplstyle`) so
the paper's tree is self-contained. The previous script hand-rolled its own
preamble and set figure prose in **Libertinus Serif**, which is not the body
face -- the body is TeX Gyre Schola -- so every page carrying a figure had a real
typographic mismatch. It also left matplotlib's default `pdf.fonttype: 3`, which
arXiv flags. Both are fixed by `es_style(backend="pgf")`, which routes labels
through the same LuaLaTeX run and font chain the document uses.

Two deliberate departures from the kit defaults, documented in the script:
`bbox_inches=None`, because the document includes these at natural size and the
width must equal the 452.97pt measure (a tight bbox would crop below it); and
`axes.grid` off, because the kit's y-grid is for quantitative y-axes and here `y`
indexes cases.

Each figure also now makes its point geometrically instead of by annotation:

- **Fig 2** puts zeros on an upper tier and poles on a lower one, so lattice
  coincidence *is* vertical alignment at `r = 3` and a visible stagger at
  `r = 3/2`.
- **Fig 3** loses six floating labels crammed at `x ~ 9.6` and a fake axis gap
  (ticks jumped 8 -> 10 with no break marker); it gains real ticks 0-10, honest
  arrowheads, an amber mark for the isolated cap `D ceil(r)` and a forest rule
  for the balanced point `rD`, so it carries Remark 12.2's claim.
- **Fig 4** shades the open interval each level lost, making erosion visible as
  area rather than only an arrow; the fragile `rotation=32` label and a
  duplicated trailing comment block are gone.
- **Fig 1** shades the two sub-intervals and colour-matches each brace to its
  factor.

Captions were rewritten to state what to see. Figures come out 451.2pt against a
452.97pt measure. All four were checked both standalone and in place on pages 8,
12, 40 and 44.

### Files for release

Minimum to build: `gindikin-rank.tex`, `figs/*.pdf`, `BUILD.md`.
To regenerate figures, add `figs/make_figures.py`, `figs/es_figure.py`,
`figs/etch-and-sketch.mplstyle`.
To check the mathematics, add `verify_section8.py`, `verify_revision5.py`,
`figs/wallach_locus.py`, `figs/locus_tailaware.py`, `recompute_table.py`, `bfun/`.
Do **not** ship `verify_edits.py`, `verify_review3.py`, `verify_review_810.py`,
`whitespace_audit.py` or `ws.py`: session bookkeeping with stale paths, and
`verify_review3.py`'s OLD/NEW anchors no longer resolve after the restructuring.

### Not done

The Mellin/Watson half-sector derivation is still in the main text rather than an
appendix. Figure 1 is still a matplotlib figure although an interval split with
braces is arguably an `etch-schematic` schematic; converting it risks the
`\underbrace` brace-decoration fault recorded above, and one register across all
four figures is worth more than one perfectly classified figure.


## Revision 6 (this build)

Two further review passes applied (`gindikinz`, `gindikinz2`), which overlap
heavily on three local corrections and diverge in one important place: the first
review identifies a theorem the paper already proved without noticing. Built with
Etch & Sketch under TeX Live 2023 (`lualatex`), three passes: **54 pages, 0
errors, 0 overfull boxes, 0 underfull boxes, 0 undefined or multiply-defined
references.** No Type 3 fonts. `pagecheck` still reports the single
`thin-box-segment` on p26.

### The new theorem

**Theorem 10.8 (rational steps stabilize).** For $D=d/2$ rational and any real
$r$, there is a finite $N_0$ with $W_N(r,d)=W_\infty(r,d)$ for $N\ge N_0$; and at
positive nonintegral rank $W_\infty$ is a finite union of closed intervals and
isolated points in $[0,D\lceil r\rceil]$ with endpoints in $b^{-1}Z$.

Nothing new is needed to prove it. Proposition 9.2 cages the locus in a bounded
interval past degree $k+1$; every spectral root is a cell value
$(i-1)D-(j-1)\in b^{-1}Z$; so on $[0,kD]$ each $W_N$ is a union of members of a
fixed stratification into $2bkD+1$ strata; and $W_N$ is decreasing because it is
an intersection over a growing index set. A decreasing sequence of subunions of a
finite stratification terminates. Integral rank is Theorem 8.4, rank zero is
Proposition 11.2, and negative rank transports through Theorem 11.1 cutoff by
cutoff.

This retires the paper's own open question. Section 10.4 previously asked whether
the three unresolved examples stabilize at all; they must, since $D=3,5,3/2$.
What remains open is now sharper and is stated as such in Section 12: the
threshold and closed form at rational nonintegral defect, and whether finite
stabilization holds at *irrational* step, where the cell lattice is dense and the
stratification argument has nothing to work with.

### Local corrections

- **Lemma 10.4 was false as stated.** It asserted an identity of subsets of
  $[0,D]$ whose right-hand side was not inside $[0,D]$: at $D=3/2$, $M=4$ the
  right side contains $2$. Restated over all of $R$ as
  $\{0,\dots,M-2\}\cup[M-1,\infty)$, which is the actual one-dimensional
  mechanism (a nonintegral $\sigma\ge0$ has its first negative falling factorial
  at order $\lfloor\sigma\rfloor+2$; an integral one reaches zero there and stays
  zero). Theorem 10.5's proof now intersects with the terminal chamber
  explicitly, which is legitimate because there $M_N\le\nu<D$. Downstream results
  were never damaged.
- **Corollary 9.7's trichotomy omitted $\nu=0$.** It did not assume nonintegral
  rank, and integer rank satisfies $b\nu\in Z$ while failing all three cases.
  Repaired the stronger of the two ways the reviews offered: hypothesis $r>0$
  added and case (ii) widened to $\nu\in Z_{\ge0}$, so $\nu=0$ recovers the
  integer-rank length ideal generated by $(k+1,1)$ and eq:mincell still returns
  it with $m=t_0=0$. Proposition 9.6 immediately before it is not restricted to
  fractional rank, so the corollary should not have been either.
- **Corollary 10.7's proof used Theorem 10.5 one degree below its hypothesis.**
  When $\nu=1$, $N_*-1=k<k+1$. The $\nu=1$ case is now argued directly: at cutoff
  $k$ every partition has at most $k$ rows, so all pivots are nonnegative for
  $s\ge(k-1)D$ and $W_k$ contains the whole ray while $W_\infty$ stops at $kD$.
  The $\nu\ge2$ argument is unchanged. Also fixed a literal index error in the
  same proof: the erosion event replaces $[m-2,D]$, not $[M-1,D]$.
- **Theorem 9.9 claimed to decide what it only protects.** Condition (85) is
  sufficient, not necessary. Retitled *A lattice-gap criterion protecting the
  upper edge*, and the exact criterion that was buried in following prose is
  promoted to **Proposition 9.10**: erosion occurs iff some diagram misses $Z$
  and meets $M$ in odd cardinality. The integer-$D$ trichotomy stays as the
  $b=1$ case.

### Scope and attribution

- The abstract said "at fractional rank the Wallach ray becomes a bounded locus."
  False at negative fractional rank: Theorem 8.4 gives $W_\infty(1,1)=[0,\infty)$
  and Theorem 11.1 sends it to $W_\infty(-1/2,4)=(-\infty,0]$. Now reads
  *positive* nonintegral rank. Theorem 9.1 and Proposition 9.2 gained the same
  qualifier in their titles.
- Corollary 6.2 no longer requires $f$ to be a determinant or a prehomogeneous
  relative invariant; any polynomial with a compatible Bernstein--Sato polynomial
  suffices, with those as the principal examples.
- The Borodin--Olshanski background now names the fat-hook degenerate series and
  says that the integral-defect rank-null ideal *is* one of them: the surviving
  diagrams satisfy $\lambda_{k+1}\le\nu$, i.e. containment in the fat hook with
  arm $k$ and leg $\nu$. Leaving the nearest predecessor incompletely described
  was the largest attribution risk in the paper.
- The claim that the two period conditions are independent and "neither implies
  the other" was wrong at its own example: at $h=1/2$, $h$-periodicity *does*
  imply unit periodicity. Restated as invariance under $Z+hZ$, with neither
  condition discardable uniformly in $h$.
- Table 1's caption asserted that erosion is governed by $\nu$ and not by $d$.
  True of the displayed rows only, because all of them have even $d$ hence
  integral $D$; the paper's own $(3/2,3)$ example erodes with $\nu=3/4<1$. The
  caption now carries the same arithmetic qualifier Figure 3 already had.
- The $(3/2,10)$ locus was described as carrying "more than one interior
  interval"; it has one interval and several connected components. Fixed.
- Section 12's $(3/2,4)$ definiteness claim is now cutoff-indexed: definite for
  $N<6$, semidefinite but not definite for $N\ge6$.
- The supplementary-material note no longer claims `verify_section8.py` audits
  *every* claim of Sections 8--11. It recomputes the computational claims; the
  structural theorems, literature identifications, and scope statements are not
  machine-checkable and are stated not to be checked.

### Presentation

- Section 7's logarithmic deformation exponent was $D(r,s)$ while
  Sections 8--12 use $D=d/2$. Renamed to $E(r,s)$: 54 tokens inside Section 7,
  scoped so that no $D=d/2$ was touched. The eight capital Ds remaining in that
  section are English words.
- A `Part II. Fractional-Rank Positivity` divider with a `\clearpage` now marks
  the analytic/positivity division, landing at the top of p27 above Section 8.
- Section 10's opener described only Section 10.1; it now names all three
  arithmetic regimes.
- Section 1.4's closing paragraph explained that the section titles tell the
  story, which is the sort of thing a manuscript should do rather than announce.
  Replaced by a three-stage summary keyed to `\ref`s, so it cannot go stale
  again.
- Three stale "Section 8" references updated to "Sections 8--11", and the two
  multi-argument `\Cref`s split so cleveref capitalizes each result type instead
  of rendering "Theorem 9.9 and corollary 10.7".
- Affiliation is now `Independent Researcher`; the contact address was changed to
  `zack@internetuniverse.org`.

### Verification

`verify_revision6.py` is new. `verify_section8.py`, `verify_revision5.py` and
`verify_revision6.py` all pass.

The new file audits Theorem 10.8 ingredient by ingredient rather than trusting
the assembled argument: **E1** every spectral root lies in $b^{-1}Z$ across 13
rational steps and all partitions to degree 7; **E2** the locus is a bounded
subset of $[0,kD]$ past degree $k+1$; **E3** monotonicity, $s\in W_{N+1}\Rightarrow
s\in W_N$; **E4** membership is constant on each open stratum, with stratum counts
5--31; **E5** the three formerly open examples are constant over the windows the
paper claims; **E6** the irrational obstruction, the minimal distance from $tD$ to
$Z$ shrinking as claimed. Then **F** the unbounded negative-rank locus forcing the
abstract's qualifier, **G** the $\nu=0$ cell, **H** the restated Lemma 10.4 over
$(1/8)Z$ on $[-5,25]$ for $M=1..8$ plus a check that the old $[0,D]$ form was
literally false, and **I** the $\nu=1$ case of Corollary 10.7.

One test failure worth recording, because it was the test and not the paper.
E5's first version used the window $11\le N\le13$ for $(3/2,10)$ and failed: there
is an erosion event at exactly $N=12$, so a window opening at 11 straddles it and
the locus is correctly non-constant. Narrowing to the window the paper actually
claims, $12\le N\le13$, passes. This is the second time a first-draft test has
failed against a correct paper; both times the cause was the test reaching
outside the region the paper's claim was scoped to.

### Not done

The Ruijsenaars notation crosswalk on pp22--25 is still in the main text. Review 1
says it "could move to an appendix without weakening the main argument" and files
it under minor; moving it is a structural change to a proof that is currently
correct, so it is left for a decision rather than made silently. The
Mellin/Watson half-sector derivation remains in the main text for the same
reason.


## Revision 7 (this build)

Review `review-last11` applied: two blockers, six required corrections, a
terminology sweep, and the three optional upgrades the reviewer rated worth
adding. **56 pages, 0 errors, 0 overfull, 0 underfull, 0 undefined references,
no Type 3 fonts.** `pagecheck` reports one stranded heading on p24 (7.6, three
lines under it) in place of the previous thin-box-segment.

### The supplement, and a note on verify_positivity.py

The reviewer's supplementary-material paragraph names a script
`verify_positivity.py`. **It did not exist** -- the name was the reviewer's
proposal, not a reference to something missing from the tree. It exists now, as
a driver over the three suites that were already here plus the checks new to
this round. The three older files are kept because each is independently
runnable and each was written against a specific review, but nobody needs to
know that: `python3 verify_positivity.py` is the whole interface.

Archive scaffolding added for the DOI deposit: `README.md`, `LICENSE` (CC BY 4.0
for the paper, MIT for the code), `CITATION.cff`, `.zenodo.json`,
`requirements.txt`, `MANIFEST.md` with SHA-256 of every file, and
`tools/manifest.py` to regenerate the digests. Two placeholders in `README.md`
must be filled at deposit time: the DOI and the tagged commit hash. The paper's
supplementary-material paragraph refers to both without hardcoding either.

### The two blockers

**Figure 4 was internally inconsistent.** It carried a secondary top axis
labelled `s = kD - sigma` whose ticks increased left to right -- impossible under
an orientation-reversing map; at `kD = 4` they had to read 4,3,2,1,0. It also
ordered `M = 1` at the bottom while the caption called the bottom row the stable
one, so "lost relative to the one above" pointed the wrong way. Regenerated
rather than patched: the second axis is gone (the relation is stated in the
caption), levels run downward so the bottom row genuinely is the stable row, the
continuous endpoint advances right by one per level, and faded segments are
labelled "removed at this level". The caption is now literally true of the
picture.

**Table 1 had been separated from its caption by a whole figure page.** It is now
a single `table` float with the caption above the tabular, `placeins` is loaded,
and a `\FloatBarrier` follows it. The tabular was also split into two stacked
blocks (N = 4,6,8 and N = 9,10), which both enlarges the type from `\footnotesize`
to `\small` as the reviewer asked and fixes the overfull box that the larger type
would otherwise have caused.

### Required corrections

- **Page 49 contradicted Corollary 9.7.** It said that for "the remaining
  nonintegral-defect cases" no rank-null ideal exists, which is false whenever
  `b*nu` is an integer but `nu` is not -- the paper's own `(2/3,3)` example. The
  paragraph now splits nonintegral defect into its two arithmetic classes and
  says which mechanism is available in each. Verified that `(2/3,3)` has
  `b*nu = 1` in Z with `nu = 1/2` not in Z, and that `(3/2,6)`, `(3/2,10)`,
  `(3/2,3)` all have `b*nu` not in Z, so the three examples really do belong to
  the no-ideal class the corrected paragraph assigns them to.
- **Part I was missing** while Part II was announced. Added, and the pair
  retitled *Analytic Continuation and Carrier Obstructions* / *Formal Positivity
  at Fractional Rank*, the "formal" being a scope guard.
- **Proposition 7.7 did not say which logarithmic lift it expands.** Another
  lift differs by a constant in `2*pi*i*Z`, which cannot be absorbed into
  `O(s^{-M-1})`. Now fixed to the lift in (10) with the principal logarithm.
- **Lemma 7.1's proof still differentiated `D`** after the round-6 rename to `E`.
  Both occurrences fixed. The Bernoulli convention moved from Proposition 7.7 up
  to Proposition 7.6, which was using `B_j(1)` before it was defined.
- **The Landsberg--Manivel pointer was wrong.** The decomposition
  `J_3(S) = J_3(H) + A_3(H^perp)` and the square-zero radical are in their
  section 8.2, not sections 3-4. Fixed.
- **The z-measure novelty boundary now cites propositions, not sections:**
  Prop. 1.2 for the principal/complementary classification, Props. 1.3 and 1.4
  for the row, column and fat-hook degenerations, with Petrov added to the
  bibliography. The chamber identification is also stated precisely -- the
  chamber *interior* is the complementary series, the boundary is semidefinite
  degeneration -- in the body and in the abstract.

### Optional upgrades taken

- **Corollary 12.1**, the formal separation theorem the title promises, which
  the paper previously delivered only in concluding prose. Each clause is a
  specialization of an existing result; part (iii) is the balanced-point identity
  `pi_lambda(rD) = F(rD)^2 / (D^|lam| H_lam) >= 0`, verified across 7 steps and 8
  real ranks including negative ones, together with the definiteness dichotomy at
  `rD` in or out of the content set.
- **Proposition 8.3**, the finite-cutoff Gram determinant. Because the Jack basis
  diagonalizes the pairing, `det G_N` factors over cells with multiplicity
  `m_N(i,j)`, packaging every rank wall, spectral wall and multiplicity into one
  formula. Verified against the direct product of pivots over 6 steps, 4 ranks,
  5 spectral points and 3 cutoffs.
- **Table 2**, the arithmetic-regime map, at the head of Section 10. Verified
  that the three conditions are exhaustive and mutually exclusive. This is also
  what the corrected page-49 paragraph now points at.
- **Remark 8.3**, the two-point cell kernel `Pi_{lambda,D}(x,y)`, with the
  Hermitian specialization `y = conj(x)` giving `|F|^2 / (D^|lam| H_lam) >= 0` as
  the complex principal-series companion, and conjugation acting by
  `(D,x,y,lam) -> (1/D, -x/D, -y/D, lam')`. This exhibits the chamber theorem and
  the duality as two slices of one object.

### Terminology and scope sweep

`cell lattice` -> `content set` throughout (9 occurrences), since for irrational
`D` the set is dense and calling it a lattice is exactly the sort of thing a
referee circles; `content grid` is reserved for the rational case where it really
is `b^{-1}Z`. The carrier claim in the introduction is now qualified by the
affine compatibility condition rather than excluding "a finite-dimensional
determinant carrier" outright. Theorem 5.1 says *not rational* rather than
*transcendental*. Corollary 10.7's `nu = 1` clause no longer says "no erosion
occurs", which ignored the initial capping, but "the capped band is already
stable at cutoff k+1". The `N` convention is stated once and for both parts, and
Part II opens by saying `D = h = d/2`. Remark 6.1, Remark 12.2, Section 8.3 and
Section 10.4 retitled as suggested. The abstract was replaced with the reviewer's
version, which is shorter and states the chamber result precisely.

### Not done

The reviewer's *Simplification and restructuring* section is advisory and is not
applied: the introduction is not condensed by a page, Section 9.5's inertia
counts and extended census are not moved to the supplement, Section 12 is not
consolidated into three parts, and the Ruijsenaars notation crosswalk on p23 is
still in the main text. All four move correct material out of a correct paper for
reasons of pace; they are judgement calls about the author's voice rather than
defects, and are left for a decision rather than made silently. The reviewer
explicitly agrees the paper should **not** be split.


## Revision 8 (this build)

The merged repair specification `merged-review-repair-spec.md` applied. Built with
Etch & Sketch v2.3 under TeX Live 2023 (`lualatex`), four passes: **59 pages, 0
errors, 0 overfull boxes, 0 underfull boxes, 0 undefined or multiply-defined
references.** No Type 3 fonts. `tools/pagecheck.py` reports **no page-break
issues**, where the pre-revision source reported one stranded heading on p53.

### What was already done

Most of the merged specification had already landed in Revision 7, which applied
the same review under the name `review-last11`. This was checked against the
source rather than taken from the changelog: Stage A (R-01, R-P1, R-P2, R-P4,
R-P8, R-P9), Stage B (R-02, R-03), R-04, R-S8, all of Stage D, all of Stage E,
R-F1, R-F3, and all four Stage G upgrades were verified present. What remained
was Stage C, which is exactly what Revision 7 filed under *Not done*.

### Structure

- **The introduction is rebuilt.** Section 1.3's seven `\paragraph` mini-summaries
  are replaced by four paragraphs: construction and exact functional equations;
  termination and the polynomial-carrier obstruction; then the reviewer's own two
  paragraphs verbatim, the hinge (*"the loss of a determinant does not force
  positivity to disappear"*) and the positivity overview. The section loses its
  theorem-level previews and about a page. The organization paragraph in 1.4 loses
  the sentence the fourth paragraph now covers.

  Note on locating the reviewer's target: the second review anchored its
  replacement to three strings, `Thus`, `the same affine root data`, and a
  trailing outline sentence. Only the last two are in the current build, and they
  are in the Section 8 bridge, not the introduction. The two reviews were reading
  different drafts. The replacement text is introduction register and the merge
  places it as paragraphs 3 and 4 of 1.3, so that is where it went; the Section 8
  bridge is untouched.

- **The Ruijsenaars crosswalk moved.** The two-page notation reconciliation inside
  the proof of Proposition 7.7 is now **Lemma 7.6** (*Sectorial continuation of the
  Barnes remainder*), which states only what the proof consumes -- holomorphic
  continuation of the truncated remainder to `C \ (-inf,0]` and the
  `O(|a|^{-M-1})` bound on `|arg a| <= pi - delta` -- plus **Appendix A**, an
  eleven-row translation table. The half-sector computation stays in the body,
  since it identifies the coefficients from this paper's normalization rather than
  importing them.

- **Section 9.5 trimmed.** The three conceptual archetypes are kept: odd-`d` upper
  edge erosion, lower-edge erosion, and one-step erosion halted by a rank-null
  ideal. The exact inertia count at `(3/2,8)`, cutoff 6, and the two receipts on
  either side of the `nu = 1` threshold now point at the ancillary data. Table 1
  is **not** moved: the specification lists "the extended census" among the
  material to relocate, but the only thing answering to that description is
  Table 1, which R-03 in the previous round explicitly rebuilt and enlarged.
  Moving it would undo a blocker fix. Flagged rather than guessed.

- **Section 12 consolidated** into *The Separation*, *Interpretation and
  Limitations*, and *Open Problems*. The four remarks fold into the second, except
  Remark 12.2, which keeps its identity under the title it was given last round.

### Mathematics added

Both are consequences of Theorem 10.8 and Theorem 11.1 that the specification
asked to be recorded and that were not in the source.

- **Corollary 10.9** (*Finite certificate*). At rational step,
  `W_infinity(r,d) = intersection over a finite family F(r,d) of {s : pi_lambda(s) >= 0}`.
  Immediate from Theorem 10.8. This is where the effectivity gap sits: existence
  of a certificate without a bound on its degree.
- **Corollary 10.10** (*The stabilization degree is self-dual*).
  `N_0(-rD, 4/d) = N_0(r,d)` whenever either side is defined, because partition
  conjugation preserves degree and so matches the loci cutoff by cutoff. This says
  the effectivity gap is one problem and not two, and Section 12's open problems
  now say so.

### Terminology and front matter

`Cell-lattice chamber positivity` and `The Cell Lattice Generates a Principal
Rank-Null Ideal` were the two surviving places where the content set was still
called a lattice; both renamed. Section 1.1 still carried
*"Throughout, N denotes an integer rank and r a complex one"*, which contradicts
the Part I / Part II convention installed two paragraphs above it; the clause is
gone and the Jordan-algebra scope guard kept. The keyword list is the reviewer's
seven.

### Figures

**Figures are renumbered**, because the new figure lands in Section 9.1 and
therefore takes the number 3. The files are renamed to match, so a filename and a
figure number never disagree again:

| file | figure | section |
|---|---|---|
| `fig1-cocycle-split.pdf` | 1 | 4 |
| `fig2-divisor-cancellation.pdf` | 2 | 5 |
| `fig3-cone-strata.pdf` | 3 | 9.1 (new) |
| `fig4-positivity-loci.pdf` | 4 | 9.5 (was fig3) |
| `fig5-erosion-staircase.pdf` | 5 | 10 (was fig4) |

- **Figure 3 is new.** It is the only figure in the paper that draws a
  correspondence rather than a computation. Left panel: at integer rank `R = 3`
  the Riesz distribution is a positive measure exactly on the Wallach set
  (Faraut--Koranyi Thm. VII.3.1), and at a ladder point `s = jD` its support is
  the closure of the rank-`j` orbit (Prop. VII.2.3), so `s |-> supp R_s` carries
  the ladder onto the flag `{0} < O_1-bar < boundary` and the ray onto the
  interior. Right panel: at `r = 3/2` there is no cone, hence no interior stratum
  for a ray to be supported on, and what survives is the retained grid, the band,
  the balanced point and the cap. The ray is drawn as the hollow channel it used
  to occupy. This is the paper's subtitle in one picture, and it was the one thing
  the figure set did not show: the geometry the argument is *against*.

  Both panels are checked. See `verify_figure3.py`.

- **Figure 4** (the loci) now carries, on each fractional row, the integer-rank ray
  that row lost, drawn as a hollow channel from the top of its locus to the right
  edge. The amputation was previously visible only by comparing rows across a
  hairline; it is now on the row. The two blocks are also named on the figure
  rather than in the fifth sentence of the caption.

- **Figure 1** draws the `(2*pi)^{h r q}` normalization as an `r` by `q` rectangle
  labelled with its area, so the one term that was pure bookkeeping is now a
  measurement. It also gains the axis arrowhead the other four figures have.

Palette discipline in Figure 3 follows the file's documented semantics: blue is
the object being tracked, so it is the interior -- the thing fractional rank
removes; the three boundary strata are ink at three weights; wine is the
obstruction, hence the lost ray; amber is the cap; forest is the balanced point.

### Verification

`verify_figure3.py` is new and is wired into `verify_positivity.py`, which is
still the whole interface. It checks the figure's two panels by different means,
because they rest on different things. The left panel's classical dictionary is
not recomputable from this paper's machinery, so what is checked is the weaker
statement the figure needs: that the paper's own integer-rank theorem reproduces
the ladder-plus-ray the flag is paired with. The right panel is checked mark by
mark against the locus routine -- retained grid, band at cutoff `k+1`, balanced
point strictly interior, cap retained, and 29 probes above the cap confirming the
ray is absent -- at each of `d = 2, 4, 6, 8`. A final group checks the caption's
own hedge, that the band is stable at `d = 2, 4` and erodes at `d = 6, 8`, so that
drawing `W_pre` rather than `W_infinity` is necessary and is what the caption
says. 28 checks, all pass.

One test failure worth recording, because it was again the test and not the
paper. The erosion group first compared `locus()` output as a whole tuple and
reported `d = 2` and `d = 4` as eroding. `locus()` returns
`(isolated points, closed intervals, breakpoints)`, and the third component is
the stratification the routine searched, which necessarily grows with the cutoff.
The loci were identical. Comparing only the first two components passes. This is
the third time a first-draft test has failed against a correct paper.

`verify_positivity.py` now runs four suites plus the extra checks: 83 checks,
all pass. One of them independently confirms the new Corollary 10.10 --
`s in W_N(r,d)` iff `-s/D in W_N(-rD, 4/d)` at every cutoff, 2184 probes, 0
violations.

### Not verified

The figures were generated and checked programmatically -- text extraction from
the built PDF confirms every label, and a pixel scan of the rendered raster
confirms the position and colour of every mark -- but they were **not visually
inspected** in this session. Look at Figure 3 before trusting it.

### Still blocked

The DOI and the tagged commit hash for the supplementary-material paragraph.
`README.md` still carries both placeholders.


## Revision 9 (this build)

Review item 8, the Bergman--Wallach branch, landed as **Section 8.5**. Built with
Etch & Sketch v2.3: **61 pages, 0 errors, 0 overfull, 0 underfull, 0 undefined or
multiply-defined references**, no page-break issues.

### Why it belongs here, and what changed on the way in

The item was written against the Gibbs-chart manuscript -- the sentence it
quotes, about a convexity proof that "needs no identification of a distinguished
Gram entry with a full Bergman kernel", is that paper's, not this one's, and this
paper has no convexity proof and no Bergman anything. Two of the item's three
parts therefore had no target here: there was no exclusion sentence to repair,
and this paper never made the scalar mistake, since Proposition 8.2 already works
with the whole Gram matrix.

The third part is the one that fits, and it fits more tightly than the item
claims. Proposition 8.2 makes `G_N(r,s)` **diagonal** in the Jack basis, so the
matrix inverse the item asks for is immediate and the reproducing kernel of the
model is a sum over partitions with the pivots in the denominators. That kernel
is the object the Wallach set is classically defined by -- Faraut--Koranyi
Ch. XIII.2 defines the set as the parameters at which the weighted kernel is of
positive type -- so the paper's `W_N(r,d)` was already a continuation of a
positive-type locus without saying so.

The item calls the correspondence between discrete Wallach points and
multiplicity collapse an analogy and recommends recording it as an open problem.
In this paper it is a **theorem**, and its proof is already inside the proof of
Theorem 8.4, in the ladder-points step, unextracted. Recording it as open would
have understated what the paper proves.

The item's labelling also needed one correction. It proposes discrete Wallach
points against *one-dimensional* Bergman collapse. The correct statement is
graded: the `j`-th ladder point collapses the model to `j` rows, and
one-dimensional is the case `j = 1`.

### What was installed

- **Definition 8.6**, the reproducing kernel `B_{N,r,s}` of the model, with the
  sum form immediate from diagonality of `G_N`. Named a reproducing kernel rather
  than a Bergman kernel: in Faraut--Koranyi the Bergman kernel is the member of
  the family at one distinguished parameter, and calling the whole family Bergman
  would be loose. The relation to `det G_N` of (gram) and to `W_N` of (loci) is
  two sentences and no argument.

- **Remark 8.2**, that a single Gram entry constrains nothing. Two witnesses: the
  Sylvester one-liner, and the sharper fact that in a basis which does not
  diagonalize the form the scalar surrogate is not merely uninformative but
  false. For the moment form on `span{1, x}`, `det G(s) = Gamma(s)Gamma(s+1)` and
  the kernel diagonal is `((x-s)^2 + s)/Gamma(s+1)`, whose logarithm at `x = 1`
  is **not** concave on `[1/2, 1]`, where the multiplicity-one surrogate
  `-log Gamma` is concave by Bohr--Mollerup. Checked numerically at three
  interior points. This is the item's own counterexample; its stated value
  `(3/2)Gamma(3/2)^{-1}` should read `(3/4)Gamma(3/2)^{-1}`, though the number
  `3/(2 sqrt pi)` it reduces to is right.

- **Proposition 8.7**, the collapse: `F_{lambda,D}(jD) = 0` iff
  `ell(lambda) > j`, for every integer `j >= 0` and **every** `D > 0`, with no
  rationality hypothesis. Hence at `s = jD` the null space contains the span of
  the Jack polynomials of length exceeding `j`, with equality off the rank-null
  locus, and the quotient has basis the Jack polynomials of `j` variables. The
  kernel descends to the reproducing kernel of that `j`-variable model.

  This is the algebraic form of the correspondence Figure 3 draws. At integer
  rank the Riesz distribution at `s = jD` is supported on the closure of the
  rank-`j` orbit (Faraut--Koranyi Prop. VII.2.3); here the same `j` counts the
  rows the model keeps. Functions of `j` variables are what a measure carried by
  rank-`j` elements can see.

  Two limits are stated with it: the collapse is about this formal model and
  constructs no Hilbert space, and (collapse) is indexed by integers, so it
  speaks at the retained grid of Proposition 9.3 -- including the cap, where the
  model collapses to `ceil(r)` rows -- and says nothing about band interiors.

- **A fourth open problem** in Section 12, which is the item's `op:wallach-bergman`
  restated at what actually remains open. Not whether the index identity holds --
  Proposition 8.7 settles that for this model -- but whether any genuine Hilbert
  space of functions reproduces `B_{N,r,s}` at nonintegral `r`. That is the
  natural successor to Proposition 6.4: it obstructs the polynomial determinant
  carrier and says nothing about a reproducing one, and the positivity of
  Sections 8--10 is exactly the hypothesis such a carrier would need.

### Verification

`verify_figure3.py` grows from 28 to 32 checks and keeps the single entry point.
(collapse) is checked at 6048 probes across nine values of `D` including
irrational-ratio and unit cases, 0 mismatches; the quotient basis is checked
against the length filter at twelve `(D, j)` pairs; and Remark 8.2's
counterexample is checked in both directions, that the multiplicity-two curve
falls below its chord and the multiplicity-one control rises above it, at the
same three interior points.

`verify_positivity.py`: 87 checks across four suites plus extras, all pass.

### Not verified

Nothing new is unverified beyond what Revision 8 already recorded: the figures
still have not been visually inspected in-session.


## Revision 10 (this build)

Two false claims installed in Revision 8.5 removed, and the Section 9.5 archive
pointers made to resolve. **61 pages, 0 errors, 0 overfull, 0 underfull, 0
undefined or multiply-defined references**, no page-break issues. 87 checks pass.

### Two errors of my own, found by testing rather than re-reading

Both were in the paragraph joining Definition 8.6 to Proposition 8.7. Both were
written as "immediate from (56) and cost no argument", which is the tell: the
sentence claimed the reasoning was too obvious to check, and neither claim
survived being checked.

- **"`W_N(r,d)` is the closure of the positive-type locus of `B`."** False, and
  not marginally. The strict locus where every `pi_lambda(s) > 0` is *empty* as
  soon as the cutoff admits a rank-null partition, because such a pivot vanishes
  identically in `s`. At integer rank that is the generic case: by Theorem 8.5
  every `lambda` with `ell(lambda) > R` is rank-null, so at `(R, d) = (3, 8)` and
  `N = 4` the strict locus is empty while `W_N = {0} u {4} u [8, inf)`. The claim
  would assert that this set is the closure of the empty set. Even ignoring the
  rank-null ideal it fails, because the isolated ladder and cap points have no
  strictly positive neighbours and so are not in the closure of anything.

  Replaced by the correct statement: `W_N` is where the form is positive
  semidefinite, hence where the kernel descends to a kernel of positive type *on
  the quotient by the null space*; the gap between the two sets is where
  `det G_N` vanishes, and it contains the retained ladder points of
  Proposition 9.3 and the isolated cap points of Remark 12.1. Describing the
  quotient there is what Proposition 8.7 does, so the correction makes 8.7 the
  resolution of the gap rather than a coda.

- **"the erosion of Section 9 is precisely the failure of any proper subfamily to
  decide the locus."** This contradicts Corollary 10.9, installed in Revision 8,
  which supplies a finite -- hence proper -- family that does decide the locus.
  At `(3/2, 8)` the family `{|lambda| <= 6}` decides `W_infinity` exactly.
  Replaced by what erosion actually shows: a family truncated *below the
  stabilization degree* gets the locus wrong, and no bound on the degree of a
  deciding family follows from the finite-cutoff computation. That is the
  effectivity gap Corollary 10.9 records, stated consistently with it.

Proposition 8.7's null-space clause also now carries the cutoff `|lambda| <= N`,
which the quotient clause already carried; the asymmetry was harmless but wrong.

### The Section 9.5 pointers now resolve

R-S5 required that anything relegated from Section 9.5 be reachable in the frozen
archive. Three things were relegated in Revision 8 and the text pointed at them
as "the ancillary data" and "the ancillary census" -- naming no file. Of the
three, only the inertia was emitted anywhere (`verify_section8.py`); the exact
value of the witness rank factor and the threshold census were emitted nowhere.
A reader following those pointers would have found nothing.

`ancillary_census.py` is new and emits all three:

1. `F_{(3,3,3,3), 3/2}(9/4) = 310134825/16777216`, with the sign of the pivot at
   three interior points of `5/2 < s < 3` confirming the text's conclusion.
2. The full inertia at `(3/2, 8)`, cutoff 6: `(29, 1, 0)` at seven points across
   the open cell `7 < s < 8`, constant, with `(2,2,2)` the unique null mode
   at `s = 7`.
3. The threshold census, six `(r, d)` pairs on both sides of `d = 4`.

All three pointers in the text, and the supplementary-material paragraph, now
name the file.

A discrepancy surfaced while writing it. The census first reported inertia
`(28, 1)` against the paper's `(29, 1)`. The paper was right: the Gram matrix on
`V_N` is indexed by every `|lambda| <= N`, the empty partition included, and
`pi_empty = 1 > 0` as an empty product. The first draft of the census had
filtered the empty partition out. This is the fourth time a first-draft test has
failed against a correct paper.

The census also strengthens the text it supports. It shows `(3/2, 3)`, with
`nu = 3/4 < 1`, eroding anyway -- because `D = 3/2` is not an integer and the
trichotomy of Theorem 9.9 requires `D` in `Z`. So neither the multiplicity nor
the defect alone governs, which is what Section 9.5 asserts; the sentence now
points at a case that makes the second half of that assertion visible too.

### Found and deliberately not fixed

Remarks run on a counter separate from theorems, propositions, lemmas,
definitions and corollaries. Every section with a remark therefore has a
collision: Remark 4.1 against Theorem 4.1, Remark 7.1 and 7.2 against Lemmas 7.1
and 7.2, Remark 8.1 against Definition 8.1, Remark 9.1 against Theorem 9.1,
Remark 10.1 against Theorem 10.1, Remark 12.1 against Corollary 12.1 -- and now
Remark 8.2 against Proposition 8.2.

The new one is the worst of them, because Remark 8.2 and Proposition 8.2 are
both about the Gram matrix and sit three pages apart, whereas the other pairs are
unrelated objects. But the convention is the paper's, it predates every review
round, and merging the counters would renumber essentially every result in the
document and invalidate every external reference to it. Flagged rather than
changed.

Also flagged and not changed: Section 8.2 cites "(Theorem 9.9, Corollary 10.7)"
for determining "the first cutoff at which the band loses a point and the exact
degree at which it stops moving". Corollary 10.7 does both. Theorem 9.9 is a
criterion for *whether* the upper edge erodes and determines no cutoff. This is
in the z-measure attribution subsection, where what is and is not claimed matters,
so it is quoted rather than silently repaired.


## September 2026 build (release v1.1.0)

Typeset with Etch & Sketch v2.5 (the kit's own version string:
`\ProvidesPackage{etch-math}[2026/08/02 v2.5 ...]`; the "v5"/"v6" labels in the
notes above are earlier round numbers, not kit versions), LuaHBTeX 1.24 under
MiKTeX 25.12: **60 pages, 0 errors, 0 overfull boxes, no undefined or
multiply-defined references**, and `tools/pagecheck.py` reports no page-break or
math-font faults. The sequence of numbered environments and the count of equation
environments are unchanged from revision 10, so every statement and equation
number matches it.

What changed against revision 10:

- The preamble patch that appended `title after break={... (continued)}` to both
  plate styles is removed; kit v2.5 sets the continuation title itself.
- Title block: ORCID added, date September 2026.
- Table 1 caption: the stability of the d = 4 row is now attributed to Corollaries
  10.6 and 10.7 (stable from N* = 3) and the d = 2 row to Theorem 10.1, instead of
  to the upper-edge trichotomy of Theorem 9.9.
- After the defect definition, one sentence: at half-integer rank nu = d/4, which is
  an integer exactly when 4 | d. Inline, so no equation numbers move.
- The citation flagged in revision 10's "Found and deliberately not fixed" is fixed:
  Section 8.2 now cites Corollary 10.7 alone (at integral defect) for the first
  cutoff at which the band loses a point and the degree at which it stops moving.
  The Remark-counter collision noted there is still not changed.
- The supplementary-material paragraph now points to this release and to the
  concept DOI, and names `ancillary_census.py` and `verify_positivity.py`.
- Prose: five "not merely / not fundamentally" constructions made direct, and a
  passage that appeared twice (that (r,d) = (3,6) is formal) now appears once.
- A stranded heading (9.3) is kept with its text by `\Needspace*`, the device the
  paper already uses before three other headings.

Verification for this release: `python3 verify_positivity.py` ends with
`ALL COMPUTATIONAL CLAIMS OF SECTIONS 8-11 VERIFIED` (87 checks in four suites plus
the in-file extras, 0 failed, about 25 s on Python 3.14.6 with SymPy 1.14.0 and
mpmath 1.3.0); `ancillary_census.py`, `verify_figure3.py` and
`recompute_table.py` run clean. The Figure 3 suite and `ancillary_census.py`
import `figs/wallach_locus.py`, which needs SymPy; revision 10's
`requirements.txt` still said the verification was standard library only, and
this release corrects it. Without SymPy the full run reports
`FAILED SUITES: figure`, and `--quick` still passes.
