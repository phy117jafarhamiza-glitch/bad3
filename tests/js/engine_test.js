const { LiveEngine, LM } = require("" + require("path").resolve(__dirname, "../../views") + "/live_component/engine.js");
const ease = x => { x = Math.max(0, Math.min(1, x)); return 10*x**3 - 15*x**4 + 6*x**5; };
function pose(shift, arm) {
  const cx = 320, P = Array.from({length:33}, () => [0,0]);
  P[LM.nose]=[cx,180]; P[LM.l_sh]=[cx-25,220]; P[LM.r_sh]=[cx+25,220]; P[LM.l_hip]=[cx-15,300]; P[LM.r_hip]=[cx+15,300];
  P[LM.l_kn]=[cx-15,360]; P[LM.r_kn]=[cx+15,360]; P[LM.l_an]=[cx-15,420]; P[LM.r_an]=[cx+15,420];
  P[LM.l_el]=[cx-30,265]; P[LM.l_wr]=[cx-30,305];
  const re=[cx+30,265], rw=[cx+30,305], ue=[cx+62,240], uw=[cx+100,262];
  P.forEach(p => p[0]+=shift);
  P[LM.r_el]=[re[0]+(ue[0]-re[0])*arm+shift, re[1]+(ue[1]-re[1])*arm];
  P[LM.r_wr]=[rw[0]+(uw[0]-rw[0])*arm+shift, rw[1]+(uw[1]-rw[1])*arm];
  return P;
}
function sim(eng, rts, contact) {
  const ev=[]; const seen=new Set(); let t=0; eng.start(t);
  while (t < 60 && !eng.done) {
    if (eng.phase==="stimulus" && !seen.has(eng.stimT)) { seen.add(eng.stimT); ev.push(eng.stimT + rts[(ev.length) % rts.length]); }
    let sh=0, arm=0;
    for (const on of ev) { sh += 70*ease((t-on)/0.45) - 70*ease((t-(on+1.2))/0.45); if (contact) arm += ease((t-on)/0.35) - ease((t-(on+0.55))/0.35); }
    const xy = pose(sh, arm).map(p => [p[0]+(Math.random()-0.5)*0.6, p[1]+(Math.random()-0.5)*0.6]);
    eng.update(t, xy); t += 1/30;
  }
}
let fails = 0; const ok = (c, m) => { if (!c) { fails++; console.log("FAIL", m); } };
let e = new LiveEngine({stim:{mode:"four_colors",delay_min:0.8,delay_max:1.2}, n_trials:3, dominant:"right", use_wrist:false, contact:false, posture_ref:{}}, 1);
sim(e, [0.30,0.40,0.25], false);
ok(e.done, "done"); ok(e.trials.length===3, "3 trials");
e.trials.forEach((r,i)=>{ ok(r.flag==="ok", "flag "+r.flag); ok(Math.abs(r.rt-[0.30,0.40,0.25][i])<0.15, "rt "+r.rt); });
e = new LiveEngine({stim:{mode:"single_color",delay_min:0.8,delay_max:1.0}, n_trials:1, dominant:"right", use_wrist:false, contact:false}, 2);
sim(e, [50], false); ok(e.trials[0].flag==="no_response", "no response");
e = new LiveEngine({stim:{mode:"skill_cue",skill:"mixed",delay_min:0.8,delay_max:1.0}, n_trials:2, dominant:"right", use_wrist:true, contact:true,
  posture_ref:{elbow:[110,175,"e"],knee:[90,150,"k"],trunk:[5,40,"t"]}}, 4);
sim(e, [0.3,0.3], true);
ok(e.trials.length===2 && Number.isFinite(e.trials[0].reach) && e.trials[0].reach>0.8, "contact posture "+JSON.stringify(e.trials[0]&&e.trials[0].reach));
for (const m of ["fake_arrow","delayed_arrow","arrows","numbers","sound","coach_cue"]) {
  e = new LiveEngine({stim:{mode:m,delay_min:0.8,delay_max:1.0,fake_prob:1}, n_trials:2, dominant:"right", use_wrist:false, contact:false}, 7);
  sim(e,[0.3],false); ok(e.trials.length===2 && e.trials.every(r=>r.flag==="ok"), "mode "+m+" "+JSON.stringify(e.trials.map(r=>r.flag)));
}
console.log(fails ? "FAILED "+fails : "ALL OK");
process.exit(fails?1:0);
