// Original finite fixture. The solver itself is the unchanged upstream XPBD.cpp.
#include <PositionBasedDynamics/XPBD.h>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <type_traits>

#ifdef USE_DOUBLE
#error This protocol freezes the default float Real profile.
#endif
#ifdef __FAST_MATH__
#error Fast math is excluded by the frozen protocol.
#endif
#ifndef EIGEN_MPL2_ONLY
#error The reviewed Eigen license restriction must be enabled.
#endif
static_assert(std::is_same<Real, float>::value, "Real must be float");
static_assert(sizeof(Real) == 4 && std::numeric_limits<Real>::digits == 24,
              "This finite protocol requires binary32 Real");
static_assert(std::numeric_limits<Real>::is_iec559, "IEEE Real required");

namespace {
using Points = std::array<Vector3r, 3>;
void require(bool ok, const char* why) {
    if (!ok) throw std::runtime_error(why);
}
void finite(Real x) { require(std::isfinite(x), "nonfinite scalar"); }
void finite(const Vector3r& p) { for (int k=0;k<3;++k) finite(p[k]); }
void invariant(const Points& p, const std::array<Real,2>& lambda) {
    for (const auto& x:p) {
        finite(x);
        require(x[1] == Real(0) && x[2] == Real(0), "lost collinearity");
    }
    require(p[0][0] == Real(0), "anchor moved");
    require(p[1][0] > p[0][0] && p[2][0] > p[1][0], "point order changed");
    for (Real x:lambda) finite(x);
}
void vector_json(const Vector3r& p) {
    std::cout << '[' << double(p[0]) << ',' << double(p[1]) << ',' << double(p[2]) << ']';
}
void points_json(const Points& p) {
    std::cout << '[';
    for (int i=0;i<3;++i) { if(i) std::cout << ','; vector_json(p[i]); }
    std::cout << ']';
}
void lambdas_json(const std::array<Real,2>& x) {
    std::cout << '[' << double(x[0]) << ',' << double(x[1]) << ']';
}
}

int main() {
    try {
        std::cout << std::setprecision(std::numeric_limits<double>::max_digits10);
        const Real stiffness=Real(100), dt=Real(0.1), rest=Real(1);
        const std::array<Real,3> inv_mass{{Real(0),Real(1),Real(1)}};
        const Real scaled=Real(1)/(stiffness*dt*dt);
        require(stiffness>Real(0) && dt>Real(0), "invalid stiffness or dt");
        finite(scaled);
        Points p{{Vector3r(0,0,0),Vector3r(Real(1.2),0,0),Vector3r(Real(2.6),0,0)}};
        std::array<Real,2> lambda{{Real(0),Real(0)}};
        invariant(p,lambda);
        std::cout << "{\"record\":\"header\",\"real_bytes\":" << sizeof(Real)
                  << ",\"real_digits\":" << std::numeric_limits<Real>::digits
                  << ",\"stiffness\":" << double(stiffness) << ",\"dt\":" << double(dt)
                  << ",\"rest_length\":" << double(rest) << ",\"scaled_native\":" << double(scaled)
                  << ",\"eigen\":[" << EIGEN_WORLD_VERSION << ',' << EIGEN_MAJOR_VERSION << ',' << EIGEN_MINOR_VERSION
                  << "],\"initial_positions\":";
        points_json(p); std::cout << ",\"initial_lambdas\":"; lambdas_json(lambda); std::cout << "}\n";
        unsigned call=0;
        for(unsigned sweep=1;sweep<=8;++sweep) {
            for(unsigned constraint=0;constraint<2;++constraint) {
                const unsigned a=constraint,b=constraint+1;
                invariant(p,lambda);
                const Points before=p;
                const auto lambda_before=lambda;
                const Real distance=(p[a]-p[b]).norm();
                const Real denominator=inv_mass[a]+inv_mass[b]+scaled;
                finite(distance); finite(denominator);
                require(distance>Real(1e-6), "degenerate native distance branch");
                require(denominator>Real(1e-6), "degenerate native denominator branch");
                Vector3r ca=Vector3r::Constant(std::numeric_limits<Real>::quiet_NaN());
                Vector3r cb=ca;
                const bool ok=PBD::XPBD::solve_DistanceConstraint(
                    p[a],inv_mass[a],p[b],inv_mass[b],rest,stiffness,dt,lambda[constraint],ca,cb);
                require(ok, "native routine returned false");
                finite(ca); finite(cb); finite(lambda[constraint]);
                // Apply returned corrections immediately, matching the inspected native caller.
                if(inv_mass[a]!=Real(0)) p[a]+=ca;
                if(inv_mass[b]!=Real(0)) p[b]+=cb;
                invariant(p,lambda);
                require(lambda[1-constraint]==lambda_before[1-constraint], "other multiplier changed");
                ++call;
                std::cout << "{\"record\":\"call\",\"call\":" << call << ",\"sweep\":" << sweep
                          << ",\"constraint\":" << constraint << ",\"native_return\":true,\"distance_before\":" << double(distance)
                          << ",\"denominator\":" << double(denominator) << ",\"positions_before\":";
                points_json(before); std::cout << ",\"lambdas_before\":"; lambdas_json(lambda_before);
                std::cout << ",\"corrections\":["; vector_json(ca); std::cout << ','; vector_json(cb);
                std::cout << "],\"positions_after\":"; points_json(p);
                std::cout << ",\"lambdas_after\":"; lambdas_json(lambda); std::cout << "}\n";
            }
            if(sweep==1 || sweep==2 || sweep==8) {
                std::cout << "{\"record\":\"checkpoint\",\"sweep\":" << sweep << ",\"positions\":";
                points_json(p); std::cout << ",\"lambdas\":"; lambdas_json(lambda); std::cout << "}\n";
            }
        }
        require(call==16, "unexpected native call count");
        std::cout << "{\"record\":\"trace_complete\",\"native_calls\":16,\"sweeps\":8}\n";
        require(bool(std::cout), "output stream failure");
        return 0;
    } catch(const std::exception& e) {
        std::cerr << "Fixture aborted: " << e.what() << '\n';
        return 2;
    }
}
