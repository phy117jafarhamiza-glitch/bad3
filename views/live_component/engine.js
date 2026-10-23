/* محرك البث المباشر (JavaScript) — نسخة مطابقة لـ core/live.py، لا يعتمد على المتصفح فيُختبر بـ node.
   الإحداثيات بالبكسل: xy = مصفوفة 33 نقطة [x, y]. الزمن بالثواني. */
(function (root) {
  const LM = { nose: 0, l_sh: 11, r_sh: 12, l_el: 13, r_el: 14, l_wr: 15, r_wr: 16,
               l_hip: 23, r_hip: 24, l_kn: 25, r_kn: 26, l_an: 27, r_an: 28 };
  const RT_MIN = 0.10, RT_MAX = 1.50;
  const COLORS4 = [["أحمر", "#dc2828"], ["أخضر", "#2ea043"], ["أزرق", "#1e66d0"], ["أصفر", "#f0c814"]];
  const ARROWS = [["يسار", [-1, 0]], ["يمين", [1, 0]], ["أمام", [0, -1]], ["خلف", [0, 1]]];
  const SKILLS = { net_straight: "شبكة مستقيمة", net_cross: "شبكة قطرية", net_lift: "رفع" };

  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
  function median(arr) { const s = arr.slice().sort((a, b) => a - b); const n = s.length; return n ? (n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2) : 0; }

  function angleDeg(a, b, c) {
    const ba = [a[0] - b[0], a[1] - b[1]], bc = [c[0] - b[0], c[1] - b[1]];
    const den = Math.hypot(...ba) * Math.hypot(...bc);
    if (den < 1e-9) return NaN;
    const cos = Math.max(-1, Math.min(1, (ba[0] * bc[0] + ba[1] * bc[1]) / den));
    return Math.acos(cos) * 180 / Math.PI;
  }
  function side(dom) { return dom === "right" ? [LM.r_sh, LM.r_el, LM.r_wr, LM.r_hip] : [LM.l_sh, LM.l_el, LM.l_wr, LM.l_hip]; }

  function postureAt(p, dom) {
    const [sh, el, wr, hip] = side(dom);
    const midSh = mid(p[LM.l_sh], p[LM.r_sh]), midHip = mid(p[LM.l_hip], p[LM.r_hip]);
    const torso = Math.max(1e-6, dist(midSh, midHip));
    const tv = [midSh[0] - midHip[0], midSh[1] - midHip[1]];
    const trunk = Math.atan2(Math.abs(tv[0]), Math.max(1e-9, -tv[1])) * 180 / Math.PI;
    const knees = [angleDeg(p[LM.l_hip], p[LM.l_kn], p[LM.l_an]), angleDeg(p[LM.r_hip], p[LM.r_kn], p[LM.r_an])]
      .filter(Number.isFinite);
    return {
      elbow: angleDeg(p[sh], p[el], p[wr]), shoulder: angleDeg(p[hip], p[sh], p[el]),
      knee: knees.length ? Math.min(...knees) : NaN, trunk,
      reach: dist(p[wr], midHip) / torso, hit_height: (p[hip][1] - p[wr][1]) / torso,
    };
  }

  // يقارن الزوايا بالمدى المرجعي: ref = {elbow:[lo,hi,label], ...}
  function postureStatus(angles, ref, useArm) {
    const out = {};
    for (const key of ["elbow", "shoulder", "knee", "trunk"]) {
      if (!ref[key]) continue;
      if ((key === "elbow" || key === "shoulder") && !useArm) continue;
      const v = angles[key]; if (!Number.isFinite(v)) continue;
      const [lo, hi, label] = ref[key];
      out[key] = { value: v, status: v < lo ? "low" : (v > hi ? "high" : "ok"), label };
    }
    return out;
  }

  function makeStimulus(mode, skill, rnd, opts) {
    opts = opts || {};
    const pick = a => a[Math.floor(rnd() * a.length)];
    if (mode === "single_color") return { label: "لون أخضر", bg: "#2ea043" };
    if (mode === "four_colors") { const [n, c] = pick(COLORS4); return { label: n, bg: c }; }
    if (["arrows", "fake_arrow", "delayed_arrow"].includes(mode)) {
      let [n, d] = pick(ARROWS);
      while (opts.avoid && n === opts.avoid) [n, d] = pick(ARROWS);
      return { label: "سهم " + n, bg: opts.decoy ? "#1e66d0" : "#1e66d0", arrow: d, key: n };
    }
    if (mode === "numbers") { const k = 1 + Math.floor(rnd() * 6); return { label: "منطقة " + k, bg: "#6a1b9a", digit: k }; }
    if (mode === "sound") return { label: "إشارة صوتية + وميض", bg: "#ffffff", sound: true };
    if (mode === "coach_cue") return { label: "تحرّك الآن", bg: "#2ea043" };
    if (mode === "skill_cue") {
      const key = skill === "mixed" ? pick(Object.keys(SKILLS)) : skill;
      const z = 1 + Math.floor(rnd() * 4);
      const arrow = { net_straight: [0, -1], net_cross: [1, -1], net_lift: [0, -1] }[key];
      return { label: SKILLS[key] + " – منطقة " + z, bg: "#1e66d0", arrow, digit: z };
    }
    return { label: "مثير", bg: "#2ea043" };
  }

  function mulberry(seed) { let a = seed >>> 0; return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

  class LiveEngine {
    constructor(cfg, seed) {
      this.cfg = cfg; this.rnd = seed == null ? Math.random : mulberry(seed);
      this.phase = "idle"; this.trials = []; this.stim = null; this.message = "اضغط «ابدأ»";
      this.status = {}; this.angles = {}; this.lastRt = null;
      this.t = []; this.xy = []; this.speed = []; this.torsos = [];
      this.detected = 0; this.total = 0; this.best = null; this.onsetT = null;
    }
    get done() { return this.phase === "done"; }
    start(t) { this.phase = "countdown"; this.p0 = t; this.trials = []; this.message = "استعد"; }
    stop() { this.phase = "done"; this.message = "أُوقفت الجلسة"; }

    _push(t, xy) {
      const midSh = mid(xy[LM.l_sh], xy[LM.r_sh]), midHip = mid(xy[LM.l_hip], xy[LM.r_hip]);
      this.torsos.push(dist(midSh, midHip)); if (this.torsos.length > 90) this.torsos.shift();
      this.t.push(t); this.xy.push(xy);
      if (this.t.length > 600) { this.t.splice(0, 100); this.xy.splice(0, 100); this.speed.splice(0, 100); }
      if (this.t.length < 2) { this.speed.push(0); return; }
      const n = this.t.length, dt = Math.max(1e-3, this.t[n - 1] - this.t[n - 2]);
      const tl = Math.max(1e-6, median(this.torsos));
      const prev = this.xy[n - 2];
      let sp = dist(midHip, mid(prev[LM.l_hip], prev[LM.r_hip])) / dt / tl;
      if (this.cfg.use_wrist) {
        const w = side(this.cfg.dominant)[2];
        sp = Math.max(sp, 0.5 * dist(xy[w], prev[w]) / dt / tl);
      }
      this.speed.push(0.5 * sp + 0.5 * this.speed[n - 2]);
    }

    update(t, xy) {
      this.total++;
      const ok = xy && xy.every(p => Number.isFinite(p[0]) && Number.isFinite(p[1]));
      if (ok) {
        this.detected++; this._push(t, xy);
        this.angles = postureAt(xy, this.cfg.dominant);
        this.status = postureStatus(this.angles, this.cfg.posture_ref || {}, this.cfg.use_wrist || this.cfg.contact);
        if (this.phase === "stimulus" && this.onsetT !== null && this.cfg.contact) {
          const w = side(this.cfg.dominant)[2];
          const d = dist(xy[w], mid(xy[LM.l_hip], xy[LM.r_hip]));
          if (!this.best || d > this.best.d) this.best = { d, xy: xy.map(p => p.slice()), t };
        }
      } else if (this.phase === "waiting" || this.phase === "stimulus") this.message = "لا يظهر اللاعب في الإطار";
      this._advance(t);
      return this.state();
    }

    _advance(t) {
      const c = this.cfg, ph = this.phase;
      if (ph === "countdown") {
        const left = 3 - (t - this.p0); this.message = "ابدأ بعد " + Math.max(0, Math.ceil(left));
        if (left <= 0) this._beginWait(t);
      } else if (ph === "waiting") {
        this.message = "استعد… ثبّت وضع الاستعداد";
        if (t - this.p0 >= this.wait) this._afterWait(t);
      } else if (ph === "cue") {
        if (t - this.p0 >= this.cueLen) this._show(t);
      } else if (ph === "decoy") {
        if (t - this.p0 >= 0.25) this._show(t, this.decoyKey);
      } else if (ph === "stimulus") this._watch(t);
      else if (ph === "rest") {
        if (t - this.p0 >= (c.rest_s || 2)) {
          if (this.trials.length >= c.n_trials) { this.phase = "done"; this.message = "انتهت المجموعة"; } else this._beginWait(t);
        }
      }
    }
    _beginWait(t) {
      const s = this.cfg.stim;
      this.phase = "waiting"; this.p0 = t; this.stim = null;
      this.wait = s.delay_min + this.rnd() * (s.delay_max - s.delay_min);
    }
    _afterWait(t) {
      const s = this.cfg.stim;
      if (s.mode === "delayed_arrow") { this.phase = "cue"; this.p0 = t; this.cueLen = 0.8 + this.rnd() * 0.7;
        this.stim = { label: "تهيّأ", bg: "#f0c814", cue: true }; this.message = "تهيّأ"; return; }
      if (s.mode === "fake_arrow" && this.rnd() < (s.fake_prob == null ? 0.3 : s.fake_prob)) {
        this.stim = makeStimulus("arrows", null, this.rnd); this.decoyKey = this.stim.key;
        this.stim.decoy = true; this.phase = "decoy"; this.p0 = t; this.message = "انتبه…"; return;
      }
      this._show(t);
    }
    _show(t, avoid) {
      const s = this.cfg.stim;
      this.stim = makeStimulus(s.mode, s.skill, this.rnd, { avoid, decoy: false });
      if (avoid) this.stim.bg = "#c62828";
      this.phase = "stimulus"; this.stimT = t; this.p0 = t; this.message = "الآن! " + this.stim.label;
      const base = [];
      for (let i = 0; i < this.t.length; i++) if (this.t[i] >= t - 0.4 && this.t[i] <= t) base.push(this.speed[i]);
      const b = base.length >= 3 ? base : [0];
      const mu = b.reduce((a, x) => a + x, 0) / b.length;
      const sd = Math.sqrt(b.reduce((a, x) => a + (x - mu) ** 2, 0) / b.length);
      this.thr = Math.max(0.4, mu + 4 * sd); this.preMoving = mu > 0.6 * 0.4;
      this.run = 0; this.runStart = null; this.onsetT = null; this.best = null;
    }
    _watch(t) {
      if (this.onsetT === null) {
        const n = this.speed.length;
        if (n && this.speed[n - 1] > this.thr) {
          this.run++; if (this.runStart === null) this.runStart = this.t[n - 1];
          if (this.run >= 3) this.onsetT = this.runStart;
        } else { this.run = 0; this.runStart = null; }
        if (this.onsetT === null && t - this.stimT > RT_MAX) this._finish(t, null);
        else if (this.onsetT !== null && !this.cfg.contact) this._finish(t, this.onsetT);
      } else if (this.cfg.contact && t - this.onsetT > 1.0) this._finish(t, this.onsetT);
    }
    _finish(t, onset) {
      const row = { idx: this.trials.length + 1, t_stim: this.stimT, rt: null, valid: 0, flag: "no_response",
                    speed_peak: Math.max(0, ...this.speed.slice(-30)) };
      if (onset !== null) {
        const rt = onset - this.stimT; row.rt = rt;
        if (this.preMoving) row.flag = "unsteady";
        else if (rt < RT_MIN) row.flag = "anticipation";
        else if (rt > RT_MAX) row.flag = "slow";
        else { row.flag = "ok"; row.valid = 1; }
        this.lastRt = rt;
      }
      if (this.cfg.contact && this.best) {
        Object.assign(row, postureAt(this.best.xy, this.cfg.dominant)); row._xy = this.best.xy;
      }
      this.trials.push(row); this.phase = "rest"; this.p0 = t;
      this.message = row.rt != null ? "زمن الاستجابة " + Math.round(row.rt * 1000) + " م.ث" : "لا استجابة";
    }
    state() {
      return { phase: this.phase, message: this.message, stim: this.stim, lastRt: this.lastRt, nDone: this.trials.length,
               nTrials: this.cfg.n_trials, status: this.status, angles: this.angles,
               detected: this.total ? this.detected / this.total : 0 };
    }
  }
  const api = { LiveEngine, postureAt, postureStatus, makeStimulus, angleDeg, LM };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.BacEngine = api;
})(typeof self !== "undefined" ? self : this);
