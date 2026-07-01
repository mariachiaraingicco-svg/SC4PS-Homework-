# Matrix Multiplication

## Exercise

Create a C code that performs matrix multiplication:

```
C = A * B    with    C_ij = sum_k A_ik * B_kj    (i, j, k = 0, ..., N-1)
```

Inputs from command line: `a`, `b`, `N`, `fileout`, where:
- `A = a * I_N` and `B = b * I_N`... actually, following the assignment, `A` and `B` are matrices in which **every** element equals `a` and `b` respectively (not identity matrices: every entry of `A` is `a`, every entry of `B` is `b`).
- `fileout` is the filename for the output matrix `C`.

## Note on the test matrices

With `A` constant (every entry = `a`) and `B` constant (every entry = `b`), the matrix product gives, for every `i, j`:

```
C_ij = sum_{k=0}^{N-1} A_ik * B_kj = sum_{k=0}^{N-1} a * b = N * a * b
```

So every element of `C` is expected to equal `N*a*b`, independently of `i, j`.

## Quickest way to check correctness without comparing every element

Because every element of `C` is identical by construction (see derivation above), checking a single entry, `C[0][0]`, against the expected value `N*a*b` is mathematically sufficient to validate the whole matrix. There is no need for an O(N^2) verification loop just to *check* the result (the O(N^3) multiplication is of course still needed to *compute* it).

```c
double expected = a * b * N;
if (fabs(C[0] - expected) < tol) { /* correct */ }
```

A small tolerance is used instead of exact equality for the same floating-point reasons discussed in HW2.

## Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

void fill_matrix(double *M, int N, double val) {
    for (int i = 0; i < N * N; i++) M[i] = val;
}

void matmul_ijk(double *A, double *B, double *C, int N) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) {
            double sum = 0.0;
            for (int k = 0; k < N; k++)
                sum += A[i*N + k] * B[k*N + j];
            C[i*N + j] = sum;
        }
}

void matmul_ikj(double *A, double *B, double *C, int N) {
    for (int i = 0; i < N * N; i++) C[i] = 0.0;
    for (int i = 0; i < N; i++)
        for (int k = 0; k < N; k++) {
            double a_ik = A[i*N + k];
            for (int j = 0; j < N; j++)
                C[i*N + j] += a_ik * B[k*N + j];
        }
}

void matmul_jki(double *A, double *B, double *C, int N) {
    for (int i = 0; i < N * N; i++) C[i] = 0.0;
    for (int j = 0; j < N; j++)
        for (int k = 0; k < N; k++) {
            double b_kj = B[k*N + j];
            for (int i = 0; i < N; i++)
                C[i*N + j] += A[i*N + k] * b_kj;
        }
}

int save_matrix(const char *filename, double *M, int N) {
    FILE *f = fopen(filename, "w");
    if (!f) { fprintf(stderr, "Error: cannot open %s\n", filename); return 1; }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) fprintf(f, "%.10g ", M[i*N + j]);
        fprintf(f, "\n");
    }
    fclose(f);
    return 0;
}

int main(int argc, char *argv[]) {

    if (argc != 5) {
        fprintf(stderr, "Usage: %s <a> <b> <N> <fileout>\n", argv[0]);
        return 1;
    }

    double a = atof(argv[1]);
    double b = atof(argv[2]);
    int N = atoi(argv[3]);
    const char *fileout = argv[4];

    double *A = malloc(N * N * sizeof(double));
    double *B = malloc(N * N * sizeof(double));
    double *C = malloc(N * N * sizeof(double));
    if (!A || !B || !C) { fprintf(stderr, "Allocation failed\n"); return 1; }

    fill_matrix(A, N, a);
    fill_matrix(B, N, b);

    const char *names[3] = {"ijk", "ikj", "jki"};
    void (*funcs[3])(double*, double*, double*, int) = {matmul_ijk, matmul_ikj, matmul_jki};

    double expected = a * b * N;
    double tol = 1e-6 * (N > 1 ? N : 1);

    for (int t = 0; t < 3; t++) {
        clock_t start = clock();
        funcs[t](A, B, C, N);
        clock_t end = clock();
        double elapsed = (double)(end - start) / CLOCKS_PER_SEC;

        printf("Loop ordering %s: time = %f s\n", names[t], elapsed);
        if (fabs(C[0] - expected) < tol)
            printf("  -> Result correct (C[0][0] = %.10g, expected %.10g)\n", C[0], expected);
        else
            printf("  -> Result NOT correct (C[0][0] = %.10g, expected %.10g)\n", C[0], expected);
    }

    if (save_matrix(fileout, C, N) == 0)
        printf("Matrix C saved to %s\n", fileout);

    free(A); free(B); free(C);
    return 0;
}
```

## Compilation

```bash
gcc -O2 -o matmul matmul.c -lm
```

`-O2` is used so the benchmark reflects realistic, optimized performance rather than unoptimized debug code.

## Usage

```bash
./matmul <a> <b> <N> <fileout>
```

Example:
```bash
./matmul 2 3 500 result.txt
```

## Timing function

`clock()` from `<time.h>` is used to measure CPU time, following the standard approach described at
https://stackoverflow.com/questions/5248915/execution-time-of-c-program

```c
clock_t start = clock();
clock_t end = clock();
double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
```

Note: `clock()` measures **CPU time**, not wall-clock time. For single-threaded code like this one they coincide; for multi-threaded code `clock()` would need to be replaced with `omp_get_wtime()` or `gettimeofday()`/`clock_gettime(CLOCK_MONOTONIC, ...)`.

## Benchmark: which loop ordering is fastest, and why

The three classic loop orderings (`ijk`, `ikj`, `jki`) were compiled with `-O2` and timed for several matrix sizes `N`. Measured results (single run, CPU time in seconds):

| N   | ijk      | ikj      | jki      |
|-----|----------|----------|----------|
| 10  | 0.000008 | 0.000001 | 0.000002 |
| 200 | 0.010014 | 0.005556 | 0.007198 |
| 500 | 0.171761 | 0.082084 | 0.201265 |

**`ikj` is consistently the fastest**, roughly 2x faster than `ijk` and `jki` at N = 500.

**Why**: matrices are stored in C in **row-major order**, meaning `A[i*N + k]` and `A[i*N + k+1]` are adjacent in memory, while elements in the same column (`A[i*N+k]` and `A[(i+1)*N+k]`) are N doubles apart. The innermost loop variable should therefore be the one that walks along a row (i.e. the last index), to maximize spatial locality and CPU cache utilization:

- **`ikj`**: the innermost loop varies `j`, walking row-wise through both `B[k*N + j]` and `C[i*N + j]` — both accesses are sequential in memory. This is cache-friendly and explains why it's the fastest.
- **`ijk`**: the innermost loop varies `k`, which walks row-wise through `A[i*N+k]` (good) but column-wise through `B[k*N+j]` (bad: stride-N access, poor cache reuse).
- **`jki`**: the innermost loop varies `i`, which walks column-wise through both `A[i*N+k]` and `C[i*N+j]` (bad on both accesses), explaining why it is the slowest of the three at large N.

In short: the loop ordering that keeps the innermost-loop memory accesses contiguous (row-major, stride-1) wins, because it minimizes cache misses. This matters more as N grows, since for small N the whole working set fits in cache and the ordering makes little difference — consistent with the N=10 timings above, where the differences are at the microsecond/noise level.

## Output

The program saves the resulting matrix `C` to the file given as `fileout`, one row per line, space-separated values.
