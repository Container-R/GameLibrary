#include "entt.hpp"
#include <cstdint>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string_view>
#include <variant>
#include <vector>

using Token = std::variant<std::uint32_t, entt::entity>;
struct OutputArchive {
    std::vector<Token> tokens;
    void operator()(std::uint32_t value) { tokens.emplace_back(value); }
    void operator()(entt::entity value) { tokens.emplace_back(value); }
};
struct InputArchive {
    const std::vector<Token> &tokens;
    std::size_t pos{};
    void operator()(std::uint32_t &value) {
        if(pos >= tokens.size() || !std::holds_alternative<std::uint32_t>(tokens[pos])) {
            throw std::runtime_error("archive_uint32");
        }
        value = std::get<std::uint32_t>(tokens[pos++]);
    }
    void operator()(entt::entity &value) {
        if(pos >= tokens.size() || !std::holds_alternative<entt::entity>(tokens[pos])) {
            throw std::runtime_error("archive_entity");
        }
        value = std::get<entt::entity>(tokens[pos++]);
    }
};
static void require(bool value) {
    if(!value) { throw std::runtime_error("fixture_precondition"); }
}
static void handle(entt::entity value) {
    std::cout << "{\"full\":" << entt::to_integral(value)
              << ",\"index\":" << entt::to_entity(value)
              << ",\"version\":" << entt::to_version(value) << '}';
}
static void emit(const char *stage, entt::registry &remote, entt::registry &local,
                 const entt::continuous_loader &loader, entt::entity source,
                 entt::entity seed, std::optional<entt::entity> initial,
                 std::optional<std::size_t> consumed) {
    const auto mapped = loader.map(source);
    const bool contains = loader.contains(source);
    const bool nonnull = mapped != entt::null;
    const bool valid = local.valid(mapped);
    const auto active = local.storage<entt::entity>().free_list();
    const std::optional<bool> initial_valid = initial ? std::optional<bool>{local.valid(*initial)} : std::nullopt;
    const bool source_valid = remote.valid(source);
    const bool seed_valid = local.valid(seed);
    std::cout << "{\"kind\":\"stage\",\"stage\":\"" << stage << "\",\"source\":";
    handle(source);
    std::cout << ",\"seed\":"; handle(seed);
    std::cout << ",\"mapped_now\":"; handle(mapped);
    std::cout << ",\"mapped_initial\":";
    if(initial) { handle(*initial); } else { std::cout << "null"; }
    std::cout << ",\"contains\":" << contains
              << ",\"mapped_nonnull\":" << nonnull
              << ",\"mapped_valid\":" << valid
              << ",\"active_count\":" << active
              << ",\"initial_valid\":";
    if(initial) { std::cout << *initial_valid; } else { std::cout << "null"; }
    std::cout << ",\"source_valid\":" << source_valid
              << ",\"seed_valid\":" << seed_valid
              << ",\"input_consumed\":";
    if(consumed) { std::cout << *consumed; } else { std::cout << "null"; }
    std::cout << "}\n";
    std::cout.flush();
    require(static_cast<bool>(std::cout));
    // Check the captured observation after emitting it; never print constants
    // instead of observations, and never proceed past a failed stage.
    require(source_valid && seed_valid);
    const std::string_view phase{stage};
    if(phase == "before_load") {
        require(!contains && !nonnull && !valid && active == 1 && !initial && !consumed);
    } else {
        require(initial.has_value() && *initial != entt::null && *initial != seed);
        require(contains && nonnull && mapped != seed);
        if(phase == "loaded") {
            require(valid && active == 2 && *initial_valid && mapped == *initial && consumed && *consumed == 3);
        } else if(phase == "externally_destroyed") {
            require(!valid && active == 1 && !*initial_valid && mapped == *initial && !consumed);
        } else if(phase == "reloaded") {
            require(valid && active == 2 && !*initial_valid && mapped != *initial && consumed && *consumed == 3);
        } else {
            require(false);
        }
    }
}
int main() {
    std::cout << std::boolalpha;
    try {
        std::cout << "{\"kind\":\"declaration\",\"schema\":1,\"cplusplus\":" << __cplusplus
                  << ",\"gcc\":";
#ifdef __GNUC__
        std::cout << '[' << __GNUC__ << ',' << __GNUC_MINOR__ << ',' << __GNUC_PATCHLEVEL__ << ']';
#else
        std::cout << "null";
#endif
        std::cout << ",\"clang\":";
#ifdef __clang__
        std::cout << '[' << __clang_major__ << ',' << __clang_minor__ << ',' << __clang_patchlevel__ << ']';
#else
        std::cout << "null";
#endif
        std::cout << ",\"entt\":[" << ENTT_VERSION_MAJOR << ',' << ENTT_VERSION_MINOR << ',' << ENTT_VERSION_PATCH
                  << "],\"entity_mask\":" << entt::entt_traits<entt::entity>::entity_mask
                  << ",\"version_mask\":" << entt::entt_traits<entt::entity>::version_mask << "}\n";
        entt::registry remote;
        entt::registry local;
        const auto source = remote.create();
        const auto seed = local.create();
        entt::continuous_loader loader{local};
        OutputArchive output;
        entt::snapshot{remote}.get<entt::entity>(output);
        const auto &tokens = output.tokens;
        require(tokens.size() == 3);
        require(std::holds_alternative<std::uint32_t>(tokens[0]) && std::get<std::uint32_t>(tokens[0]) == 1);
        require(std::holds_alternative<std::uint32_t>(tokens[1]) && std::get<std::uint32_t>(tokens[1]) == 1);
        require(std::holds_alternative<entt::entity>(tokens[2]) && std::get<entt::entity>(tokens[2]) == source);
        for(std::size_t index{}; index < tokens.size(); ++index) {
            std::cout << "{\"kind\":\"token\",\"index\":" << index << ",\"type\":\"";
            if(const auto *value = std::get_if<std::uint32_t>(&tokens[index])) {
                std::cout << "uint32\",\"value\":" << *value;
            } else {
                std::cout << "entity\",\"value\":" << entt::to_integral(std::get<entt::entity>(tokens[index]));
            }
            std::cout << "}\n";
        }
        emit("before_load", remote, local, loader, source, seed, std::nullopt, std::nullopt);
        InputArchive first{tokens};
        loader.get<entt::entity>(first);
        require(first.pos == tokens.size());
        const auto initial = loader.map(source);
        emit("loaded", remote, local, loader, source, seed, initial, first.pos);
        local.destroy(initial);
        emit("externally_destroyed", remote, local, loader, source, seed, initial, std::nullopt);
        InputArchive second{tokens};
        loader.get<entt::entity>(second);
        require(second.pos == tokens.size());
        emit("reloaded", remote, local, loader, source, seed, initial, second.pos);
        std::cout.flush();
        return std::cout ? 0 : 3;
    } catch(...) {
        std::cout.flush();
        std::cerr << "fixture_precondition_or_archive_failure\n";
        return 2;
    }
}
