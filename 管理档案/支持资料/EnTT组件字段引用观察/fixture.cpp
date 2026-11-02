#include "entt.hpp"
#include <cstdint>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string_view>
#include <variant>
#include <vector>

struct Link { entt::entity target; };
using Token = std::variant<std::uint32_t, entt::entity, Link>;
struct OutputArchive {
    std::vector<Token> tokens;
    void operator()(std::uint32_t value) { tokens.emplace_back(value); }
    void operator()(entt::entity value) { tokens.emplace_back(value); }
    void operator()(const Link &value) { tokens.emplace_back(value); }
};
struct InputArchive {
    const std::vector<Token> &tokens;
    std::size_t pos{};
    std::optional<entt::entity> observed_target{};
    template<typename T> void read(T &value) {
        if(pos >= tokens.size() || !std::holds_alternative<T>(tokens[pos])) { throw std::runtime_error("archive_type_or_bounds"); }
        value = std::get<T>(tokens[pos++]);
    }
    void operator()(std::uint32_t &value) { read(value); }
    void operator()(entt::entity &value) { read(value); }
    void operator()(Link &value) { read(value); observed_target = value.target; }
};
static void require(bool value) {
    if(!value) { throw std::runtime_error("fixture_precondition"); }
}
static void handle(entt::entity value) {
    std::cout << "{\"full\":" << entt::to_integral(value)
              << ",\"index\":" << entt::to_entity(value)
              << ",\"version\":" << entt::to_version(value) << '}';
}

