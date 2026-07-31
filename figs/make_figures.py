"""
Figure generation for 'The Barnes--Gindikin Symbol'.

Register
--------
These figures are drawn through the Etch & Sketch matplotlib companion
(`es_figure.py`, vendored beside this file together with
`etch-and-sketch.mplstyle`), with `backend="pgf"`. That routes every label
through the *same* LuaLaTeX run and the *same* font selection the document
body uses: TeX Gyre Schola for prose, Libertinus Math for mathematics. The
previous version of this file hand-rolled its own preamble and set figure
prose in Libertinus *Serif*, which is not the body face -- a genuine
typographic mismatch on every page carrying a figure. It also left
matplotlib's default `pdf.fonttype: 3`, which arXiv flags; the kit style sets
42.

Two deliberate departures from the kit defaults, both documented:

1. `bbox_inches=None` instead of the style's `tight`. The document includes
   these with a bare `\\includegraphics`, i.e. at natural size, so the figure
   width must equal the text measure exactly (452.97pt = 6.267in). A tight
   bbox would crop to content and land the figure narrower than the measure.
2. `axes.grid` off, with vertical lattice guides drawn by hand. The kit's
   y-grid is for quantitative y-axes; here y indexes cases, not magnitude.

Fractions in labels are written `$3/2$`, not `\\tfrac32`: the body's
content-aware fraction policy lives in etch-math.sty and a figure preamble
cannot load it, so `\\tfrac` here would stack where the body sets a case
fraction, putting one value in two forms on one page.

Palette is the kit's, unmodified, and used semantically:
  blue   -- the object being tracked (zeros, positivity loci)
  amber  -- the exceptional feature the caption names (isolated cap points,
            the descending edge)
  forest -- the balanced point r*D
  wine   -- obstruction (poles, the cut, area lost to erosion)
  grey   -- controls, guides, and anything cancelled or inert
  ink    -- axes and primary text
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from es_figure import es_style, es_save          # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402
from matplotlib.lines import Line2D              # noqa: E402

es_style(backend="pgf")

# ---- kit palette, named by role -------------------------------------------
BLUE, AMBER, FOREST, WINE, GREY, INK = (
    "#4A6E8A", "#C97D2C", "#4A6B4F", "#8C3A3A", "#6A7986", "#2C3E50")
PANEL = "#FAF7F0"

LABEL = 9.0
TICK = 8.0

plt.rcParams.update({
    "axes.grid": False,
    "axes.facecolor": PANEL,
    "axes.edgecolor": INK,
    "axes.linewidth": 0.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "lines.solid_capstyle": "butt",
    "legend.frameon": False,
    "legend.handlelength": 1.5,
    "legend.handletextpad": 0.5,
    "legend.borderpad": 0.0,
    "legend.columnspacing": 1.6,
    "savefig.bbox": None,
})

TEXTWIDTH = 6.267        # inches = 452.97pt, the document text measure exactly


def _row_axis(ax, y_at):
    """Single bottom rule in ink, no left/right/top spines, no y ticks."""
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK)
    ax.spines["bottom"].set_position(("data", y_at))
    ax.tick_params(axis="x", colors=INK, labelcolor=INK, labelsize=TICK)
    ax.tick_params(axis="y", length=0, labelcolor=INK, labelsize=TICK)


def _guides(ax, xs, y0, y1, color=GREY):
    for x in xs:
        ax.plot([x, x], [y0, y1], color=color, lw=0.4,
                ls=(0, (1.6, 2.4)), zorder=0)


# ======================================================================
# Figure 1 - the cocycle as an interval split
# ======================================================================
def figure_one(path):
    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 2.05), layout="constrained")

    n, cut = 6, 2.5
    xs = list(range(n))
    ax.set_xlim(-0.72, n - 1 + 0.72)
    ax.set_ylim(-1.30, 1.34)

    # the two sub-intervals, shaded so the split reads before the braces do
    ax.axvspan(-0.40, 2.40, color=BLUE, alpha=0.075, lw=0, zorder=0)
    ax.axvspan(2.60, 5.40, color=AMBER, alpha=0.10, lw=0, zorder=0)

    # the argument axis
    ax.plot([-0.5, n - 0.5], [0, 0], color=INK, lw=0.9, zorder=3)
    for x in xs:
        ax.plot([x, x], [-0.075, 0.075], color=INK, lw=0.9, zorder=4)

    labels = [r"$s$", r"$s-h$", r"$s-(r-1)h$",
              r"$s-rh$", r"$\cdots$", r"$s-(r+q-1)h$"]
    for x, lab in zip(xs, labels):
        ax.text(x, -0.21, lab, ha="center", va="top",
                fontsize=TICK, color=INK)

    # the cut
    ax.plot([cut, cut], [-1.00, 1.04], color=WINE, lw=0.8,
            ls=(0, (2.4, 2.0)), zorder=2)
    ax.text(cut, 1.11, "cut", ha="center", va="bottom",
            fontsize=TICK, color=WINE, style="italic")

    def brace(x0, x1, y, label, colour, below=False):
        tip = -0.13 if below else 0.13
        ax.plot([x0, x0, x1, x1], [y, y + tip, y + tip, y],
                color=colour, lw=0.8, solid_joinstyle="miter", zorder=4)
        ax.text((x0 + x1) / 2, y + tip + (-0.11 if below else 0.09),
                label, ha="center", va="top" if below else "bottom",
                fontsize=LABEL, color=colour)

    brace(-0.16, 2.16, 0.30, r"$\mathcal{G}_h(r,s)$", BLUE)
    brace(2.84, 5.16, 0.30, r"$\mathcal{G}_h(q,\,s-rh)$", AMBER)
    brace(-0.16, 5.16, -0.64,
          r"$\mathcal{G}_h(r+q,\,s)\times(2\pi)^{-hrq}$", INK, below=True)

    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"descending $\Gamma$-argument, step $h$",
                  fontsize=LABEL, color=INK, labelpad=26)

    es_save(fig, path, bbox_inches=None)
    plt.close(fig)


# ======================================================================
# Figure 2 - termination as divisor cancellation
# ======================================================================
def figure_two(path):
    """Two tiers per rank: zeros above the row rule, poles below it.

    Coincidence of the two lattices is then geometric -- vertical alignment
    at integer rank, a visible stagger at fractional rank -- instead of being
    asserted by an annotation.
    """
    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 2.55), layout="constrained")

    lo, hi = -4.75, 3.15
    rows = {"int": 1.05, "frac": 0.0}
    TIER = 0.20
    BASE = -0.86

    ax.set_xlim(lo - 0.30, hi + 0.95)
    ax.set_ylim(BASE, 1.80)

    # zeros of R_{r,h}: s = h(r-1-n), n >= 0.  poles: s = -h(m+1), m >= 0.
    data = {
        "int":  dict(zeros=[2, 1, 0, -1, -2, -3, -4], poles=[-1, -2, -3, -4]),
        "frac": dict(zeros=[0.5, -0.5, -1.5, -2.5, -3.5],
                     poles=[-1, -2, -3, -4]),
    }

    for key, y in rows.items():
        ax.plot([lo, hi], [y, y], color=GREY, lw=0.5, zorder=1)
        ax.annotate("", xy=(hi + 0.52, y), xytext=(hi, y),
                    arrowprops=dict(arrowstyle="-|>", color=GREY,
                                    lw=0.6, mutation_scale=7))
        z, p = data[key]["zeros"], data[key]["poles"]
        cancelled = sorted(set(z) & set(p))
        for x in z:
            dead = x in cancelled
            ax.plot(x, y + TIER, marker="o", ms=4.6,
                    mfc=GREY if dead else BLUE,
                    mec=GREY if dead else BLUE,
                    alpha=0.45 if dead else 1.0, mew=0.9, zorder=4)
        for x in p:
            dead = x in cancelled
            ax.plot(x, y - TIER, marker="o", ms=4.6, mfc="none",
                    mec=GREY if dead else WINE,
                    alpha=0.45 if dead else 1.0, mew=1.0, zorder=4)
        for x in cancelled:
            ax.plot([x, x], [y - TIER + 0.055, y + TIER - 0.055],
                    color=GREY, lw=0.7, alpha=0.75, zorder=3)

    ax.text(2.05, rows["int"] + TIER + 0.17,
            r"lattices coincide; $3$ zeros survive",
            ha="center", va="bottom", fontsize=TICK, color=INK)
    ax.text(-2.05, rows["frac"] - TIER - 0.17,
            r"lattices interleave; nothing cancels",
            ha="center", va="top", fontsize=TICK, color=INK)

    ticks = [-4, -3, -2, -1, 0, 1, 2, 3]
    ax.set_xticks(ticks)
    ax.set_xticklabels([r"$-4h$", r"$-3h$", r"$-2h$", r"$-h$",
                        r"$0$", r"$h$", r"$2h$", r"$3h$"])
    ax.set_yticks([rows["int"], rows["frac"]])
    ax.set_yticklabels([r"$r=3$", r"$r=3/2$"])
    _row_axis(ax, BASE)
    ax.set_ylabel(r"formal rank", fontsize=LABEL, color=INK, labelpad=6)
    ax.set_xlabel(r"$s$", fontsize=LABEL, color=INK, labelpad=2)

    handles = [
        Line2D([], [], marker="o", ls="none", ms=4.6, mfc=BLUE, mec=BLUE,
               label=r"zero of $R_{r,h}$"),
        Line2D([], [], marker="o", ls="none", ms=4.6, mfc="none", mec=WINE,
               mew=1.0, label=r"pole of $R_{r,h}$"),
        Line2D([], [], marker="o", ls="-", ms=4.6, mfc=GREY, mec=GREY,
               color=GREY, alpha=0.5, label=r"cancelling pair"),
    ]
    ax.legend(handles=handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.19), ncol=3,
              fontsize=TICK, labelcolor=INK)

    es_save(fig, path, bbox_inches=None)
    plt.close(fig)


# ======================================================================
# Figure 3 - positivity loci
# ======================================================================
def figure_three(path):
    """Rows of exact loci, integer controls above a hairline, fractional
    below. Amber marks an isolated cap point D*ceil(r); a forest caret marks
    the balanced point r*D on which the cell chamber is centred.
    """
    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 3.05), layout="constrained")

    lo, hi = -0.55, 10.45          # rays run to the right edge; no axis break
    #  label, locus symbol, ladder pts, intervals, ray, integer?, cap, rD
    rows = [
        (r"$(2,8)$",   r"$\mathcal{W}_\infty$", [0.0],      [],           4.0,  True,  None, None),
        (r"$(3,8)$",   r"$\mathcal{W}_\infty$", [0.0, 4.0], [],           8.0,  True,  None, None),
        (r"$(3/2,2)$", r"$\mathcal{W}_\infty$", [0.0],      [(1.0, 2.0)], None, False, None, 1.5),
        (r"$(3/2,4)$", r"$\mathcal{W}_\infty$", [0.0],      [(2.0, 4.0)], None, False, None, 3.0),
        (r"$(3/2,6)$", r"$\mathcal{W}_{10}$",   [0.0, 3.0], [(4.0, 5.0)], None, False, 6.0, 4.5),
        (r"$(3/2,8)$", r"$\mathcal{W}_\infty$", [0.0],      [(4.0, 7.0)], None, False, 8.0, 6.0),
    ]
    BASE = -0.72
    top = len(rows) - 0.42
    ax.set_xlim(lo, hi + 0.55)
    ax.set_ylim(BASE, top)

    _guides(ax, range(0, 11), BASE + 0.10, top - 0.14)

    for i, (lab, sym, pts, ivals, ray, integer, cap, bal) in enumerate(rows):
        y = len(rows) - 1 - i
        finite = sym.endswith("{10}$")
        ax.plot([lo + 0.28, hi], [y, y], color=GREY, lw=0.5, zorder=1,
                ls=(0, (2.4, 2.0)) if finite else "-")
        col = GREY if integer else BLUE
        for a, b in ivals:
            ax.plot([a, b], [y, y], color=col, lw=2.8, zorder=3)
            for e in (a, b):
                ax.plot(e, y, marker="o", ms=4.4, mfc=col, mec=col, zorder=4)
        if ray is not None:
            ax.plot([ray, hi], [y, y], color=col, lw=2.8, zorder=3)
            ax.plot(ray, y, marker="o", ms=4.4, mfc=col, mec=col, zorder=4)
            ax.annotate("", xy=(hi + 0.44, y), xytext=(hi, y),
                        arrowprops=dict(arrowstyle="-|>", color=col,
                                        lw=1.4, mutation_scale=9))
        for p in pts:
            ax.plot(p, y, marker="o", ms=4.4, mfc=col, mec=col, zorder=4)
        if cap is not None:
            ax.plot(cap, y, marker="o", ms=5.6, mfc=AMBER, mec=AMBER, zorder=5)
        if bal is not None:
            ax.plot([bal, bal], [y - 0.235, y - 0.075], color=FOREST,
                    lw=1.1, zorder=5)

    # hairline separating the integer controls from the fractional rows
    sep = len(rows) - 2.5
    ax.plot([lo + 0.10, hi + 0.30], [sep, sep], color=GREY, lw=0.5,
            alpha=0.9, zorder=2)

    ax.set_yticks([len(rows) - 1 - i for i in range(len(rows))])
    ax.set_yticklabels([r"%s,\ %s" % (r[0], r[1]) for r in rows])
    _row_axis(ax, BASE)
    ax.set_ylabel(r"$(r,d)$", fontsize=LABEL, color=INK, labelpad=6)
    ax.set_xticks(list(range(0, 11)))
    ax.set_xticklabels([r"$%d$" % k for k in range(0, 11)])
    ax.set_xlabel(r"Wallach parameter $s$", fontsize=LABEL,
                  color=INK, labelpad=2)

    handles = [
        Line2D([], [], color=BLUE, lw=2.8, marker="o", ms=4.4, mfc=BLUE,
               mec=BLUE, label=r"locus at fractional rank"),
        Line2D([], [], color=GREY, lw=2.8, marker="o", ms=4.4, mfc=GREY,
               mec=GREY, label=r"integer-rank control"),
        Line2D([], [], marker="o", ls="none", ms=5.6, mfc=AMBER, mec=AMBER,
               label=r"isolated cap $D\lceil r\rceil$"),
        Line2D([], [], marker="|", ls="none", ms=7.5, mec=FOREST, mew=1.1,
               label=r"balanced point $rD$"),
    ]
    ax.legend(handles=handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.155), ncol=4,
              fontsize=TICK, labelcolor=INK)

    es_save(fig, path, bbox_inches=None)
    plt.close(fig)


# ======================================================================
# Figure 4 - the integral-defect erosion staircase
# ======================================================================
def figure_four(path):
    """Terminal coordinate sigma = kD - s, and ONLY that coordinate.

    The previous version carried a secondary top axis labelled s = kD - sigma
    but drew its ticks increasing left to right, which is impossible under an
    orientation-reversing map: at kD = 4 the upper labels had to read
    4,3,2,1,0. It also ordered M = 1 at the bottom while the caption called
    the bottom row the stable one. Both are fixed here by dropping the second
    axis (the relation goes in the caption) and ordering M = 1..nu downward,
    so the bottom row really is the stable row and "removed at this level"
    points the right way.

    Rows M = 1..nu, first imposed at cutoff N = M(k+1); surviving interval
    [M-1, D], isolated survivors {0,..,M-2}.

    Instance: Albert step D = 4 at rank r = 1/4, so k = ceil(r) = 1, nu =
    D(k-r) = 3 and k+1 = 2. Levels arrive at N = 2, 4, 6 and the staircase
    halts at N_* = nu(k+1) = 6. The bottom row M = 3 reads sigma in [2,4] u
    {0,1}, i.e. s in [0,2] u {3,4}, the all-degree locus W_inf(1/4, 8).
    """
    D, nu, KP1 = 4, 3, 2

    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 2.55), layout="constrained")

    BASE = 0.42
    ax.set_xlim(-0.60, D + 0.92)
    ax.set_ylim(BASE, nu + 0.78)

    _guides(ax, range(0, D + 1), BASE + 0.06, nu + 0.42)

    # M increases DOWNWARD: level M is drawn at height nu + 1 - M, so
    # M = 1 is the top row and M = nu the bottom, stable, row.
    def ypos(M):
        return nu + 1 - M

    for M in range(1, nu + 1):
        y = ypos(M)
        ax.plot([0, D], [y, y], color=GREY, lw=0.5, zorder=1)
        # the open interval removed at this level, relative to the row above
        if M >= 2:
            ax.plot([M - 2, M - 1], [y, y], color=WINE, lw=2.8, alpha=0.22,
                    zorder=2)
        # the surviving continuous interval [M-1, D]
        ax.plot([M - 1, D], [y, y], color=BLUE, lw=2.8, zorder=3)
        for e in (M - 1, D):
            ax.plot(e, y, marker="o", ms=4.4, mfc=BLUE, mec=BLUE, zorder=4)
        # the isolated survivors {0,...,M-2}
        for p_ in range(0, M - 1):
            ax.plot(p_, y, marker="o", ms=4.4, mfc=BLUE, mec=BLUE, zorder=4)

    # the continuous left endpoint moves RIGHT by one at each level down
    for M in range(2, nu + 1):
        ax.annotate("", xy=(M - 1, ypos(M) + 0.17),
                    xytext=(M - 2, ypos(M - 1) - 0.17),
                    arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.1,
                                    mutation_scale=8, shrinkA=1.5,
                                    shrinkB=1.5),
                    zorder=6)
    ax.text(D + 0.14, ypos(1), "edge advances", fontsize=TICK, color=AMBER,
            ha="left", va="center")
    ax.text(D + 0.14, ypos(nu), r"stable from $N_*=6$", fontsize=TICK,
            color=GREY, ha="left", va="center")

    ax.set_yticks([ypos(M) for M in range(1, nu + 1)])
    ax.set_yticklabels([r"$M=%d,\ N=%d$" % (M, M * KP1)
                        for M in range(1, nu + 1)])
    _row_axis(ax, BASE)
    ax.set_xticks(list(range(0, D + 1)))
    ax.set_xticklabels([r"$%d$" % k for k in range(0, D + 1)])
    ax.set_xlabel(r"terminal coordinate $\sigma = kD - s$, with $0\le\sigma\le D$",
                  fontsize=LABEL, color=INK, labelpad=2)

    handles = [
        Line2D([], [], color=BLUE, lw=2.8, marker="o", ms=4.4, mfc=BLUE,
               mec=BLUE, label=r"retained at this level"),
        Line2D([], [], color=WINE, lw=2.8, alpha=0.22,
               label=r"removed at this level"),
    ]
    ax.legend(handles=handles, loc="upper center",
              bbox_to_anchor=(0.5, -0.185), ncol=2,
              fontsize=TICK, labelcolor=INK)

    es_save(fig, path, bbox_inches=None)
    plt.close(fig)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    figure_one(os.path.join(here, "fig1-cocycle-split.pdf"))
    figure_two(os.path.join(here, "fig2-divisor-cancellation.pdf"))
    figure_three(os.path.join(here, "fig3-positivity-loci.pdf"))
    figure_four(os.path.join(here, "fig4-erosion-staircase.pdf"))
    print("wrote fig1, fig2, fig3, fig4")
