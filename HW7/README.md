# Random numbers and Monte Carlo

Five exercises on random-number generation, the law of large numbers, Monte Carlo integration, change of variables, inverse-transform sampling, and the empirical CDF.

**Language**: Python (numpy + matplotlib), since the assignment refers to a notebook and the exercises are about sampling and histograms. The script `montecarlo.py` is written with `# %%` cell markers, so in VS Code it opens directly as an interactive notebook (or runs as a plain script: `python3 montecarlo.py`).

Reproducibility: a single master seed (`np.random.SeedSequence`) feeds independent child streams, so results are reproducible and the two streams used for the π estimate are genuinely independent.

---

## 1. Coin tosses and the Law of Large Numbers

100,000 fair tosses (0/1). The running fraction of heads after n tosses is the cumulative mean. Real output:

```
after      10 tosses: 0.80000
after     100 tosses: 0.55000
after    1000 tosses: 0.51100
after   10000 tosses: 0.50290
after  100000 tosses: 0.49746
|fraction - 0.5| at the end = 2.54e-03
```

**Comment.** The running fraction converges to 0.5, but not monotonically: early on (n = 10) it can be far off (0.80), and it settles down as n grows. The size of the fluctuations around 0.5 shrinks like 1/√n — this is the law of large numbers made visible: the sample mean of i.i.d. Bernoulli(½) variables converges to the expected value ½, with standard deviation of the running mean ≈ 0.5/√n. The plot (semilog-x) shows the large early swings damping into a tight band around 0.5.

---

## 2. Monte Carlo estimate of π

Draw points (x, y) uniformly in the unit square using **two independent RNG streams**; the fraction landing inside the quarter circle x²+y² ≤ 1 estimates π/4, so π ≈ 4·(inside fraction). RMS error over 30 trials per N:

```
N=      100: pi~3.20000  RMS error = 1.716e-01
N=     1000: pi~3.11200  RMS error = 4.908e-02
N=    10000: pi~3.16000  RMS error = 1.474e-02
N=   100000: pi~3.14792  RMS error = 4.278e-03
N=  1000000: pi~3.13951  RMS error = 1.543e-03
N= 10000000: pi~3.14179  RMS error = 4.874e-04
```

**Study of the error.** Each tenfold increase in N reduces the error by a factor ≈ √10 ≈ 3.16 (e.g. 1.72e-1 → 4.91e-2 → 1.47e-2 → ...), i.e. the error scales as **1/√N**. This is the universal Monte Carlo convergence rate: the estimator is a sample mean, whose standard deviation falls like σ/√N regardless of dimension. The log-log plot of RMS error vs N lies parallel to the 1/√N reference line. Note the practical cost: getting one extra correct digit (10× smaller error) requires 100× more samples.

---

## 3. Change of variables: Y = U²

With U ~ Uniform(0,1) and Y = U², the density of Y is

```
F_Y(y) = P(U² ≤ y) = P(U ≤ √y) = √y      (0 < y < 1)
f_Y(y) = dF_Y/dy = 1/(2√y)
```

The histogram of 200,000 transformed samples matches the analytic density f_Y(y) = 1/(2√y) over (0,1), including the integrable singularity at y → 0 (the density diverges there because squaring compresses many U values near 0 into a tiny Y range). The plot overlays histogram and curve; they agree.

---

## 4. Inverse-transform exponential

The inverse-transform method: if U ~ Uniform(0,1), then Y = −ln(1−U)/λ is Exponential(λ). Here λ = 1.5, 200,000 samples.

Derivation: the exponential CDF is F(y) = 1 − e^{−λy}; inverting F(Y) = U gives Y = −ln(1−U)/λ. (Since 1−U is also Uniform(0,1), −ln(U)/λ would work equally well.)

Real output: sample mean = 0.6669, vs the theoretical mean 1/λ = 0.6667 — agreement to 4 significant figures. The histogram matches the PDF f(y) = λe^{−λy}.

---

## 5. Empirical CDF

For the exponential sample of Exercise 4, the empirical CDF is the step function

```
F_n(y) = (number of samples ≤ y) / n
```

obtained by sorting the sample and plotting sorted values against k/n. It is compared to the exact CDF F(y) = 1 − e^{−λy}.

Real output: max |ECDF − exact CDF| = **1.51e-03**. The two curves are visually indistinguishable; the maximum gap (a Kolmogorov-type statistic) is of order 1/√n, consistent with the Glivenko–Cantelli theorem (the empirical CDF converges uniformly to the true CDF as n → ∞).

---

## Files

- `montecarlo.py` — all five exercises (VS Code `# %%` cells or plain script)
- `hw7_montecarlo.png` — the six-panel figure (LLN, MC-π error, π estimate, Y=U², exponential, ECDF)

## Usage

```bash
pip install numpy matplotlib
python3 montecarlo.py
```
