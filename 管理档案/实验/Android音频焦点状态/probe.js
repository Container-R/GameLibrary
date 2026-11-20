"use strict";
// Synthetic app policy. Request IDs identify incarnations; callbacks below are injected,
// not Android runtime observations. All "gains" in the model are normalized multipliers.
const cases={
 pause_transient:[["enter","A"],["play"],["request",1,"yes"],["loss",1,"temporary"],["pause"],["gain",1]],
 stale_delayed:[["enter","A"],["play"],["request",1,"delay"],["exit"],["enter","B"],["play"],["request",2,"delay"],["gain",1],["gain",2]],
 valid_delayed:[["enter","A"],["play"],["request",1,"delay"],["gain",1]],
 background:[["enter","A"],["play"],["request",1,"yes"],["loss",1,"temporary"],["background"],["gain",1]],
 system_duck:[["enter","A"],["play"],["request",1,"yes"],["os_gain",0.2],["os_gain",1]],
 permanent:[["enter","A"],["play"],["request",1,"yes"],["loss",1,"permanent"],["gain",1],["play"],["request",2,"yes"]],
 mute_keep:[["enter","A"],["play"],["request",1,"yes"],["slider",0],["slider",0.75]],
 mute_abandon:[["enter","A"],["play"],["request",1,"yes"],["slider",0],["gain",1],["slider",0.75],["request",2,"yes"]]
};
function run(events,guard,abandon) {
 let scene=null,foreground=false,intent=false,id=null,focus="none",playing=false,slider=1,osGain=1;
 const retire=()=>{id=null;focus="none";playing=false;};
 return events.map(([event,a,b])=>{
   switch(event) {
     case "enter":scene=a;foreground=true;intent=false;break;
     case "exit":scene=null;foreground=false;intent=false;retire();break;
     case "background":foreground=false;retire();break;
     case "play":intent=true;break;
     case "pause":intent=false;playing=false;break;
     case "request":
       if(!scene||!foreground||!intent)throw Error("invalid test request");
       id=a;focus=b==="yes"?"granted":"pending";playing=focus==="granted";break;
     case "loss":
       if(id!==a)break;
       playing=false;
       if(b==="permanent"){retire();intent=false;}else focus="suspended";
       break;
     case "gain":
       if(!guard){playing=true;break;}
       if(id===a&&(focus==="pending"||focus==="suspended"))focus="granted";
       break;
     case "os_gain":osGain=a;break; // No focus callback injected for this step.
     case "slider":
       slider=a;
       if(a===0&&abandon)retire();
       break;
     default:throw Error(event);
   }
   if(guard)playing=!!scene&&foreground&&intent&&focus==="granted";
   return [event,scene,foreground,intent,id,focus,playing,slider,osGain,playing?slider*osGain:0];
 });
}
const report={scope:"Synthetic app policy, no Android runtime, audio device, callback ordering or measured gain.",fields:["event","scene","foreground","intent","generation","permission","playing","slider","system_gain","modeled_mix"],cases:{}};
for(const [k,v] of Object.entries(cases)){
 report.cases[k]={events:v,naive:run(v,false,k==="mute_abandon"),guarded:run(v,true,k==="mute_abandon")};
}
const h=report.cases;
function at(k,n=-1,p="guarded"){return h[k][p].at(n);}
const playing=(k,n=-1,p="guarded")=>at(k,n,p)[6];
const checks=[
 playing("pause_transient",-1,"naive")&&!playing("pause_transient"),
 playing("stale_delayed",-2,"naive")&&!playing("stale_delayed",-2)&&playing("stale_delayed")&&playing("valid_delayed"),
 playing("background",-1,"naive")&&!playing("background"),
 playing("system_duck",-2)&&at("system_duck",-2)[9]===.2&&at("system_duck")[9]===1,
 playing("permanent",-3,"naive")&&!playing("permanent",-3)&&!playing("permanent",-2)&&playing("permanent"),
 playing("mute_keep",-2)&&at("mute_keep",-2)[5]==="granted"&&at("mute_keep",-2)[9]===0&&at("mute_keep")[9]===.75,
 !playing("mute_abandon",-3)&&!playing("mute_abandon",-2)&&playing("mute_abandon")
];
if(!checks.every(Boolean))throw Error(JSON.stringify(checks));
console.log(JSON.stringify(report));
