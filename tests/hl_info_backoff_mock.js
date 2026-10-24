// mock-only: HL.post cache / in-flight share / 429 cooldown (extracts the HL object from workspace_app.html)
const fs = require("fs"), s = fs.readFileSync(__dirname + "/../modules/workspace_app.html", "utf8");
const i = s.indexOf("const HL = {q:{}"), j = s.indexOf("\n};", i) + 3;
let calls = 0, mode = "ok"; const store = {};
global.localStorage = {getItem: k => store[k] || null, setItem: (k, v) => store[k] = v};
global.fetch = async () => { calls++; await new Promise(r => setTimeout(r, 20));
  return mode === "429" ? {status: 429, ok: false, headers: {get: () => "7"}} : {status: 200, ok: true, headers: {get: () => null}, json: async () => ({n: calls})}; };
const HL_API = "x", HL_DEX = "xyz", hlCat = () => "", HL = eval("(" + s.slice(i + "const HL = ".length, j - 1) + ")");
(async () => {
  await Promise.all([1,2,3,4,5].map(() => HL.post({type: "l2Book", coin: "A"}))); console.assert(calls === 1, "in-flight share", calls);
  await HL.post({type: "l2Book", coin: "A"}); console.assert(calls === 1, "ttl cache", calls);
  mode = "429"; try { await HL.post({type: "l2Book", coin: "B"}); } catch (e) {} console.assert(calls === 2);
  const c = calls; for (let k = 0; k < 20; k++) { try { await HL.post({type: "l2Book", coin: "C" + k}); } catch (e) {} } console.assert(calls === c, "cooldown blocks fetches", calls - c);
  console.assert(HL.coolUntil() - Date.now() >= 6500, "Retry-After honoured"); console.log("ok, fetches:", calls);
})();
