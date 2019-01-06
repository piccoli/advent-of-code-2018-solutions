#include <stdio.h>

static int run(int acc) {
    static int const lim[] = { 974, 10551374 };

    int const n = lim[acc % 2];
    int /*j,*/ i;

    /* Translated machine code from my input
     * essentially boils down to this: */
    /*
    for (acc = 0, i = 1; i <= n; ++i)
        for (j = 1; j <= n; ++j)
            if (i * j == n)
                acc += i;
    */

    /* Slightly optimized: */
    for (acc = 0, i = 1; i <= n; ++i)
        if (n % i == 0)
            acc += n / i;

    return acc;
}

int main(void) {
    printf("%d\n%d\n", run(0), run(1));
    return 0;
}