static void optional_handle(std::optional<entt::entity> value) {
    if(value) { handle(*value); } else { std::cout << "null"; }
}
static void tokens(const char *stream, const OutputArchive &archive) {
    for(std::size_t i{}; i < archive.tokens.size(); ++i) {
        std::cout << "{\"kind\":\"token\",\"stream\":\"" << stream << "\",\"index\":" << i << ",\"type\":\"";
        const auto &token = archive.tokens[i];
        if(const auto *v = std::get_if<std::uint32_t>(&token)) { std::cout << "uint32\",\"value\":" << *v; }
        else if(const auto *v = std::get_if<entt::entity>(&token)) { std::cout << "entity\",\"value\":"; handle(*v); }
        else { std::cout << "Link\",\"value\":{\"target\":"; handle(std::get<Link>(token).target); std::cout << '}'; }
        std::cout << "}\n";
    }
}
static void emit(const char *name, entt::registry &remote, entt::registry &local,
                 const entt::continuous_loader &loader, entt::entity box, entt::entity holder, entt::entity seed,
                 const OutputArchive &entities, const OutputArchive &links, const InputArchive &er, const InputArchive &lr,
                 std::optional<entt::entity> loaded, std::optional<entt::entity> previous_box, std::optional<entt::entity> previous_holder) {
    const auto B=loader.map(box), L=loader.map(holder);
    const bool rv=remote.valid(box), hv=remote.valid(holder), sv=local.valid(seed);
    require(hv && remote.all_of<Link>(holder));
    const auto source=remote.get<Link>(holder).target;
    require(links.tokens.size()==3 && std::holds_alternative<Link>(links.tokens[2]));
    const auto archived=std::get<Link>(links.tokens[2]).target;
    const bool bc=loader.contains(box), hc=loader.contains(holder), bv=local.valid(B), lv=local.valid(L);
    const bool has=lv && local.all_of<Link>(L);
    const auto active=local.storage<entt::entity>().free_list(), count=local.storage<Link>().size();
    const std::optional<bool> target_valid=loaded ? std::optional<bool>{local.valid(*loaded)} : std::nullopt;
    const std::optional<bool> equals=loaded ? std::optional<bool>{*loaded==seed} : std::nullopt;
    std::cout << "{\"kind\":\"stage\",\"stage\":\"" << name << "\"";
    std::cout << ",\"remote_box\":"; handle(box);
    std::cout << ",\"remote_holder\":"; handle(holder);
    std::cout << ",\"local_seed\":"; handle(seed);
    std::cout << ",\"mapped_box\":"; handle(B);
    std::cout << ",\"mapped_holder\":"; handle(L);
    std::cout << ",\"source_target\":"; handle(source);
    std::cout << ",\"archive_target\":"; handle(archived);
    std::cout << ",\"input_target\":"; optional_handle(lr.observed_target);
    std::cout << ",\"loaded_target\":"; optional_handle(loaded);
    std::cout << ",\"source_box_valid\":" << rv;
    std::cout << ",\"source_holder_valid\":" << hv;
    std::cout << ",\"seed_valid\":" << sv;
    std::cout << ",\"box_contains\":" << bc;
    std::cout << ",\"holder_contains\":" << hc;
    std::cout << ",\"mapped_box_valid\":" << bv;
    std::cout << ",\"mapped_holder_valid\":" << lv;
    std::cout << ",\"holder_has_link\":" << has;
    std::cout << ",\"target_active_count\":" << active;
    std::cout << ",\"target_link_count\":" << count;
    std::cout << ",\"entity_written\":" << entities.tokens.size();
    std::cout << ",\"link_written\":" << links.tokens.size();
    std::cout << ",\"entity_read\":" << er.pos;
    std::cout << ",\"link_read\":" << lr.pos;
    std::cout << ",\"loaded_target_in_local_valid\":";
    if(target_valid) { std::cout << *target_valid; } else { std::cout << "null"; }
    std::cout << ",\"loaded_target_equals_seed\":";
    if(equals) { std::cout << *equals; } else { std::cout << "null"; }
    std::cout << "}\n"; std::cout.flush(); require(static_cast<bool>(std::cout));
    require(rv && hv && sv && box!=holder && source==box && archived==box);
    require(entities.tokens.size()==4 && links.tokens.size()==3);
    const std::string_view phase{name};
    if(phase=="prepared") {
        require(B==entt::null && L==entt::null && !bc && !hc && !bv && !lv && !has && active==1 && count==0 && er.pos==0 && lr.pos==0 && !loaded && !lr.observed_target);
    } else {
        require(bc && hc && bv && lv && B!=L && B!=seed && L!=seed && B!=box && active==3 && er.pos==4);
        if(phase=="entities_loaded") { require(!has && count==0 && lr.pos==0 && !loaded && !lr.observed_target); }
        else {
            require(phase=="component_loaded" && has && count==1 && lr.pos==3);
            require(previous_box && previous_holder && B==*previous_box && L==*previous_holder);
            require(loaded && lr.observed_target && *loaded==box && *lr.observed_target==box && *loaded!=B);
            require(target_valid && equals && *equals==(*loaded==seed) && *target_valid==(*loaded==seed || *loaded==B || *loaded==L));
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
        entt::registry remote, local;
        const auto box=remote.create(), holder=remote.create();
        remote.emplace<Link>(holder, Link{box});
        const auto seed=local.create();
        entt::continuous_loader loader{local};
        require(remote.valid(box) && remote.valid(holder) && box!=holder && remote.all_of<Link>(holder));
        require(remote.get<Link>(holder).target==box);
        OutputArchive entities, links;
        entt::snapshot{remote}.get<entt::entity>(entities).get<Link>(links);
        require(entities.tokens.size()==4 && links.tokens.size()==3);
        require(std::get<std::uint32_t>(entities.tokens[0])==2 && std::get<std::uint32_t>(entities.tokens[1])==2);
        const auto e0=std::get<entt::entity>(entities.tokens[2]), e1=std::get<entt::entity>(entities.tokens[3]);
        require((e0==box && e1==holder) || (e0==holder && e1==box));
        require(std::get<std::uint32_t>(links.tokens[0])==1 && std::get<entt::entity>(links.tokens[1])==holder && std::get<Link>(links.tokens[2]).target==box);
        tokens("entities",entities); tokens("links",links);
        InputArchive er{entities.tokens}, lr{links.tokens};
        emit("prepared",remote,local,loader,box,holder,seed,entities,links,er,lr,std::nullopt,std::nullopt,std::nullopt);
        loader.get<entt::entity>(er);
        emit("entities_loaded",remote,local,loader,box,holder,seed,entities,links,er,lr,std::nullopt,std::nullopt,std::nullopt);
        const auto B=loader.map(box), L=loader.map(holder);
        loader.get<Link>(lr);
        const auto current=loader.map(holder);
        require(local.valid(current) && local.all_of<Link>(current));
        const auto loaded=local.get<Link>(current).target;
        emit("component_loaded",remote,local,loader,box,holder,seed,entities,links,er,lr,loaded,B,L);
        std::cout.flush(); return std::cout ? 0 : 3;
    } catch(...) { std::cout.flush(); std::cerr << "fixture_precondition_or_archive_failure\n"; return 2; }
}
