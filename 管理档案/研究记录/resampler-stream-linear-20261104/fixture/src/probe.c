/* Original finite fixture driver. It does not implement a resampler. */
#include <float.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "samplerate.h"

_Static_assert(FLT_RADIX == 2 && FLT_MANT_DIG == 24 && sizeof(float) == 4,
               "This fixture requires binary32 float");
_Static_assert(DBL_MANT_DIG >= 53, "This fixture requires binary64 precision");

#define PROTOCOL "resampler-stream-linear-v1"
#define COMMIT "c96f5e3de9c4488f4e6c97f59f5245f22fda22f7"
#define VERSION "libsamplerate-0.2.2 (c) 2002-2008 Erik de Castro Lopo"
#define SENTINEL 1234.0f

static const int whole[16] = {0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13};
static const int reset_result[16] = {0,0,0,1,2,3,4,5,8,8,8,9,10,11,12,13};

typedef struct {
    const char *arm;
    int count;
    long capacities[2], used[2], generated[2];
    int ends[2];
    const int *expected;
} Plan;

static const Plan plans[4] = {
    {"W",1,{20,0},{8,0},{16,0},{1,0},whole},
    {"S",2,{12,12},{4,4},{8,8},{0,1},whole},
    {"R",2,{12,12},{4,4},{8,8},{0,1},reset_result},
    {"C",2,{5,13},{2,6},{5,11},{1,1},whole}
};

static unsigned created, deleted, processed, resets;
static const char *failure = "none";

static const char *boolean(bool value) { return value ? "true" : "false"; }

static void float_hex(float value) {
    if (isnan(value)) fputs("\"nan\"", stdout);
    else if (isinf(value)) fputs(signbit(value) ? "\"-inf\"" : "\"inf\"", stdout);
    else printf("\"%a\"", (double)value);
}

static bool flush_record(void) {
    return fputc('\n', stdout) != EOF && fflush(stdout) == 0;
}

static bool release_state(SRC_STATE *state, const char *arm) {
    SRC_STATE *result = src_delete(state);
    deleted++;
    printf("{\"type\":\"delete\",\"arm\":\"%s\",\"returned_null\":%s}",
           arm, boolean(result == NULL));
    bool io_ok = flush_record();
    if (result != NULL && strcmp(failure, "none") == 0) failure = "delete_error";
    if (!io_ok) failure = "io_error";
    return result == NULL && io_ok;
}

