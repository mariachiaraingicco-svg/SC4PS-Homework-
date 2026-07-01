import numpy as np
import mpmath as mp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

L_MAX = 50
X_VALUES = [0.1, 0.5, 0.9, 0.99]
mp.mp.dps = 100  # 100 decimal digits for the reference


def legendre_forward(x, L):
    P = np.zeros(L + 1, dtype=np.float64)
    P[0] = 1.0
    if L >= 1:
        P[1] = x
    for l in range(1, L):
        P[l + 1] = ((2 * l + 1) * x * P[l] - l * P[l - 1]) / (l + 1)
    return P


def legendre_reference(x, L):
    xx = mp.mpf(x)
    P = [mp.mpf(0)] * (L + 1)
    P[0] = mp.mpf(1)
    if L >= 1:
        P[1] = xx
    for l in range(1, L):
        P[l + 1] = ((2 * l + 1) * xx * P[l] - l * P[l - 1]) / (l + 1)
    return P


def legendre_backward(x, L):
    Pt = np.zeros(L + 2, dtype=np.float64)
    Pt[L + 1] = 0.0
    Pt[L] = 1.0
    for l in range(L, 0, -1):
        Pt[l - 1] = ((2 * l + 1) * x * Pt[l] - (l + 1) * Pt[l + 1]) / l
    c = 1.0 / Pt[0]
    return c * Pt[:L + 1]


def main():
    print(f"Legendre stability study, L_MAX={L_MAX}, mpmath dps={mp.mp.dps}")
    print("=" * 64)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.ravel()

    for ax, x in zip(axes, X_VALUES):
        ref = legendre_reference(x, L_MAX)
        fwd = legendre_forward(x, L_MAX)
        bwd = legendre_backward(x, L_MAX)

        ls = np.arange(L_MAX + 1)
        rel_fwd = np.zeros(L_MAX + 1)
        rel_bwd = np.zeros(L_MAX + 1)

        for l in ls:
            r = ref[l]
            denom = float(abs(r)) if float(abs(r)) > 0 else 1.0
            rel_fwd[l] = float(abs(mp.mpf(float(fwd[l])) - r)) / denom
            rel_bwd[l] = float(abs(mp.mpf(float(bwd[l])) - r)) / denom

        print(f"\nx = {x}")
        print(f"  P_50 forward   rel.err = {rel_fwd[L_MAX]:.3e}")
        print(f"  P_50 backward  rel.err = {rel_bwd[L_MAX]:.3e}")
        print(f"  max rel.err forward  over l: {rel_fwd.max():.3e}")
        print(f"  max rel.err backward over l: {rel_bwd.max():.3e}")

        ax.semilogy(ls, np.clip(rel_fwd, 1e-20, None), "o-", ms=3, label="forward (double)")
        ax.semilogy(ls, np.clip(rel_bwd, 1e-20, None), "s-", ms=3, label="backward (Miller-style)")
        ax.set_title(f"x = {x}")
        ax.set_xlabel(r"degree $\ell$")
        ax.set_ylabel("relative error")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle("Relative error of P_l(x) vs degree (forward vs backward recurrence)")
    fig.tight_layout()
    fig.savefig("legendre_relative_error.png", dpi=110)
    print("\nWrote legendre_relative_error.png")


if __name__ == "__main__":
    main()
