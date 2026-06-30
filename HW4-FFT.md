# Homework 4 -- Fourier Transform - Guided Worksheet Answers

Reference project: https://github.com/alexninogh/myfft_tutorial

---

## Part 1: Before running

**1. What an FFT tells you about a signal.** It estimates how strongly each frequency is present in a sampled signal: it decomposes a time series x(t), known at N discrete sample points, into the sinusoidal components (amplitude per frequency) that make it up.

**2. Sampling rate vs Nyquist vs frequency resolution.**
- Sampling rate f_s: samples per second; sets the time step Δt = 1/f_s.
- Nyquist frequency f_N = f_s/2: the highest frequency representable without aliasing. A property of *how fast you sample*.
- Frequency resolution Δf = 1/T = f_s/N: the spacing between FFT bins, i.e. the smallest frequency separation you can resolve. A property of *how long you record* (T = N·Δt).

**3. Why the time grid must be uniform.** The radix-2 FFT used here (`gsl_fft_complex_radix2_forward`) is defined on equally spaced samples: each sample is multiplied by exp(-i2πkn/N) on a fixed step. A non-uniform grid breaks this, and the bin frequencies no longer correspond to the data. (Non-uniform data need other tools, e.g. Lomb-Scargle.) The project header `fft_utils.h` states this assumption explicitly.

---

## Part 2: Build and run

**1. CSV files created in `output/`** (8 files):
- `good_sampling_signal.csv`, `good_sampling_spectrum.csv`
- `undersampled_signal.csv`, `undersampled_spectrum.csv`
- `short_record_signal.csv`, `short_record_spectrum.csv`
- `coupled_oscillators_time.csv`, `coupled_oscillators_spectrum.csv`

**2. Program that studies pure sampling issues:** `src/sampling_demo.c`.

**3. Program that studies a mechanics problem:** `src/coupled_oscillators_fft.c`.

**4. Two frequencies in the well-sampled case:** **50 Hz and 120 Hz** (the signal is `sin(2π·50·t) + 0.70·sin(2π·120·t)`). Real run: peaks at 50.000 Hz (amplitude 1.0000) and 120.000 Hz (amplitude 0.7000), both recovered correctly since f_s = 512 Hz puts Nyquist at 256 Hz.

---

## Part 3: Sampling and aliasing

Focus on `src/sampling_demo.c`, undersampled case (f_s = 128 Hz, N = 128, same 50+120 Hz signal).

1. Given: f_s = 128 Hz.
2. Nyquist: f_N = f_s/2 = **64 Hz**.
3. The 120 Hz component cannot be reconstructed because 120 Hz > 64 Hz: it lies above Nyquist and folds back to a false lower frequency.
4. Aliased peak near 8 Hz.
5. **Explanation.** A sampled sinusoid is only observed at discrete instants, so frequencies differing by an integer multiple of f_s produce identical samples: exp(i2πf₀nΔt) = exp(i2π(f₀+m·f_s)nΔt) when Δt = 1/f_s. Here the 120 Hz tone aliases to

   f_alias = |120 − 128| = **8 Hz**.

   Real run confirms it: the undersampled spectrum shows peaks at 50.000 Hz (amp 1.0) and 8.000 Hz (amp 0.7) — the 120 Hz energy has moved to 8 Hz exactly as predicted, while the well-sampled 50 Hz stays put.

---

## Part 4: Frequency resolution

Focus on the `short_record` case: signal `sin(2π·50·t) + 0.85·sin(2π·55·t)`, with **N = 64, f_s = 512 Hz**.

1. Given: 50 Hz and 55 Hz.
2. Record length: T = N/f_s = 64/512 = **0.125 s**.
3. Frequency spacing: Δf = 1/T = f_s/N = 512/64 = **8 Hz**.
4. **Why they are hard to separate.** The two tones differ by only 5 Hz, which is *smaller* than the 8 Hz bin spacing. Two frequencies can be resolved only if their separation exceeds roughly Δf = 1/T, so an 8 Hz grid cannot tell 50 Hz and 55 Hz apart — even though both sit well below Nyquist (256 Hz) and are individually well sampled.

   Real run confirms this concretely. The bins fall at 40, 48, 56, 64 Hz; the energy of the 50+55 Hz pair spreads across the two neighbouring bins instead of forming two clean lines:

   ```
    40.0 Hz  amp 0.1728
    48.0 Hz  amp 0.8651   <- reported dominant peak (neither 50 nor 55 Hz!)
    56.0 Hz  amp 0.7578
    64.0 Hz  amp 0.1211
   ```

   The program reports a single dominant peak at 48 Hz — not 50, not 55 — which is exactly the signature of unresolved, leaking frequencies.
