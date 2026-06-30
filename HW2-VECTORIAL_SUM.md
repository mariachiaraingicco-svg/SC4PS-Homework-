# Homework 02 - Vector Summation: d = a*x + y

## Exercise

Implement the vector operation:

```
d = a*x + y
```

where:
- `a` is a scalar
- `x`, `y`, `d` are vectors of dimension N
- All elements of `x` have the same value
- All elements of `y` have the same value
- `a`, `x`, `y` are passed from the command line
- N is tested for N = 10, N = 10^6, N = 10^8

---

## Implementation

The program:
- reads `a`, `x`, `y` as command-line arguments (`argv`)
- allocates memory dynamically for the vectors, for each value of N in turn
- initializes vectors `x` and `y` (constant value across all elements)
- computes the result vector `d = a*x + y`
- tests that all elements of `d` equal the expected value, using a tolerance instead of exact equality (see "Floating-Point Precision" below)

Command-line input was chosen instead of interactive `scanf` input because it makes the program scriptable: it can be called from a shell script or a benchmark loop without manual typing, and the same run is exactly reproducible.

---

## Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main(int argc, char *argv[]) {

    if (argc != 4) {
        fprintf(stderr, "Usage: %s <a> <x> <y>\n", argv[0]);
        return 1;
    }

    double a = atof(argv[1]);
    double x = atof(argv[2]);
    double y = atof(argv[3]);

    long N[] = {10, 1000000, 100000000};
    int num_tests = 3;

    double expected = a * x + y;

    printf("Vector sum d = a*x + y, with a = %g, x = %g, y = %g\n", a, x, y);
    printf("Expected value of each element of d: %.17g\n", expected);

    for (int i = 0; i < num_tests; i++) {

        long n = N[i];
        printf("\n=== Testing with N = %ld ===\n", n);

        double *x_vec = malloc(n * sizeof(double));
        double *y_vec = malloc(n * sizeof(double));
        double *d_vec = malloc(n * sizeof(double));

        if (!x_vec || !y_vec || !d_vec) {
            fprintf(stderr, "Memory allocation failed for N = %ld\n", n);
            free(x_vec); free(y_vec); free(d_vec);
            continue;
        }

        for (long j = 0; j < n; j++) {
            x_vec[j] = x;
            y_vec[j] = y;
        }

        for (long j = 0; j < n; j++) {
            d_vec[j] = a * x_vec[j] + y_vec[j];
        }

        printf("First 5 elements of d: ");
        for (long j = 0; j < (n < 5 ? n : 5); j++) {
            printf("%.17g ", d_vec[j]);
        }
        printf("\n");

        /* quickest way to check all elements: since x, y, a are constant,
           every d_vec[j] is identical, so it is enough to verify the
           first element instead of looping over all N of them */
        double tol = 1e-10;
        if (fabs(d_vec[0] - expected) < tol) {
            printf("Result correct (within tolerance %.0e)\n", tol);
        } else {
            printf("Error: result NOT correct (got %.17g, expected %.17g)\n",
                   d_vec[0], expected);
        }

        free(x_vec);
        free(y_vec);
        free(d_vec);
    }

    return 0;
}
```

## Compilation
```bash
gcc -O2 -o vector_sum vector_sum.c -lm
```

## Usage
```bash
./vector_sum <a> <x> <y>
```

Example:
```bash
./vector_sum 3 0.1 7.1
```

## Check 
Since `a`, `x`, and `y` are scalars (every element of `x` and `y` is identical), every element of `d` is computed in exactly the same way and is therefore identical too. So checking `d[0]` alone is mathematically sufficient to validate the whole vector

## Floating-Point Precision

Test case:
- a = 3
- x = 0.1
- y = 7.1

Expected mathematical result:
```
7.40000000000000000
```
Actual result:
```
7.39999999999999947
```

This happens because decimal numbers like 0.1 and 7.1 cannot be represented exactly in binary floating-point format (IEEE 754 double precision). The rounding error introduced when storing 0.1 and 7.1 in binary propagates through the multiplication and addition. Comparing with `==` therefore fails even though the result is correct to ~16 significant digits.

We solve this by using a tolerance instead of exact comparison:
```c
fabs(d[i] - expected) < 1e-10
```

## Large N values (N = 10^8)

For N = 10^8, the program needs about 2.4 GB of RAM (3 arrays x 10^8 elements x 8 bytes each).

- **Problem observed**: declaring arrays of this size as fixed-size local (stack) arrays causes a stack overflow **→ Solution**: used dynamic memory allocation with `malloc()`, which allocates from the heap and can handle multi-gigabyte sizes (as long as enough RAM is available on the machine).
- For very large N on memory-constrained machines, allocation can still fail; the code checks the return value of `malloc()` for this reason.
