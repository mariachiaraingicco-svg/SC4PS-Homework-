# Homework 02 - Vector Summation

## Exercise

Implement the vector operation:

d = a x + y

where:
- `a` is a scalar
- `x`, `y`, `d` are vectors of dimension N
- All elements of `x` have the same value
- All elements of `y` have the same value

---

## Implementation

The program:
- reads input values for `a`, `x`, and `y`
- allocates memory dynamically for vectors
- initializes vectors `x` and `y`
- computes the result vector `d`
- prints a subset of results for verification

---

## Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main() {

    int N[] = {10, 1000000, 100000000};
    int num_tests = 3;

    double a, x, y;

    printf("In the vector sum d = ax + y\n");

    printf("- enter the value of a: ");
    scanf("%lf", &a);

    printf("- enter the value of x: ");
    scanf("%lf", &x);

    printf("- enter the value of y: ");
    scanf("%lf", &y);

    for(int i = 0; i < num_tests; i++) {

        int n = N[i];
        printf("\n=== Testing with N = %d ===\n", n);

        double *x_vec = malloc(n * sizeof(double));
        double *y_vec = malloc(n * sizeof(double));
        double *d_vec = malloc(n * sizeof(double));

        for(int j = 0; j < n; j++) {
            x_vec[j] = x;
            y_vec[j] = y;
        }

        for(int j = 0; j < n; j++) {
            d_vec[j] = a * x_vec[j] + y_vec[j];
        }

        printf("The first 5 elements of d are: ");
        for(int j = 0; j < (n < 5 ? n : 5); j++) {
            printf("%.17lf\n", d_vec[j]);
        }
        printf("\n");

        //expected value
        double expected = a * x + y;
        int all_correct = 1;

        for(int j = 0; j < n; j++) {
            if (d_vec[j] != expected) {
                all_correct = 0;
                break;
            }    
        }

        if (all_correct) {
            printf("All elements are correct\n");
        } else {
            printf("Error: some elements are NOT correct\n");
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
gcc -o vector_sum vector_sum.c -lm
```

## Usage
Run the program and enter the requested values:
```bash
./vector_sum
```
## Tests performed 
- N = 10
- N = 1000000
- N = 10000000

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
This happens because decimal numbers cannot be represented exactly in binary floating-point format. This demonstrates the importance of using tolerance-based comparisons for floating-point equality checks.

## Large N values (N = 10^8)
For N = 10^8, the program needs about 2.4 GB of RAM (3 arrays × 10^8 elements × 8 bytes)
- **Solution**: Used dynamic memory allocation with `malloc()`
- Static arrays would cause stack overflow
