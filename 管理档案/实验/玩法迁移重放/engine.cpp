#include <cstdint>
#include <iostream>
#include <string_view>

int main(int argc, char** argv) {
    using i64 = std::int64_t;
    const bool floor_policy = argc == 2 && std::string_view(argv[1]) == "floor";
    if (argc != 2 || (!floor_policy && std::string_view(argv[1]) != "trunc")) return 2;
    constexpr i64 limit = 1'000'000'000, width = 10;
    i64 x = 0, cell = 0, tick = 0, dx = 0;
    while (std::cin >> dx) {
        if (dx < -limit || dx > limit || tick == limit) return 3;
        x += dx; // Each operand was already within [-limit, limit].
        if (x < -limit || x > limit) return 3;
        auto q = x / width;
        const auto r = x % width;
        if (floor_policy && r < 0) --q;
        std::cout << ++tick << ',' << x << ',' << q << ',';
        if (q != cell) std::cout << "enter:" << q;
        else std::cout << '-';
        std::cout << '\n';
        cell = q;
    }
    return std::cin.eof() ? 0 : 4;
}
