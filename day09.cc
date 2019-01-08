#include <list>
#include <vector>
#include <iostream>
#include <algorithm>

using namespace std;

static long long highest_score(size_t const number_of_players, long long const last_marble) {
    vector<long long> score(number_of_players, 0);
    list<long long> circle = { 0 };

    auto current = circle.begin();
    long long next_number = 0LL;

    for (size_t turn = 0; next_number != last_marble; turn = (turn + 1) % number_of_players)
        if (++next_number % 23 != 0) {
            if (++current == circle.end())
                current = circle.begin();

            current = circle.insert(++current, next_number);
        }
        else {
            for (int i = 7; i--; --current)
                if (current == circle.begin())
                    current = circle.end();

            score[turn] += next_number + *current;

            current = circle.erase(current);
        }

    return *max_element(score.begin(), score.end());
}

static vector<string> split(string const& s, string const& delim = " ") {
    vector<string> out;

    for (size_t a = 0, b; ; a = b + delim.length()) {
        b = s.find(delim, a);

        out.push_back(s.substr(a, b));

        if (b == string::npos)
            break;
    }
    return out;
}

int main(void) {
    string line;
    getline(cin, line);

    auto const record = split(line);

    size_t const number_of_players = stoi(record[0]);
    long long const last_marble = stoll(record[6]);

    cout << highest_score(number_of_players, last_marble      ) << endl;
    cout << highest_score(number_of_players, last_marble * 100) << endl;

    return 0;
}
