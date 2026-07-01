This repository collects the solutions to the seven SC4PS homework assignments. Each folder contains its own `README.md` with the write-up, the source code, and any figures. Moreover, each folder's `README.md` gives the exact build and run commands.

| HW | Topic | Language | Contents |
|----|-------|----------|----------|
| [HW01](HW01/) | Linux VM setup on CloudVeneto for compiling/running C | — | setup guide |
| [HW02](HW02/) | Vector sum `d = a*x + y`; floating-point precision | C | `vector_sum.c` |
| [HW03](HW03/) | Matrix multiplication; loop-ordering cache benchmark | C | `matmul.c`, benchmark plot |
| [HW04](HW04/) | Discrete/Fast Fourier Transform: sampling, aliasing, resolution, coupled oscillators | C | worksheet answers, spectra plots, bug fix |
| [HW05](HW05/) | Numerical stability of Legendre-polynomial recurrences | Python | `legendre_stability.py`, error plot |
| [HW06](HW06/) | Chunked daxpy with partial sums, config-file input, HDF5 output | C | `daxpy_chunks.c`, `input.conf` |
| [HW07](HW07/) | Random numbers and Monte Carlo (LLN, π, sampling, ECDF) | Python | `montecarlo.py`, figure |

## Notes (building and running)

- **C homeworks** (HW02, HW03, HW06) compile with `gcc`. HW06 additionally needs
  the HDF5 C library and the header-only config parser
  [welljsjs/Config-Parser-C](https://github.com/welljsjs/Config-Parser-C)
  (AGPL-3.0, cloned separately — see `HW06/README.md`).
- **Python homeworks** (HW05, HW07) need `numpy`, `mpmath` (HW05) and
  `matplotlib`. Run with `python3 <script>.py`.
- **HW04** is based on the external project
  [alexninogh/myfft_tutorial](https://github.com/alexninogh/myfft_tutorial)
  (build with GNU GSL; plots via `make plot-python`).
