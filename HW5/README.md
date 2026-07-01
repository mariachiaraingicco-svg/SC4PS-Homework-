# Stability of Legendre Polynomials

For fixed order m = 0 and degrees up to ℓ_max = 50, compare numerical ways of computing the Legendre polynomials P_ℓ(x) (which are Y_ℓ0 up to normalization) at x = 0.1, 0.5, 0.9, 0.99, and check whether the expected stability claim actually holds.

---

## Methods

**1. Forward recurrence (double precision).** Bonnet's recurrence:

```
P_0(x) = 1,  P_1(x) = x
P_{ℓ+1}(x) = ((2ℓ+1) x P_ℓ(x) − ℓ P_{ℓ-1}(x)) / (ℓ+1),   ℓ ≥ 1
```

**2. High-precision reference.** The same Bonnet recurrence evaluated with `mpmath` at `mp.dps = 100` (100 decimal digits — not 100 bits, which would be only ~30 digits). These values are treated as exact for measuring double-precision error.

**3. Backward (Miller-style) recurrence.** The forward recurrence solved for the lower index:

```
P_{ℓ-1}(x) = ((2ℓ+1) x P_ℓ(x) − (ℓ+1) P_{ℓ+1}(x)) / ℓ,   ℓ = L, L-1, ..., 1
```

seeded with P~_{L+1} = 0, P~_L = 1, propagated downward, then rescaled by c = 1/P~_0 so that P_0 = 1:

```
P_ℓ^(back)(x) = c · P~_ℓ(x)
```

---

## Code

```python
import numpy as np
import mpmath as mp

L_MAX = 50
X_VALUES = [0.1, 0.5, 0.9, 0.99]
mp.mp.dps = 100  # 100 decimal digits for the reference

def legendre_forward(x, L):
    P = np.zeros(L + 1)
    P[0] = 1.0
    if L >= 1:
        P[1] = x
    for l in range(1, L):
        P[l + 1] = ((2*l + 1) * x * P[l] - l * P[l - 1]) / (l + 1)
    return P

def legendre_reference(x, L):
    xx = mp.mpf(x)
    P = [mp.mpf(0)] * (L + 1)
    P[0] = mp.mpf(1)
    if L >= 1:
        P[1] = xx
    for l in range(1, L):
        P[l + 1] = ((2*l + 1) * xx * P[l] - l * P[l - 1]) / (l + 1)
    return P

def legendre_backward(x, L):
    Pt = np.zeros(L + 2)
    Pt[L + 1] = 0.0
    Pt[L] = 1.0
    for l in range(L, 0, -1):
        Pt[l - 1] = ((2*l + 1) * x * Pt[l] - (l + 1) * Pt[l + 1]) / l
    c = 1.0 / Pt[0]
    return c * Pt[:L + 1]
```

(The full script, including error computation and plotting, is in `legendre_stability.py`.)

## Usage

```bash
pip install numpy mpmath matplotlib
python3 legendre_stability.py
```

It prints the errors per x and writes `legendre_relative_error.png`.

---

## Results (real output, ℓ = 50)

| x    | forward rel.err (ℓ=50) | max forward rel.err | backward rel.err (ℓ=50) | max backward rel.err |
|------|------------------------|---------------------|-------------------------|----------------------|
| 0.1  | 7.5e-16                | 6.9e-15             | 6.8e+00                 | 1.7e+02              |
| 0.5  | 3.9e-16                | 7.7e-16             | 4.2e+01                 | 4.8e+01              |
| 0.9  | 4.7e-16                | 5.6e-15             | 6.6e-01                 | 8.1e+00              |
| 0.99 | 8.8e-16                | 1.1e-14             | 9.2e-01                 | 8.4e+00              |

The relative-error-vs-degree plot (`legendre_relative_error.png`) shows the forward recurrence pinned at machine precision (~1e-16) across all ℓ, while the backward Miller-style result jumps to order-unity-or-larger error immediately.

---

## Explanation of the numerical behavior

A three-term recurrence has **two** independent solutions. For Bonnet's recurrence these are the Legendre function of the first kind P_ℓ(x) and of the second kind Q_ℓ(x). Whether a given direction of propagation is stable depends on which solution grows and which decays in that direction.

**Miller's algorithm** (backward recurrence from an arbitrary seed, then rescale) works only when the desired solution is the **minimal** (most strongly decaying) solution in the direction of propagation: any contamination from the dominant solution decays away as you iterate, so the seed is "forgotten" and the rescaling recovers the wanted function. This is the case, for example, for Bessel functions J_n.

For the **ordinary Legendre polynomials on |x| < 1**, P_ℓ(x) and Q_ℓ(x) do **not** exhibit a clean dominant/minimal exponential separation — on the real interval they are both oscillatory and comparable in magnitude. Consequently:

- The **forward** recurrence is stable for the tested values: P_ℓ is not a violently subdominant solution, so forward propagation does not amplify rounding catastrophically. The measured forward error stays at machine-precision level for all four x and up to ℓ = 50, confirming the expected stability.
- The **backward** Miller-style procedure does **not** select P_ℓ: with no minimal solution to lock onto, the arbitrary seed (P~_{L+1}=0, P~_L=1) injects an arbitrary mixture of P_ℓ and Q_ℓ that the rescaling cannot purify, so it generally fails to reproduce P_ℓ. The measured backward error is order unity or larger, exactly as the homework anticipated.

So the "expected stability claim" is verified: forward is stable here, and the arbitrary backward recurrence is not a valid way to compute P_ℓ on |x| < 1.

---

## Connection to spherical harmonics

The zonal spherical harmonics are

```
Y_ℓ0(θ, φ) = sqrt((2ℓ+1)/(4π)) · P_ℓ(cos θ)
```

so an error in P_ℓ(cos θ) propagates directly into Y_ℓ0 up to the known (exact) normalization factor sqrt((2ℓ+1)/(4π)). Since the forward recurrence keeps the relative error of P_ℓ at machine precision for x = cos θ in the tested range, Y_ℓ0 inherits the same accuracy; the backward route, by contrast, would corrupt Y_ℓ0 just as badly as it corrupts P_ℓ.

## Conclusion

For x = 0.1, 0.5, 0.9, 0.99 and ℓ_max = 50:
- the standard **forward** recurrence stays at machine precision relative to the high-precision reference — it is stable for the tested cases;
- the arbitrary **Miller-style backward** procedure does not generally compute P_ℓ(x) for |x| < 1;
- Miller's algorithm is useful only where the desired solution is genuinely minimal in the backward direction, which is not the case for ordinary Legendre polynomials on the real interval.