5. **What to change to improve separation:** increase the **total acquisition time T** (more samples, same Δt). Since Δf = 1/T, a longer record shrinks the bin spacing and separates the peaks. Changing the plotting tool or the file format does nothing to the underlying resolution.

---

## Part 5: Coupled oscillators

Focus on `src/coupled_oscillators_fft.c`. Parameters in the code: m = 1.0 kg, wall spring k = 25.0 N/m, coupling spring k_c = 7.0 N/m. Initial condition: x1(0) = 0.10, x2(0) = 0, both velocities 0.

**1. Equations of motion.** Two equal masses, each tied to a wall by spring k and coupled to each other by spring k_c:

```
m·x1'' = -k·x1 - k_c·(x1 - x2)
m·x2'' = -k·x2 - k_c·(x2 - x1)
```

Expanding the coupling term, this is identical to the form written in the code:

```
m·x1'' = -(k + k_c)·x1 + k_c·x2
m·x2'' =  k_c·x1 - (k + k_c)·x2
```

(The two forms are the same equations; the first makes the physics explicit, the second is the expanded version used in `rhs()`.)

**2. Physical system:** two identical masses attached to walls and coupled by a spring — the standard two coupled harmonic oscillators (a model also used for coupled pendula, molecular vibrations, coupled LC circuits).

**3. Normal modes:**
- **In-phase** (x1 = x2): the coupling spring is never stretched, each mass feels only its wall spring → f_in = (1/2π)·√(k/m) = (1/2π)·√25 = **0.79577 Hz**.
- **Out-of-phase** (x1 = −x2): the coupling spring adds restoring force → f_out = (1/2π)·√((k+2k_c)/m) = (1/2π)·√39 = **0.99392 Hz**.

**4. Why the FFT of x1(t) shows more than one frequency.** The initial condition (x1 displaced, x2 at rest) is not a pure normal mode, so it excites *both* modes. x1(t) is then a superposition of cos(2π f_in t) and cos(2π f_out t), and its FFT necessarily shows two peaks.

**5. Why compare numerical peaks with theory.** It validates the whole pipeline (ODE solver + sampling + FFT) against a known analytic result, building confidence to trust it on problems with no closed-form answer, and helping catch modeling or coding mistakes.

---

## Part 6: Plot inspection

1. Aliasing is clearest in the **undersampled** sampling-demo spectrum (the 120 Hz tone appears at 8 Hz).
2. Limited frequency resolution is clearest in the **short_record** spectrum (50 and 55 Hz merged into the 48/56 Hz bins).
3. Do the coupled-oscillator peaks line up with theory? **Yes, closely.** Real run:

   ```
   in-phase mode:     expected 0.79577 Hz, measured 0.79688 Hz, amplitude 0.0486
   out-of-phase mode: expected 0.99392 Hz, measured 0.99219 Hz, amplitude 0.0462
   ```

4. **Why the small differences.** The FFT bin spacing here is Δf = 1/(1024·0.125) ≈ 0.0078 Hz, and the true mode frequencies do not land exactly on a bin, so the measured peak sits at the nearest bin (off by ≤ one bin, ~0.001 Hz — consistent with the numbers above). Additional small contributions: spectral leakage from non-bin-aligned frequencies and the ODE solver's finite tolerance. The initial amplitude of each mode in x1 is 0.05 (the 0.10 displacement split between the two modes); the measured ~0.047-0.049 is slightly below 0.05 because of that leakage.

---

## Part 7: Small code modification (worked example: Option A)

**Option A — change the sampling rate of the undersampled case.** Suppose we change its f_s from 128 Hz to 200 Hz (keeping N = 128), still sampling the 50+120 Hz signal.

