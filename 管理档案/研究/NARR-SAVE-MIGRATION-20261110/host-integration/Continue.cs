using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using Ink.Runtime;
class ContinueSaved {
 static int Main(string[] a) { try {
  var s = new Story(File.ReadAllText(a[0]));
  s.onError += (m,t) => { throw new Exception(t+": "+m); };
  s.state.LoadJson(File.ReadAllText(a[1]));
  var before=s.currentChoices.Select(c=>c.text).ToArray();
  if(before.Length!=2 || !before.Contains("bridge_route") || !before.Contains("road_route")) throw new Exception("Unexpected candidate choices");
  if (!(s.variablesState["heard_bridge"] is bool b) || !b || !(s.variablesState["score"] is int score) || score!=int.Parse(a[4])) throw new Exception("Facts/types differ");
  var c=s.currentChoices.Single(x=>x.text==a[2]); s.ChooseChoiceIndex(c.index);
  string text=""; int budget=32; while(s.canContinue) { if(--budget<0) throw new Exception("budget"); text+=s.Continue(); }
  var expected=a[2]=="bridge_route"?"Bridge.":"Road.";
  if(text.Trim()!=expected || s.currentChoices.Count!=0) throw new Exception("Wrong endpoint: "+text);
  File.WriteAllText(a[3],s.state.ToJson());
  Console.WriteLine(JsonSerializer.Serialize(new {before,choice=a[2],text,score,ended=!s.canContinue && s.currentChoices.Count==0})); return 0;
 } catch(Exception e) { Console.Error.WriteLine(e);return 1; } }
}
