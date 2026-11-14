#include "meshoptimizer.h"
#include <array>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <vector>

using P = std::array<float,3>;
static void check(const char* name, const std::vector<P>& v, const std::vector<unsigned>& in)
{
    for (const size_t target : {size_t(6), size_t(3), size_t(0)}) {
        std::vector<unsigned> out(in.size(), ~0u);
        float error = -1;
        const auto result = meshopt_simplify(out.data(), in.data(), in.size(), v[0].data(), v.size(),
            sizeof(P), target, 0.01f, 0, &error);
        assert(result <= in.size() && result % 3 == 0);
        assert(std::isfinite(error) && error >= 0);
        for (size_t i = 0; i < result; ++i) assert(out[i] < v.size());
        std::printf("%s input=%zu target=%zu returned=%zu error=%.9g budget=%s\n",
                    name, in.size(), target, result, error, result <= target ? "pass" : "miss");
    }
}
int main()
{
    std::vector<P> plane;
    for(int y=0;y<4;++y) for(int x=0;x<4;++x) plane.push_back({float(x),float(y),0.f});
    std::vector<unsigned> indices;
    for(unsigned y=0;y<3;++y) for(unsigned x=0;x<3;++x) {
        const unsigned a=y*4+x;
        indices.insert(indices.end(),{a,a+1,a+5,a,a+5,a+4});
    }
    check("4x4_plane",plane,indices);

    std::vector<P> islands;
    std::vector<unsigned> island_indices;
    for(unsigned t=0;t<3;++t) {
        const float x=float(t*3);
        islands.insert(islands.end(),{P{x,0,0},P{x+1,0,0},P{x,1,0}});
        island_indices.insert(island_indices.end(),{3*t,3*t+1,3*t+2});
    }
    check("three_islands",islands,island_indices);
}