- **Predictions (before rerunning):** new Nyquist = 100 Hz. The 50 Hz tone is below Nyquist → stays at 50 Hz. The 120 Hz tone is above Nyquist → aliases to f_alias = |120 − 200| = 80 Hz (fold about Nyquist). So predicted peaks: **50 Hz and 80 Hz**, no longer 8 Hz.
- **After rerunning:** edit the `sample_rate_hz` field of the undersampled case in `main()`, rebuild, and compare the reported peaks to the predicted 50 and 80 Hz.

(If you prefer Option B, predict that increasing N at fixed Δt lengthens T and shrinks Δf = 1/T, so the 50/55 Hz peaks separate. For Option C, predict the mode shifts from f_in = √(k/m)/2π and f_out = √((k+2k_c)/m)/2π — but see the bug note below, which is directly relevant to Option C.)

---

## Are there any errors? (assignment's explicit question)

Having read and run the code, the headline answer is: **the project is functionally correct** — it builds with zero warnings under `-Wall -Wextra -Wpedantic`, and every numerical result matches the theory and the worksheet's expected values. That said, scrutiny does turn up one genuine latent bug and a couple of minor issues worth opening as GitHub issues:

**1. Latent out-of-bounds read in `report_mode_near_frequency()` (coupled_oscillators_fft.c).** The target bin is computed as

```c
best_bin = (size_t)llround(target_frequency_hz / (frequencies[1] - frequencies[0]));
```

and is then used directly to index `amplitudes[best_bin]` / `frequencies[best_bin]` without checking it stays inside the spectrum (`bins = N/2 + 1`). With the default parameters this is fine, but **it is reachable through Part 7 Option C**: if a student raises the spring constant enough that a normal-mode frequency reaches Nyquist (here f_N = 1/(2·0.125) = 4 Hz; e.g. k ≈ 1000 gives f_out ≈ 5.07 Hz), then best_bin ≈ 649 while there are only 513 bins → out-of-bounds access and undefined behaviour. This was verified directly.

*Fix* (clamp into the valid range):
```c
best_bin = (size_t)llround(target_frequency_hz / (frequencies[1] - frequencies[0]));
if (best_bin >= bins) {
    best_bin = bins - 1U;   /* target at/above Nyquist: stay inside the spectrum */
}
```
Verified: with the clamp the project still builds and the default output is unchanged.

**2. No window function before the FFT (minor / by design).** The signals are transformed without a window (e.g. Hann). For frequencies that do not land on a bin (the short_record 50/55 Hz case), this produces spectral leakage — which is *useful* pedagogically here, but worth noting as the reason the reported peak appears at 48 Hz rather than at 50 or 55 Hz.

**3. Cosmetic: `-lm` is passed twice at link time** (`$(GSL_LIBS)` from `gsl-config --libs` already includes `-lm`, and the Makefile adds another `-lm`). Harmless, but redundant.

---

## Part 8: Reflection

*(personalize — example)*

One thing I learned about FFTs is how sharply the time/frequency-resolution trade-off bites in practice: a perfectly sampled but short record (the 50/55 Hz case) simply cannot separate close frequencies, and no amount of post-processing fixes it — only acquiring more time does.

One thing I learned about scientific software organization is the value of factoring the shared numerical core (`fft_utils.c`) out of the application programs and driving everything through one reproducible `make run` / `make plot` pipeline, so a new experiment can be added without touching validated code.

One thing I would improve is adding bounds-safety to the peak-search routine (the bug above) and an optional windowing flag, so the same code can be used safely when parameters are pushed outside the tutorial's default range.

---

## Optional extension (example: damped oscillator)

- **Model:** m·x'' + γ·x' + k·x = 0 (single damped harmonic oscillator).
- **Parameters:** m = 1, k matched to wall_k for comparability, small γ (underdamped, γ ≪ 2√(km)).
- **Expected spectral signature:** instead of a sharp line at f₀ = (1/2π)√(k/m), a broadened (Lorentzian-like) peak with width ∝ γ/(2πm), and the peak slightly shifted to f = (1/2π)·√(k/m − (γ/2m)²).
- **Check:** run and compare the measured peak width/shift against those formulas.
