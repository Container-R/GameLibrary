"use strict";
// Synthetic game-to-audio queue; no Android or real playback.
const work=[["GAIN",7,2],["USER_PAUSE",7,2],["AUDIO_CONSUME",7,2]];
function run(recheck) {
 let scene=7, request=2, revision=0, desired=false, actual=false, queued=null;
 for(const [event,s,r] of work){
   if(event==="GAIN") {desired=true;queued={scene:s,request:r,revision};}
   if(event==="USER_PAUSE"){desired=false;revision++;}
   if(event==="AUDIO_CONSUME" && queued && queued.scene===scene && queued.request===request
      && (!recheck || (queued.revision===revision&&desired))) actual=true;
 }
 return {scene,request,revision,desired,actual};
}
const result={work,sessionOnly:run(false),revisionAndIntent:run(true)};
if(!result.sessionOnly.actual||result.revisionAndIntent.actual)throw Error("unexpected trace");
console.log(JSON.stringify(result));
