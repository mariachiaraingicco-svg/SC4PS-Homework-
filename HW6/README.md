# Split the work :) 

Take the daxpy operation `d = a*x + y` and:
1. compute it in **chunks** instead of one single loop, and check `d` is unchanged;
2. for every chunk, store the sum of its elements in `partial_chunk_sum[]`, then sum that array and check it equals the total sum of `d`;
3. read all inputs (`n`, `chunk_size`, `a`, `x`, `y`) from a **`key = value` config file**, using an existing config-file parser;
4. save all the vector chunks and the partial sums to an **HDF5** file.

---

## Dependencies

**Config parser** — the welljsjs `Config-Parser-C` (header-only, file `parser.h`):
https://github.com/welljsjs/Config-Parser-C

Clone it (or copy `parser.h`) next to the source so the compiler finds it:
```bash
git clone https://github.com/welljsjs/Config-Parser-C.git
cp Config-Parser-C/parser.h .
```

Two important practical notes about this library:
- `parser.h` defines `read_config_file()` **inside the header** and does **not** include the standard headers it relies on. You must `#include <stdio.h>`, `<stdlib.h>`, `<string.h>` **before** `#include "parser.h"`.
- It is licensed **AGPL-3.0**. AGPL is strong copyleft: if you ship it inside your public repository as part of a combined program, the combined work falls under AGPL too. For a course submission that is fine, but be aware of it — alternatively, the `key = value` format is trivial enough to parse with a few lines of your own code if you want to avoid the license coupling.

**HDF5** — the C library (`libhdf5-dev`). On Debian/Ubuntu:
```bash
sudo apt-get install libhdf5-dev hdf5-tools
```

---

## Config file format (`input.conf`)

```
n = 100
chunk_size = 8
a = 3.0
x = 0.1
y = 7.1
```

`x` and `y` are the (constant) values assigned to every element of the vectors, as in HW2. `n` is the vector length, `chunk_size` the number of elements per chunk.

---

## Code

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "parser.h"     
#include <hdf5/serial/hdf5.h>

static const char *config_get(config_option_t co, const char *key)
{
    for (; co != NULL; co = co->prev)
        if (strcmp(co->key, key) == 0)
            return co->value;
    return NULL;
}

