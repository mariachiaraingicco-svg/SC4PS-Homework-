# Homework 02 - Vector Summation

## Exercise
Implement the vector operation: 
**d = ax + y**
where:
- `a` is a scalar
- `x`, `y`, `d` are vectors of dimension N
- All elements of x have the same value
- All elements of y have the same value

## Compilation
```bash
gcc -o vector_sum vector_sum.c -lm
```

## Usage
Run the program and enter the requested values:
```bash
./vector_sum
```

Example input: 

Enter the value of a: 3

Enter the value of x: 0.1

Enter the value of y: 7.1

Enter the dimension N: 1000000

## Tests Required
Test with:
- N = 10
- N = 10^6 (1000000)
- N = 10^8 (100000000)

Special test case:
- a = 3, x = 0.1, y = 7.1
- Expected: 7.4

## Problems Found

### 1. Large N values (N = 10^8)
For N = 10^8, the program needs about 2.4 GB of memory. 
- **Solution**: Used dynamic memory allocation with `malloc()`
- Static arrays would cause stack overflow

### 2. Floating-point precision (a=3, x=0.1, y=7.1)
The test with a=3, x=0.1, y=7.1 does NOT give exactly 7.4!

**Result**: 7.399999999999999...

**Why?** Decimal numbers like 0.1 and 7.1 cannot be represented exactly in binary floating-point format. This causes small rounding errors.

**Lesson learned**: Never use `==` to compare floating-point numbers. Use a tolerance instead:
```c
if (fabs(result - expected) < 1e-10) // OK
```

## Output Example
Expected value: 7.3999999999999995
All 1000000 elements are equal to 7.3999999999999995
First 5 elements: 7.3999999999999995 7.3999999999999995 7.3999999999999995 ...

## Key Points
- Used `double` instead of `int` for decimal values
- Used `malloc()` for large arrays
- Discovered floating-point representation issues
