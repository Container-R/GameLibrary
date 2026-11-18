const result=(()=>{function run(mode){
 let live={gear:3,food:4,ore:0,position:0}, trial=null, ledger={}, tokens=0;
 if(mode!=="none")trial=mode==="alias"?live:{gear:live.gear};
 live.gear=9;
 for(let step=0;step<2;step++){live.position++;live.food--;live.ore+=live.gear;}
 if(mode==="coupled")live.food--;
 const resultLive=JSON.parse(JSON.stringify(live));
 const id="week8:trial2:memberA:tier1";
 const awarded=trial && trial.gear===3 ? 5 : 0;
 function settle(){if(mode==="double" || !(id in ledger)){ledger[id]=awarded;tokens+=awarded;}}
 if(trial){settle();({ledger,tokens}=JSON.parse(JSON.stringify({ledger,tokens})));settle();}
 return {live:resultLive,trialGear:trial?.gear??null,tokens};
}
const modes=["none","normal","alias","coupled","double"];
const result=Object.fromEntries(modes.map(k=>[k,run(k)]));
if(JSON.stringify(result.none.live)!==JSON.stringify(result.normal.live)||result.normal.trialGear!==3||result.normal.tokens!==5||result.alias.trialGear!==9||result.coupled.live.food===result.none.live.food||result.double.tokens!==10)throw Error("control failed");
return result;})();
console.log(JSON.stringify(result,null,2));