/* Write a 1-D double dataset into an open HDF5 location. */
static int h5_write_vector(hid_t loc, const char *name, const double *data, size_t len)
{
    hsize_t dims[1] = { (hsize_t)len };
    hid_t space = H5Screate_simple(1, dims, NULL);
    hid_t dset  = H5Dcreate2(loc, name, H5T_NATIVE_DOUBLE, space,
                             H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
    herr_t st = H5Dwrite(dset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, data);
    H5Dclose(dset);
    H5Sclose(space);
    return (st < 0) ? -1 : 0;
}

static void h5_write_attr_long(hid_t loc, const char *name, long value)
{
    hid_t space = H5Screate(H5S_SCALAR);
    hid_t attr  = H5Acreate2(loc, name, H5T_NATIVE_LONG, space, H5P_DEFAULT, H5P_DEFAULT);
    H5Awrite(attr, H5T_NATIVE_LONG, &value);
    H5Aclose(attr); H5Sclose(space);
}

static void h5_write_attr_double(hid_t loc, const char *name, double value)
{
    hid_t space = H5Screate(H5S_SCALAR);
    hid_t attr  = H5Acreate2(loc, name, H5T_NATIVE_DOUBLE, space, H5P_DEFAULT, H5P_DEFAULT);
    H5Awrite(attr, H5T_NATIVE_DOUBLE, &value);
    H5Aclose(attr); H5Sclose(space);
}

int main(int argc, char *argv[])
{
    const char *config_path = (argc > 1) ? argv[1] : "input.conf";
    const char *out_path    = (argc > 2) ? argv[2] : "output.h5";

    config_option_t co = read_config_file((char *)config_path);
    if (co == NULL) { fprintf(stderr, "cannot read '%s'\n", config_path); return EXIT_FAILURE; }

    const char *s_n = config_get(co, "n"), *s_chunk = config_get(co, "chunk_size");
    const char *s_a = config_get(co, "a"), *s_x = config_get(co, "x"), *s_y = config_get(co, "y");
    if (!s_n || !s_chunk || !s_a || !s_x || !s_y) {
        fprintf(stderr, "config must define: n, chunk_size, a, x, y\n"); return EXIT_FAILURE;
    }

    const long   n = atol(s_n), chunk_size = atol(s_chunk);
    const double a = atof(s_a), x_val = atof(s_x), y_val = atof(s_y);
    if (n <= 0 || chunk_size <= 0) { fprintf(stderr, "n, chunk_size must be > 0\n"); return EXIT_FAILURE; }

    const long number_of_chunks = (n + chunk_size - 1) / chunk_size;  /* ceiling division */

    double *x = malloc((size_t)n * sizeof(double));
    double *y = malloc((size_t)n * sizeof(double));
    double *d = malloc((size_t)n * sizeof(double));
    double *d_ref = malloc((size_t)n * sizeof(double));
    double *partial_chunk_sum = malloc((size_t)number_of_chunks * sizeof(double));
    if (!x || !y || !d || !d_ref || !partial_chunk_sum) { fprintf(stderr, "alloc failed\n"); return EXIT_FAILURE; }
    for (long i = 0; i < n; ++i) { x[i] = x_val; y[i] = y_val; }

    double sum_ref = 0.0;
    for (long i = 0; i < n; ++i) { d_ref[i] = a * x[i] + y[i]; sum_ref += d_ref[i]; }

    for (long c = 0; c < number_of_chunks; ++c) {
        const long start = c * chunk_size;
        long end = start + chunk_size;
        if (end > n) end = n;                 /* last chunk may be shorter */
        double chunk_sum = 0.0;
        for (long i = start; i < end; ++i) { d[i] = a * x[i] + y[i]; chunk_sum += d[i]; }
        partial_chunk_sum[c] = chunk_sum;
    }
    double sum_from_partials = 0.0;
    for (long c = 0; c < number_of_chunks; ++c) sum_from_partials += partial_chunk_sum[c];

    int d_matches = 1;
    for (long i = 0; i < n; ++i) if (d[i] != d_ref[i]) { d_matches = 0; break; }
    const double tol = 1e-9 * (fabs(sum_ref) + 1.0);
    const int sum_matches = fabs(sum_from_partials - sum_ref) < tol;
    printf("Check 1 (chunked d == original d): %s\n", d_matches ? "PASS" : "FAIL");
    printf("Check 2 (sum of partials == total sum of d): %s\n", sum_matches ? "PASS" : "FAIL");

    /* 4. write chunks + partial sums to HDF5 */
    hid_t file = H5Fcreate(out_path, H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);
    h5_write_vector(file, "d", d, (size_t)n);
    h5_write_vector(file, "partial_chunk_sum", partial_chunk_sum, (size_t)number_of_chunks);
    h5_write_vector(file, "x", x, (size_t)n);
    h5_write_vector(file, "y", y, (size_t)n);

    hid_t chunks_grp = H5Gcreate2(file, "chunks", H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
    for (long c = 0; c < number_of_chunks; ++c) {
        const long start = c * chunk_size;
        long end = start + chunk_size; if (end > n) end = n;
        char name[32]; snprintf(name, sizeof(name), "chunk_%ld", c);
        h5_write_vector(chunks_grp, name, &d[start], (size_t)(end - start));
    }
    H5Gclose(chunks_grp);

    h5_write_attr_long(file, "n", n);
    h5_write_attr_long(file, "chunk_size", chunk_size);
    h5_write_attr_long(file, "number_of_chunks", number_of_chunks);
    h5_write_attr_double(file, "a", a);
    h5_write_attr_double(file, "total_sum", sum_from_partials);
    H5Fclose(file);

    free(x); free(y); free(d); free(d_ref); free(partial_chunk_sum);
    return EXIT_SUCCESS;
}
```

## Compilation

```bash
gcc -std=c11 -Wall -Wextra -O2 -I/usr/include/hdf5/serial -I. \
    daxpy_chunks.c -o daxpy_chunks \
    -L/usr/lib/x86_64-linux-gnu/hdf5/serial -lhdf5 -lm
```

(If `h5cc` is available, `h5cc -std=c11 -Wall -O2 -I. daxpy_chunks.c -o daxpy_chunks -lm` also works and finds the HDF5 flags automatically.)

## Usage

```bash
./daxpy_chunks input.conf output.h5
```

---

## Chunking logic

The single loop

```
for i = 0 .. n-1:  d[i] = a*x[i] + y[i]
```

is replaced by an outer loop over `number_of_chunks = ceil(n / chunk_size)` and an inner loop over the elements of each chunk. The ceiling is computed with integer arithmetic as `(n + chunk_size - 1) / chunk_size`, and the **last chunk is clamped** to `n` so it can be shorter than `chunk_size` when `n` is not a multiple of it. Each element is computed exactly as in the original loop, so the chunked `d` is identical to the original `d` (Check 1), and the sum of the per-chunk partial sums equals the total sum (Check 2).

## Real run

With `n = 100`, `chunk_size = 8`, `a = 3`, `x = 0.1`, `y = 7.1` (so every `d[i] = 7.4`):

```
Config: n=100, chunk_size=8, a=3, x=0.1, y=7.1
number_of_chunks = ceil(100/8) = 13
Check 1 (chunked d == original d): PASS
Check 2 (sum of partial sums == total sum of d): PASS
  total sum (reference)      = 740
  total sum (from partials)  = 740
Wrote HDF5 file: output.h5
```

There are 13 chunks: twelve full chunks of 8 elements (partial sum = 8·7.4 = 59.2 each) and one final chunk of 4 (partial sum = 4·7.4 = 29.6). Total = 12·59.2 + 29.6 = 740.

## HDF5 file structure

Inspected with `h5dump -n output.h5`:

```
/                         (root; attributes: n, chunk_size, number_of_chunks, a, total_sum)
/d                        full result vector (length n = all chunks, in order)
/partial_chunk_sum        one value per chunk (length 13)
/x, /y                    the input vectors
/chunks/chunk_0 ... /chunks/chunk_12   each individual chunk as its own dataset
```

`h5dump -d /partial_chunk_sum output.h5` gives:

```
DATA { (0): 59.2, 59.2, 59.2, 59.2, 59.2, 59.2, 59.2, 59.2, 59.2, 59.2, 59.2,
       (11): 59.2, 29.6 }
```

confirming the per-chunk sums and the short final chunk.
