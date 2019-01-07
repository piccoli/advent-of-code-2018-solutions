#include <iostream>
#include <unordered_set>
#include <list>

using namespace std;

int main(void) {
    long long f = 0LL;

    list<long long> sequence;
    unordered_set<long long> cache;

    for (;;) {
        long long c = f | (1LL << 16LL);

        for (f = 7571367LL;;) {
            long long e;

            f += c % (1LL << 8LL);
            f %= 1LL << 24LL;
            f *= 0x16bLL | (1LL << 16LL);
            f %= 1LL << 24LL;

            if (c < 256LL)
                break;

            for (e = 0LL; ((e + 1LL) << 8LL) <= c; ++e)
                ;

            c = e;
        }

        if (cache.find(f) != cache.end()) {
            printf("%lld\n", sequence.front());
            printf("%lld\n", sequence.back());
            return 0;
        }

        cache.insert(f);
        sequence.push_back(f);
    }
}
