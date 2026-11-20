// Exact integer ray/admission model. Run: node probe.js
// World coordinates are integers in units of 1/32. The viewer is at
// x=-64 and target samples at x=64, so wall-hit y,z are their midpoints.
// All boundary tests below are on twice the wall-hit coordinate.
const aperture = {y: [-16, 32], z: [-32, 32]};
const target = [];
for (let row=0; row<8; row++) for (let col=0; col<4; col++)
  target.push([2+4*row, -12+8*col]);
const cameras = {main: [0,0], side: [-128,0]};
// The door covers from aperture bottom to this y. Half: 8 is the midpoint of [-16,32].
const poses = {closed: 32, half: 8, open: -16};
function clear(camera, pose, sample) {
  const y2 = camera[0]+sample[0], z2 = camera[1]+sample[1];
  return y2>=2*aperture.y[0] && y2<2*aperture.y[1]
      && z2>=2*aperture.z[0] && z2<2*aperture.z[1]
      && y2>=2*poses[pose];
}
// Schedules hold an abstract baked closed/open admission state, not actual engine code.
const schedules = [
  ["closed_idle", "closed", false, false],
  ["opening_just_started", "closed", false, true],
  ["opening_half", "half", false, true],
  ["open_idle", "open", true, true],
  ["closing_half", "half", false, true],
  ["closing_fully_opaque", "closed", false, false],
];
function measure(camera, pose, admitted) {
  const indices=target.flatMap((p,i)=>clear(camera,pose,p)?[i]:[]);
  return {unoccluded_sample_indices:indices, unoccluded:indices.length,
          draw_admissions:Number(admitted), returned_samples:admitted?indices.length:0};
}
const main = Object.fromEntries(schedules.map(([name,pose,bad,good]) =>
  [name,{pose, completion_toggled_or_early_closed:measure(cameras.main,pose,bad),
         early_open_late_close:measure(cameras.main,pose,good)}]));
const side={forced_closed_admission:measure(cameras.side,"half",false),
            conservative_open_admission:measure(cameras.side,"half",true)};
const test = [
  [main.opening_just_started.early_open_late_close,0,1,0],
  [main.opening_half.completion_toggled_or_early_closed,16,0,0],
  [main.opening_half.early_open_late_close,16,1,16],
  [main.open_idle.early_open_late_close,32,1,32],
  [main.closing_half.completion_toggled_or_early_closed,16,0,0],
  [main.closing_half.early_open_late_close,16,1,16],
  [main.closing_fully_opaque.early_open_late_close,0,0,0],
  [side.forced_closed_admission,0,0,0],
  [side.conservative_open_admission,0,1,0]
];
for (const [r,unoccluded,admissions,returned] of test) {
  if (r.unoccluded!==unoccluded || r.draw_admissions!==admissions ||
      r.returned_samples!==returned) throw Error(JSON.stringify(r));
}
const result={scope:"exact integer sight rays plus authored closed/open admission mask, not engine, raster, rendered pixels, physical door or performance",
              sample_count:target.length, unit:"1/32 world unit", aperture, cameras, poses, target, main, side};
console.log(JSON.stringify(result,null,2));
