using System.Security.Cryptography;
using System.Text.Json;
using Ink.Runtime;
using Story = Ink.Runtime.Story;
using Path = System.IO.Path;

static class Program
{
    static string fixtures, output;
    static int failures;
    static bool oldScoreValue = true;
    static void Log(string kind, object data) => Console.WriteLine(JsonSerializer.Serialize(new { kind, data }));
    static void Require(bool ok, string label) {
        Log("assert", new { label, ok });
        if (!ok) { failures++; throw new Exception(label); }
    }
    static void Save(string name, string text) => File.WriteAllText(Path.Combine(output, name), text);
    static Story Compile(string name) {
        var messages = new List<string>();
        var story = new Ink.Compiler(File.ReadAllText(Path.Combine(fixtures, name + ".ink")),
            new Ink.Compiler.Options { sourceFilename = name + ".ink", errorHandler = (m,t) => {
                messages.Add(t + ": " + m); Log("compile-diagnostic", new { name, type = t.ToString(), message = m });
            }}).Compile();
        Require(story != null && !messages.Any(m => m.StartsWith("Error:")), "compile " + name);
        Save(name + ".story.json", story.ToJson());
        return story;
    }
    static Story Fresh(string name, bool diagnosticOnly = false) {
        var s = new Story(Compile(name).ToJson());
        s.onError += (m,t) => {
            Log("runtime-diagnostic", new { name, type = t.ToString(), message = m, diagnosticOnly });
            if (!diagnosticOnly && t == Ink.ErrorType.Error) failures++;
        };
        return s;
    }
    static List<string> Drain(Story s, string label, Action<string,List<string>> sink = null) {
        var lines = new List<string>();
        int budget = 100;
        while (s.canContinue) {
            Require(budget-- > 0, label + " step budget");
            var line = s.Continue(); var tags = s.currentTags.ToList(); lines.Add(line);
            Log("line", new { label, line, tags }); sink?.Invoke(line, tags);
        }
        Log("choices", new { label, choices = s.currentChoices.Select(c => new { c.index, c.text }).ToArray() });
        return lines;
    }
    static object Vars(Story s) => new [] { "knows_bridge", "heard_bridge", "score" }
        .Select(n => new { name = n, value = s.variablesState[n], clrType = s.variablesState[n]?.GetType().FullName }).ToArray();
    static bool Has(Story s, string id) => s.currentChoices.Any(c => c.text.Trim() == id);
    static void Variables() {
        var old = Fresh("variables-old"); Drain(old,"old-checkpoint");
        Require(old.currentChoices.Count == 1, "checkpoint reached");
        old.variablesState["knows_bridge"] = true; old.variablesState["score"] = oldScoreValue;
        Require(old.variablesState["score"] is bool b && b == oldScoreValue, "old explicit bool preserved before save");
        string save = old.state.ToJson(); Save("old.save.json", save);
        var baseline = Fresh("variables-old"); baseline.state.LoadJson(save);
        Require(baseline.variablesState["knows_bridge"] is true && baseline.variablesState["score"] is bool oldScore && oldScore == oldScoreValue,
            "old content reload preserves bool facts");
        baseline.ChooseChoiceIndex(0); Drain(baseline,"old-baseline-after");
        Require(Has(baseline,"bridge_route"),"baseline bridge choice");

        // Direct-load failure is an experimental result, not permission to skip the migration branch.
        try {
            var direct = Fresh("variables-new", diagnosticOnly: true); direct.state.LoadJson(save);
            Log("direct-load-variables", Vars(direct)); Save("direct-loaded.save.json", direct.state.ToJson());
            Require(direct.variablesState["knows_bridge"] == null, "direct old name absent");
            Require(direct.variablesState["heard_bridge"] is false, "direct renamed fact defaults false");
            // Revised after the preserved false-input counterexample: old defaults may be absent.
            using var saveDocument = JsonDocument.Parse(save);
            bool scoreWasSerialized = saveDocument.RootElement.GetProperty("variablesState").TryGetProperty("score", out _);
            Log("serialized-score-presence", new { scoreWasSerialized, oldScoreValue });
            Require(scoreWasSerialized
                ? direct.variablesState["score"] is bool directScore && directScore == oldScoreValue
                : direct.variablesState["score"] is int defaultScore && defaultScore == 0,
                "revised prediction: serialized score preserves bool; omitted score uses new int default");
            // Do not claim pending choice is semantically compatible: report what direct continuation does.
            if (direct.currentChoices.Count > 0) direct.ChooseChoiceIndex(0);
            Drain(direct,"direct-continuation");
        } catch (Exception e) { Log("direct-load-or-continuation-exception", new { type=e.GetType().FullName,e.Message }); }

        // Independent typed export from OLD content; never extract facts from the projected new state.
        var source = Fresh("variables-old"); source.state.LoadJson(save);
        Require(source.variablesState["knows_bridge"] is bool && source.variablesState["score"] is bool,
            "mapping precondition: both old facts bool");
        var candidate = Fresh("variables-new");
        candidate.variablesState["heard_bridge"] = (bool)source.variablesState["knows_bridge"];
        candidate.variablesState["score"] = (bool)source.variablesState["score"] ? 10 : 0;
        candidate.ChoosePathString("migration_resume");
        var lines = Drain(candidate,"semantic-migration"); Log("candidate-variables",Vars(candidate));
        Require(candidate.variablesState["heard_bridge"] is true && candidate.variablesState["score"] is int i && i == (oldScoreValue ? 10 : 0),
            "mapped facts and exact CLR types");
        Require(Has(candidate,"bridge_route") && Has(candidate,"road_route"),"approved reachable choices");
        Require(string.Concat(lines).Contains(oldScoreValue ? "Arithmetic: 11." : "Arithmetic: 1."),"authored arithmetic after mapping");
        Save("candidate.save.json",candidate.state.ToJson());
        var reload = Fresh("variables-new"); reload.state.LoadJson(candidate.state.ToJson());
        Require(reload.variablesState["score"] is int j && j == (oldScoreValue ? 10 : 0) && Has(reload,"bridge_route"),"candidate save reload");
    }
    static string Query(bool equipped, string label) {
        var s=Fresh("query"); int calls=0;
        s.BindExternalFunction("has_rope", new Func<object>(() => { calls++; return equipped; }), false);
        Drain(s,label); Require(s.currentChoices.Count==1,"one query branch");
        Log("query-input",new {label,equipped,calls}); return s.currentChoices[0].text.Trim();
    }
    static string Sequence(string name,string knot) {
        var s=Fresh(name); Drain(s,name+"-seed"); var trace=new List<string>();
        for(int i=0;i<12;i++) {
            s.ChoosePathString(knot);
            var values = Drain(s,name+"-"+i).Select(x => x.Trim()).Where(x => x.Length > 0).ToArray();
            string[] domain = name == "sequence-new-length" ? new[]{"A","B","C","D"} : new[]{"A","B","C"};
            Require(values.Length == 1 && domain.Contains(values[0]), name + " one valid sample at visit " + i);
            trace.Add(values[0]);
        }
        string[] cycleDomain = name == "sequence-new-length" ? new[]{"A","B","C","D"} : new[]{"A","B","C"};
        for (int offset = 0; offset < trace.Count; offset += cycleDomain.Length) {
            var cycle = trace.Skip(offset).Take(cycleDomain.Length).OrderBy(x => x).ToArray();
            Require(cycle.SequenceEqual(cycleDomain), name + " full shuffle cycle covers domain at " + offset);
        }
        Save(name+".final.save.json",s.state.ToJson()); Log("sequence-trace",new {name,trace});
        return JsonSerializer.Serialize(trace);
    }
    static void Inputs() {
        var a=Query(true,"historical-input"); var b=Query(true,"frozen-replay"); var c=Query(false,"current-input");
        Require(a==b && a=="rope_route" && c=="walk_route","query replay needs historical input");
        var original=Sequence("sequence-old","sample");
        Require(original==Sequence("sequence-old","sample"),"same content seed and visit schedule repeat");
        var length=Sequence("sequence-new-length","sample"); var path=Sequence("sequence-new-path","renamed_sample");
        Log("sequence-comparison",new {lengthChanged=original!=length,pathChanged=original!=path,
            note="No assertion that structural change MUST differ for this seed."});
    }
    sealed class Host {
        public int inventory, externalCalls, observers, tags, commands;
        public readonly List<string> plan = new();
        public void Route(bool candidate,string source,string id,int amount) {
            plan.Add(source+":"+id+":"+amount);
            if(!candidate) inventory+=amount; // Deliberately unsafe mock baseline; not a real service.
        }
    }
    static void Effects() {
        foreach(bool candidate in new[]{false,true}) {
            var h=new Host();
            for(int pass=0;pass<2;pass++) {
                var s=Fresh("effects");
                s.BindExternalFunction<string,int>("award",new Action<string,int>((id,n)=> {
                    h.externalCalls++; h.Route(candidate,"external",id,n);
                }),false);
                s.ObserveVariable("reward_seen",(name,value)=> {
                    h.observers++; if(value is true) h.Route(candidate,"observer","bridge.reward.1",10);
                });
                Drain(s,"effects-"+candidate+"-"+pass,(line,tags)=> {
                    foreach(var tag in tags) {
                        if(tag.Trim()!="command:reward:bridge.reward.1:10") throw new Exception("Unknown tag: "+tag);
                        h.tags++; h.Route(candidate,"tag","bridge.reward.1",10);
                    }
                    if(line.Trim().StartsWith("CMD")) {
                        if(line.Trim()!="CMD reward bridge.reward.1 10") throw new Exception("Unknown command");
                        h.commands++; h.Route(candidate,"text","bridge.reward.1",10);
                    }
                });
                Save("effects-"+candidate+"-"+pass+".save.json",s.state.ToJson());
            }
            Log("mock-host",new {candidate,h.inventory,h.externalCalls,h.observers,h.tags,h.commands,h.plan});
            Require(h.externalCalls==2 && h.observers==2 && h.tags==2 && h.commands==2,"all four outlets exercised twice");
            Require(h.inventory==(candidate?0:80),"isolated plan versus intentionally unsafe mock writes");
        }
    }
    static int Main(string[] args) {
        if(args.Length != 2 && !(args.Length == 3 && args[2] == "--old-score-false")) { Console.Error.WriteLine("Usage: NativeHarness FIXTURES NEW_OUTPUT_DIRECTORY [--old-score-false]"); return 2; }
        oldScoreValue = args.Length == 2;
        Log("scenario-input", new { oldScoreValue });
        fixtures=Path.GetFullPath(args[0]); output=Path.GetFullPath(args[1]);
        if(Directory.Exists(output)) throw new Exception("Refusing to overwrite output directory");
        Directory.CreateDirectory(output);
        foreach(var f in Directory.GetFiles(fixtures).OrderBy(x=>x)) Log("input-sha256",new { file=Path.GetFileName(f),sha256=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(f))).ToLowerInvariant() });
        foreach(var group in new (string,Action)[]{("variables",Variables),("inputs",Inputs),("effects",Effects)}) {
            try { group.Item2(); } catch(Exception e) { failures++; Log("group-failed",new {group=group.Item1,type=e.GetType().FullName,e.Message}); }
        }
        Log("summary",new { failures, note="Mock outlet test only; no transactional host integration." }); return failures==0?0:1;
    }
}
