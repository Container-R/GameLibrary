// Standalone fixture for a positive-BPM, no-warp subset. The included
// functions are generated locally from the pinned StepMania source.
#include <array>
#include <cassert>
#include <cfloat>
#include <climits>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

constexpr int rows_per_beat = 48;
int BeatToNoteRow(float b) { return std::lrint(b * rows_per_beat); }
float NoteRowToBeat(int row) { return row / float(rows_per_beat); }

enum Segment { SEGMENT_BPM, SEGMENT_WARP, SEGMENT_STOP, SEGMENT_DELAY };
struct TimingSegment {
    int row;
    float value;
    int GetRow() const { return row; }
    float GetBeat() const { return NoteRowToBeat(row); }
    float GetBPS() const { return value / 60.f; }
    float GetPause() const { return value; }
    float GetLength() const { return value; }
};
const TimingSegment* ToBPM(const TimingSegment* s) { return s; }
const TimingSegment* ToStop(const TimingSegment* s) { return s; }
const TimingSegment* ToDelay(const TimingSegment* s) { return s; }
using WarpSegment = TimingSegment;
using StopSegment = TimingSegment;
using DelaySegment = TimingSegment;
WarpSegment* ToWarp(TimingSegment* s) { return s; }

struct TimingData {
    struct GetBeatStarts {
        unsigned bpm = 0, warp = 0, stop = 0, delay = 0;
        int last_row = 0;
        float last_time = 0, warp_destination = 0;
        bool is_warping = false;
    };
    struct GetBeatArgs {
        float elapsed_time = 0, beat = 0, bps_out = 0, warp_dest_out = 0;
        int warp_begin_out = -1;
        bool freeze_out = false, delay_out = false;
    };
    std::array<std::vector<TimingSegment*>, 4> m_avpTimingSegments;
    float GetBPMAtRow(int row) const {
        float result = 120;
        for (const auto* s : m_avpTimingSegments[SEGMENT_BPM]) {
            if (s->row > row) break;
            result = s->value;
        }
        return result;
    }
    void GetBeatInternal(GetBeatStarts&, GetBeatArgs&, unsigned) const;
    float GetElapsedTimeInternal(GetBeatStarts&, float, unsigned) const;
};

#include "timing-excerpt.inc"

int main() {
    TimingSegment bpm0{0, 120}, bpm8{8 * rows_per_beat, 180};
    TimingSegment pause{8 * rows_per_beat, 0.4f};
    const std::array<std::array<long, 3>, 2> expected = {{
        {{168000, 192000, 227200}}, {{168000, 211200, 227200}}
    }};
    for (int delay = 0; delay < 2; ++delay) {
        TimingData t;
        t.m_avpTimingSegments[SEGMENT_BPM] = {&bpm0, &bpm8};
        t.m_avpTimingSegments[delay ? SEGMENT_DELAY : SEGMENT_STOP] = {&pause};
        std::cout << (delay ? "Delay:" : "Stop:");
        for (int beat = 7; beat <= 9; ++beat) {
            TimingData::GetBeatStarts start;
            long sample = std::lround(t.GetElapsedTimeInternal(start, beat, INT_MAX) * 48000.f);
            assert(sample == expected[delay][beat - 7]);
            std::cout << ' ' << sample;
        }
        std::cout << '\n';
        for (float sec : {3.99f, 4.0f, 4.2f, 4.4f}) {
            TimingData::GetBeatStarts start;
            TimingData::GetBeatArgs args;
            args.elapsed_time = sec;
            t.GetBeatInternal(start, args, INT_MAX);
            const bool held = sec >= 4.0f && sec < 4.4f;
            assert(args.freeze_out == (held && !delay));
            assert(args.delay_out == (held && delay));
            if (held) assert(args.beat == 8);
            std::cout << std::fixed << std::setprecision(3) << "  t=" << sec
                << " beat=" << args.beat << " freeze=" << args.freeze_out
                << " delay=" << args.delay_out << '\n';
        }
    }
}
