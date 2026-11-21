"use strict";
function fixture(guarded){
  let active=null, placements=[], rev=41, rows=[];
  const proposals=new Map(), receipts=new Map();
  function open(id, roster, deadline){
    const p={id,roster,deadline,phase:"confirming",accepted:new Set()};
    proposals.set(id,p); active=p; rev++;
  }
  function decision(ticket,player,id,op,ts){
    const p=active;
    const requestKey=[ticket,player,id,op].join("/");
    if(guarded&&receipts.has(requestKey))return "replayed "+receipts.get(requestKey);
    if(!p||p.phase!=="confirming")return "not confirming";
    if(guarded&&p.id!==id)return "stale proposal";
    if(ts>=p.deadline)return "deadline";
    if(p.roster[player]!==ticket)return "not member or wrong ticket";
    if(p.accepted.has(player))return "already accepted";
    p.accepted.add(player); rev++;
    if(guarded)receipts.set(requestKey,"accepted:"+p.id);
    if(p.accepted.size===Object.keys(p.roster).length){
      p.phase="ready"; placements.push("allocate:"+p.id);
    }
    return "accepted:"+p.id;
  }
  function timeout(id,ts){
    const p=proposals.get(id);
    if(p!==active || p.phase!=="confirming" || ts<p.deadline)return "no transition";
    p.phase="expired"; rev++; return "expired:"+id;
  }
  function sample(ts,event,outcome){rows.push({ts,event,outcome,active:active.id,phase:active.phase,
    accepted:[...active.accepted].sort(),placements:[...placements],revision:rev});}
  open("P1",{A:"TA",B:"TB"},100);
  sample(90,"A accepts P1; reply lost",decision("TA","A","P1","a1",90));
  sample(100,"B never accepts; expiry",timeout("P1",100));
  open("P2",{A:"TA",C:"TC"},200);
  sample(110,"candidate P2 reuses TA","opened");
  sample(130,"retry same P1 request",decision("TA","A","P1","a1",130));
  sample(140,"stale timer for P1",timeout("P1",140));
  sample(150,"C accepts P2",decision("TC","C","P2","c2",150));
  sample(151,"C duplicates P2",decision("TC","C","P2","c2",151));
  sample(155,"new delayed submission still names P1",decision("TA","A","P1","new-a1",155));
  sample(160,"A accepts P2",decision("TA","A","P2","a2",160));
  sample(161,"A duplicates P2",decision("TA","A","P2","a2",161));
  return rows;
}
const unsafe=fixture(false), guarded=fixture(true);
if(unsafe[5].placements.length!==1||guarded[6].placements.length!==0||
   guarded[7].outcome!=="stale proposal"||guarded[8].placements.length!==1||
   guarded[9].placements.length!==1||guarded[3].outcome!=="replayed accepted:P1"||
   guarded[4].outcome!=="no transition")throw Error("proposal controls");
const incoming=[{ticket:"TA",rev:43,phase:"confirming:P2"},{ticket:"TA",rev:42,phase:"expired:P1"},
 {ticket:"TA",rev:43,phase:"confirming:P2"},{ticket:"TA",rev:42,phase:"expired:P1"}];
let screen=null;
for(const x of incoming)if(!screen||x.rev>screen.rev)screen=x;
const acceptsNew=(t,deadline)=>t<deadline;
const boundary=[199,200,201].map(t=>[t,acceptsNew(t,200)]);
if(screen.phase!=="confirming:P2"||JSON.stringify(boundary)!=="[[199,true],[200,false],[201,false]]")throw Error("boundary");
console.log(JSON.stringify({unsafe,guarded,display:{lastArrival:incoming.at(-1),highestRevision:screen},exclusiveDeadline:boundary},null,2));
