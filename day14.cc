#include <cctype>
#include <vector>
#include <utility>
#include <iostream>
#include <algorithm>

using namespace std;

template <typename F>
static vector<int> cook(
    size_t const& number_of_recipes,
    vector<int> const& target_scores,
    F const&& stop_criteria);

static bool part1_criteria(
    vector<int> const& scoreboard,
    vector<int> const& target_scores,
    size_t const& number_of_recipes,
    size_t& cursor);

static bool part2_criteria(
    vector<int> const& scoreboard,
    vector<int> const& target_scores,
    size_t const& number_of_recipes,
    size_t& cursor);

static pair<size_t, vector<int>> parse_input(void);

int main(void) {
    auto const inputs            = parse_input();
    auto const number_of_recipes = inputs.first;
    auto const target_scores     = inputs.second;

    auto scoreboard = cook(
        number_of_recipes,
        target_scores,
        part1_criteria
    );

    for_each(
        scoreboard.begin() + number_of_recipes,
        scoreboard.end(),
        [](int const& s) {
            cout << s;
        }
    );

    cout << endl;

    scoreboard = cook(
        number_of_recipes,
        target_scores,
        part2_criteria
    );

    cout << scoreboard.size() - target_scores.size() << endl;

    return 0;
}

template <typename F>
static vector<int> cook(
    size_t const& number_of_recipes,
    vector<int> const& target_scores,
    F const&& stop_criteria) {

    vector<int> scoreboard { 3, 7 };

    int current_recipes[2] = { 0, 1 };

    size_t cursor = 0U;

    while (true) {
        int const score[2] = {
            scoreboard[current_recipes[0]],
            scoreboard[current_recipes[1]]
        };

        auto const sum = score[0] + score[1];

        if (sum < 10)
            scoreboard.push_back(sum);
        else {
            scoreboard.push_back(sum / 10);

            if (stop_criteria(scoreboard, target_scores, number_of_recipes, cursor))
                return scoreboard;

            scoreboard.push_back(sum % 10);
        }

        if (stop_criteria(scoreboard, target_scores, number_of_recipes, cursor))
            return scoreboard;

        int const n = scoreboard.size();
        current_recipes[0] = (1 + score[0] + current_recipes[0]) % n;
        current_recipes[1] = (1 + score[1] + current_recipes[1]) % n;
    }
}

static bool part1_criteria(
    vector<int> const& scoreboard,
    vector<int> const& target_scores,
    size_t const& number_of_recipes,
    size_t& cursor) {

    return scoreboard.size() == number_of_recipes + 10;
}

static bool part2_criteria(
    vector<int> const& scoreboard,
    vector<int> const& target_scores,
    size_t const& number_of_recipes,
    size_t& cursor) {

    if (target_scores[cursor] != scoreboard.back())
        cursor = 0;

    if (target_scores[cursor] == scoreboard.back())
        ++cursor;

    return cursor == target_scores.size();
}

static pair<size_t, vector<int>> parse_input(void) {
    string input;
    cin >> input;

    size_t const number_of_recipes = stoi(input);
    vector<int> target_scores;

    input.erase(
        remove_if(input.begin(), input.end(),
            [](char const c) { return !isdigit(c); }
        ),
        input.end()
    );

    transform(input.begin(), input.end(),
        back_inserter(target_scores),
        [](char const c) { return (int)(c - '0'); }
    );

    return make_pair(number_of_recipes, target_scores);
}
