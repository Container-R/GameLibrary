#!/usr/bin/env bash
# Host Linux GNU tool fixture; compiles owned artifacts and never executes them.
set -euo pipefail
export LC_ALL=C
t=$(mktemp -d)
trap 'rm -rf -- "$t"' EXIT
cd "$t"
mkdir a b nid stripped split
cat > a/room.c <<'EOF'
#line 41 "quest_room.c"
__attribute__((section(".probe"), noinline, used))
int award_room_key(int points) { return points + 17; }
EOF
cat > b/room.c <<'EOF'
#line 93 "shop_ui.c"
__attribute__((section(".probe"), noinline, used))
int refresh_shop_badge(int points) { return points + 29; }
EOF
build() {
  local src=$1 dest=$2 style=$3
  gcc -shared -fPIC -g -O0 -nostdlib -fno-lto "-ffile-prefix-map=$t=/fixture" \
    "-Wl,--build-id=$style" -Wl,-soname,libplay.so -Wl,--section-start=.probe=0x6000 \
    -o "$dest" "$src"
}
build a/room.c a/libplay.so sha1
build b/room.c b/libplay.so sha1
build b/room.c nid/libplay.so none
objcopy --strip-debug a/libplay.so stripped/libplay.so
objcopy --only-keep-debug a/libplay.so split/libplay.so.debug
id() { readelf -n "$1" | awk '/Build ID:/ {print $3}'; }
symbol_pc() { nm -D --defined-only "$1" | awk -v f="$2" '$3==f {print "0x"$1}'; }
elf_type() { readelf -h "$1" | awk '/Class:|Machine:/ {$1=$1;print}'; }
a_id=$(id a/libplay.so)
b_id=$(id b/libplay.so)
none_id=$(id nid/libplay.so)
pc=$(symbol_pc a/libplay.so award_room_key)
b_pc=$(symbol_pc b/libplay.so refresh_shop_badge)
nid_pc=$(symbol_pc nid/libplay.so refresh_shop_badge)
[[ -n "$pc" && "$pc" == "$b_pc" && "$pc" == "$nid_pc" ]]
[[ "$((pc))" == "$((0x6000))" ]]
[[ -n "$a_id" && -n "$b_id" && "$a_id" != "$b_id" && -z "$none_id" ]]
[[ "$(id stripped/libplay.so)" == "$a_id" && "$(id split/libplay.so.debug)" == "$a_id" ]]
[[ "$(elf_type a/libplay.so)" == "$(elf_type b/libplay.so)" ]]
lookup() {
  addr2line -f -e "$1" "$pc" | sed -E 's@^.*/([^/]+\.c:[0-9]+.*)$@\1@'
}
a_line=$(lookup a/libplay.so)
b_line=$(lookup b/libplay.so)
nid_line=$(lookup nid/libplay.so)
strip_line=$(lookup stripped/libplay.so)
split_line=$(lookup split/libplay.so.debug)
[[ "$a_line" == $'award_room_key\nquest_room.c:42'* ]]
[[ "$b_line" == $'refresh_shop_badge\nshop_ui.c:94'* ]]
[[ "$nid_line" == "$b_line" && "$split_line" == "$a_line" ]]
[[ "$strip_line" == $'award_room_key\n??:?'* ]]
# Deliberately local provenance policy, separate from direct GNU lookup.
# Filename, ABI and genuine release capture are production checks not modeled here.
decision() {
  if [[ -z "$1" || -z "$2" ]]; then printf 'UNVERIFIED';
  elif [[ "$1" != "$2" ]]; then printf 'REJECT_MISMATCH';
  else printf 'BUILD_ID_MATCH'; fi
}
show() {
  printf '%s\t%s\t%s\n' "$1" "$(decision "$2" "$3")" "$(tr '\n' ' ' <<< "$4")"
}
printf 'scope=synthetic link-time ELF address, GNU host tools; no crash/ASLR/APK/NDK\n'
printf 'pc=0x%x\nA=%s\nB=%s\n' "$((pc))" "$a_id" "$b_id"
printf 'candidate\tlocal identity status\tdirect GNU lookup (ignores frame ID)\n'
show a_full "$a_id" "$a_id" "$a_line"
show b_wrong "$a_id" "$b_id" "$b_line"
show frame_missing_id "" "$b_id" "$b_line"
show library_missing_id "$a_id" "$none_id" "$nid_line"
show a_stripped "$a_id" "$a_id" "$strip_line"
show a_separate_debug "$a_id" "$a_id" "$split_line"
