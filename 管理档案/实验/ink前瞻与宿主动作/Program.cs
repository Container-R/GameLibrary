using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Ink.Runtime;

static void Check(bool ok, string why)
{
    if (!ok) throw new Exception(why);
}

static Story Load(string name) => new(File.ReadAllText(name + ".json"));

static (string Line, string[] Tags) Next(Story story) =>
    (story.Continue().TrimEnd('\r', '\n'), story.currentTags.ToArray());

foreach (bool allowLookahead in new[] { true, false })
{
    var story = Load("permission");
    int host = 0;
    // Bind a real host-side mutation.
    story.BindExternalFunction("stamp", (Action)(() => host++), allowLookahead);
    for (int call = 1; call <= 2; call++)
    {
        var (line, tags) = Next(story);
        int ink = (int)story.variablesState["ledger"];
        Check(line == (call == 1 ? "等我看一下。" : "许可已经签好。"), "text mismatch");
        Check(ink == call - 1, "ink's variable should roll back after first line");
        Check(host == call - (allowLookahead ? 0 : 1), "unexpected external call count");
        Console.WriteLine($"action lookaheadSafe={allowLookahead,-5} Continue#{call}: {line} ink={ink} host={host}");
    }
}

foreach (bool allowLookahead in new[] { true, false })
{
    var story = Load("glue");
    var lines = new List<string>();
    int calls = 0;
    story.BindExternalFunction("route", (Func<object>)(() => { calls++; return "北门"; }), allowLookahead);
    while (story.canContinue)
    {
        var (line, tags) = Next(story);
        if (line.Length > 0) lines.Add(line);
    }
    Check(calls == 1, "unexpected query count in glue case");
    Check(lines.Count == (allowLookahead ? 1 : 2), "unexpected glue line count");
    Check(string.Concat(lines).Replace(" ", "") == "出口在北门。", "unexpected route text");
    Console.WriteLine($"pure read lookaheadSafe={allowLookahead,-5} calls={calls} lines={string.Join(" | ", lines)}");
}

var tagStory = Load("tagged");
var applied = new HashSet<string>(); // In-memory test only, not a durable save.
int grants = 0;
void ApplyReturnedTags(string[] tags)
{
    foreach (var tag in tags)
        if (tag == "action:license:guard_north:first" && applied.Add(tag)) grants++;
}

var first = Next(tagStory);
ApplyReturnedTags(first.Tags);
Check(first.Line == "等我看一下。" && first.Tags.Length == 0 && grants == 0, "too early");
Console.WriteLine($"tag Continue#1: {first.Line} tags={first.Tags.Length} grants={grants}");
string checkpoint = tagStory.state.ToJson();

var second = Next(tagStory);
ApplyReturnedTags(second.Tags);
Check(second.Line == "许可已经签好。" && second.Tags.Length == 1 && grants == 1, "missing effect");
Console.WriteLine($"tag Continue#2: {second.Line} tags={second.Tags.Length} grants={grants}");

tagStory.state.LoadJson(checkpoint);
var replay = Next(tagStory);
Check(replay.Line == second.Line && replay.Tags.SequenceEqual(second.Tags), "replay changed output");
ApplyReturnedTags(replay.Tags);
Check(grants == 1, "duplicate grant");
Console.WriteLine($"tag replay: {replay.Line} tags={replay.Tags.Length} grants={grants}");
