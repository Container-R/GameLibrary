#include "entt.hpp"
#include <iostream>
#include <vector>
#include <stdexcept>
struct Speed { int value; };
struct Observer {
    int cache = 3;
    std::vector<int> seen;
    void update(entt::registry &registry, entt::entity entity) {
        const int value = registry.get<Speed>(entity).value;
        seen.push_back(value);
        cache = value;
    }
};
static void require(bool ok) { if(!ok) throw std::runtime_error("observation_mismatch"); }
static void trial(int mode) {
    entt::registry registry;
    const auto entity = registry.create();
    registry.emplace<Speed>(entity, 3);
    Observer observer;
    // Connection is destroyed before observer and registry. No destruction signal is subscribed.
    entt::scoped_connection connection = registry.on_update<Speed>().connect<&Observer::update>(observer);
    const bool valid = registry.valid(entity);
    const bool has_speed = registry.all_of<Speed>(entity);
    const bool connected = static_cast<bool>(connection);
    require(valid && has_speed && connected);
    const int initial = registry.get<Speed>(entity).value;
    require(registry.valid(entity) && initial == 3 && observer.seen.empty() && observer.cache == 3);
    if(mode == 0) registry.get<Speed>(entity).value = 1;
    else registry.patch<Speed>(entity, [mode](Speed &speed) { speed.value = mode == 1 ? 1 : 3; });
    const int final_value = registry.get<Speed>(entity).value;
    std::cout << "{\"case\":" << mode << ",\"initial\":" << initial
              << ",\"valid\":" << (valid ? "true" : "false")
              << ",\"has_speed\":" << (has_speed ? "true" : "false")
              << ",\"connected_initial\":" << (connected ? "true" : "false")
              << ",\"value\":" << final_value << ",\"callbacks\":" << observer.seen.size()
              << ",\"seen\":[";
    for(std::size_t i=0; i<observer.seen.size(); ++i) {
        if(i) std::cout << ',';
        std::cout << observer.seen[i];
    }
    std::cout << "],\"cache\":" << observer.cache << "}\n" << std::flush;
    require(static_cast<bool>(std::cout));
    require(final_value == (mode == 2 ? 3 : 1));
    require(observer.seen.size() == (mode == 0 ? 0u : 1u));
    require(observer.cache == (mode == 1 ? 1 : 3));
    if(mode != 0) require(observer.seen[0] == final_value);
}
int main() {
    try {
        for(int mode=0; mode<3; ++mode) trial(mode);
        return 0;
    } catch(...) {
        std::cerr << "fixture_failed\n" << std::flush;
        return 1;
    }
}