static bool run_arm(const Plan *plan, float accumulated[16]) {
    int error = -1;
    SRC_STATE *state = src_new(SRC_LINEAR, 1, &error);
    if (state != NULL) created++;
    printf("{\"type\":\"create\",\"arm\":\"%s\",\"return_code\":%d,"
           "\"state_present\":%s}", plan->arm, error, boolean(state != NULL));
    bool ok = flush_record();
    if (!ok) failure = "io_error";
    else if (state == NULL || error != 0) { failure = "create_error"; ok = false; }
    if (!ok) {
        if (state != NULL) (void)release_state(state, plan->arm);
        return false;
    }

    float arena[40];
    for (int i = 0; i < 40; i++) arena[i] = SENTINEL;
    for (int i = 0; i < 8; i++) arena[i] = (float)i / 8.0f;
    long input_offset = 0, output_offset = 0;

    for (int step = 0; step < plan->count; step++) {
        if (step == 1 && plan->arm[0] == 'R') {
            int reset_error = src_reset(state);
            resets++;
            printf("{\"type\":\"reset\",\"arm\":\"R\",\"return_code\":%d}", reset_error);
            if (!flush_record()) { failure = "io_error"; ok = false; break; }
            if (reset_error != 0) { failure = "reset_error"; ok = false; break; }
        }
        for (int i = 16; i < 36; i++) arena[i] = SENTINEL;
        long provided = (plan->arm[0] == 'S' || plan->arm[0] == 'R') ? 4 : 8 - input_offset;
        long capacity = plan->capacities[step];
        /* These pointers are derived only from earlier validated actual counts. */
        if (input_offset < 0 || provided <= 0 || input_offset + provided > 8 ||
            capacity <= 0 || capacity > 20 || output_offset < 0 || output_offset > 16) {
            failure = "driver_bounds"; ok = false; break;
        }
        SRC_DATA data = {0};
        data.data_in = arena + input_offset;
        data.data_out = arena + 16;
        data.input_frames = provided;
        data.output_frames = capacity;
        data.input_frames_used = -1;
        data.output_frames_gen = -1;
        data.end_of_input = plan->ends[step];
        data.src_ratio = 2.0;
        int result = src_process(state, &data);
        processed++;

        long u = data.input_frames_used, g = data.output_frames_gen;
        bool safe_g = g >= 0 && g <= capacity;
        bool counts = u >= 0 && u <= provided && safe_g &&
                      u == plan->used[step] && g == plan->generated[step];
        bool values = safe_g && g == plan->generated[step] && output_offset + g <= 16;
        if (values) {
            for (long i = 0; i < g; i++)
                if (!isfinite(arena[16+i]) || arena[16+i] != (float)plan->expected[output_offset+i]/16.0f)
                    values = false;
        }
        bool input = true, guards = true, tail = safe_g;
        for (int i = 0; i < 8; i++) if (arena[i] != (float)i/8.0f) input = false;
        for (int i = 8; i < 16; i++) if (arena[i] != SENTINEL) guards = false;
        for (int i = 36; i < 40; i++) if (arena[i] != SENTINEL) guards = false;
        if (safe_g) for (long i = g; i < 20; i++) if (arena[16+i] != SENTINEL) tail = false;

        printf("{\"type\":\"call\",\"id\":\"%s%d\",\"input_offset\":%ld,"
               "\"input_frames\":%ld,\"output_capacity\":%ld,\"end_of_input\":%d,"
               "\"return_code\":%d,\"input_frames_used\":%ld,\"output_frames_gen\":%ld,"
               "\"arena_hex\":[", plan->arm, step+1, input_offset, provided, capacity,
               plan->ends[step], result, u, g);
        for (int i = 0; i < 40; i++) { if (i) fputc(',', stdout); float_hex(arena[i]); }
        printf("],\"checks\":{\"counts\":%s,\"values\":%s,\"input\":%s,\"guards\":%s,\"tail\":%s}}",
               boolean(counts), boolean(values), boolean(input), boolean(guards), boolean(tail));
        if (!flush_record()) { failure = "io_error"; ok = false; break; }
        /* Raw counts and all forty values are already captured before any cleanup. */
        if (result != 0) failure = "call_error";
        else if (!counts) failure = "count_mismatch";
        else if (!values) failure = "value_mismatch";
        else if (!input) failure = "input_changed";
        else if (!guards) failure = "guard_changed";
        else if (!tail) failure = "tail_changed";
        if (strcmp(failure, "none") != 0) { ok = false; break; }
        for (long i = 0; i < g; i++) accumulated[output_offset+i] = arena[16+i];
        input_offset += u;
        output_offset += g;
    }
    if (!release_state(state, plan->arm)) ok = false;
    return ok;
}

int main(void) {
    const char *version = src_get_version();
    /* Fixed upper bound, including the expected terminating NUL. */
    bool version_match = version != NULL && strncmp(version, VERSION, sizeof(VERSION)) == 0;
    printf("{\"type\":\"header\",\"protocol_id\":\"%s\",\"upstream_commit\":\"%s\","
           "\"reported_version\":", PROTOCOL, COMMIT);
    if (version_match) printf("\"%s\"", VERSION); else fputs("null", stdout);
    printf(",\"version_match\":%s,\"numeric_prerequisites\":true,"
           "\"converter\":\"SRC_LINEAR\",\"channels\":1,\"ratio\":2,"
           "\"input_units\":[0,2,4,6,8,10,12,14],\"unit_denominator\":16}", boolean(version_match));
    if (!flush_record()) return 2;
    bool ok = version_match, cross = false;
    if (!ok) failure = "version_mismatch";
    float accumulated[4][16] = {{0}};
    for (int arm = 0; arm < 4 && ok; arm++) ok = run_arm(&plans[arm], accumulated[arm]);
    if (ok) {
        cross = true;
        for (int i = 0; i < 16; i++) {
            if (accumulated[1][i] != accumulated[0][i] || accumulated[3][i] != accumulated[0][i]) cross = false;
            float difference = accumulated[2][i] - accumulated[0][i];
            float expected_difference = i == 8 ? 2.0f/16.0f : i == 9 ? 1.0f/16.0f : 0.0f;
            if (difference != expected_difference) cross = false;
        }
        if (!cross) { failure = "cross_arm_mismatch"; ok = false; }
    }
    printf("{\"type\":\"summary\",\"status\":\"%s\",\"failure\":\"%s\","
           "\"states_created\":%u,\"delete_calls\":%u,\"process_calls\":%u,"
           "\"reset_calls\":%u,\"cross_arm_ok\":%s}", ok ? "pass" : "fail", failure,
           created, deleted, processed, resets, boolean(cross));
    if (!flush_record()) return 2;
    return ok ? 0 : 1;
}
