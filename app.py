# yorujihanki - 夜の自販機
# 真夜中に立つ自販機のボタンを押すと、飲み物ではなく「今夜の気分」が入った缶が出てくる
# 単一ファイル Flask アプリ。状態は持たず、ロジックとデータはすべてブラウザ側（JS）。
# コレクション（ポケット）はブラウザの localStorage にのみ保存される。
#
# Unit 1: スタイル（CSS）
# Unit 2: スクリプト（JS: 缶データ・抽選・演出・ポケット）
# Unit 3: ページ本体（HTML テンプレート）
# Unit 4: ルーティング

from flask import Flask, render_template_string

app = Flask(__name__)

# Unit 1: スタイル
CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Hiragino Maru Gothic ProN", "Hiragino Sans", "Noto Sans JP", sans-serif;
  background: linear-gradient(180deg, #05081a 0%, #0a1030 55%, #131a3d 100%);
  color: #e8ecff;
  min-height: 100vh;
  padding: 24px 12px 48px;
}
.stars {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    radial-gradient(2px 2px at 12% 18%, #ffffffcc, transparent),
    radial-gradient(1.5px 1.5px at 32% 8%, #ffffff99, transparent),
    radial-gradient(2px 2px at 55% 22%, #ffffffb3, transparent),
    radial-gradient(1.5px 1.5px at 74% 12%, #ffffff80, transparent),
    radial-gradient(2px 2px at 88% 28%, #ffffffcc, transparent),
    radial-gradient(1.5px 1.5px at 44% 34%, #ffffff66, transparent),
    radial-gradient(1.5px 1.5px at 66% 40%, #ffffff59, transparent),
    radial-gradient(2px 2px at 22% 44%, #ffffff73, transparent);
}
.moon {
  position: fixed; top: 22px; right: 26px; width: 46px; height: 46px; z-index: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 38%, #fffbe8, #f5e6b8 70%, #e8d391);
  box-shadow: 0 0 32px 8px rgba(245, 230, 184, 0.35);
}
.wrap { position: relative; z-index: 1; max-width: 480px; margin: 0 auto; }
header { text-align: center; margin-bottom: 18px; }
h1 { font-size: 30px; letter-spacing: 0.25em; color: #cfe0ff; text-shadow: 0 0 18px rgba(140, 170, 255, 0.65); }
.sub { margin-top: 6px; font-size: 13px; color: #9fb0dd; }
.machine {
  background: linear-gradient(160deg, #26336b, #141d42 70%);
  border: 2px solid #46579e;
  border-radius: 18px;
  padding: 16px 16px 14px;
  box-shadow: 0 0 0 4px #0a0f2b, 0 0 42px rgba(80, 110, 220, 0.35), inset 0 0 24px rgba(0,0,0,0.45);
}
.machine.shaking { animation: shake 0.55s ease-in-out; }
@keyframes shake {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  15% { transform: translateX(-7px) rotate(-1.2deg); }
  30% { transform: translateX(6px) rotate(1.1deg); }
  45% { transform: translateX(-6px) rotate(-1deg); }
  60% { transform: translateX(5px) rotate(0.9deg); }
  75% { transform: translateX(-4px) rotate(-0.6deg); }
  90% { transform: translateX(3px) rotate(0.4deg); }
}
.window {
  background: linear-gradient(180deg, #0a1233, #060a22);
  border: 1px solid #3b4c8f; border-radius: 10px;
  padding: 10px 8px; display: flex; justify-content: space-around; align-items: flex-end;
  box-shadow: inset 0 0 18px rgba(90, 130, 255, 0.25);
  min-height: 86px;
}
.sample { text-align: center; }
.sample .mini-can {
  width: 30px; height: 46px; margin: 0 auto 4px; border-radius: 6px 6px 8px 8px;
  border: 1px solid rgba(255,255,255,0.45);
  box-shadow: inset 0 6px 6px rgba(255,255,255,0.35), inset 0 -8px 8px rgba(0,0,0,0.25);
}
.sample .cap { font-size: 10px; color: #aebadd; }
.buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 14px; }
.flavor-btn {
  border: none; border-radius: 10px; padding: 10px 2px; cursor: pointer;
  font-size: 15px; font-weight: bold; color: #101736;
  box-shadow: 0 3px 0 rgba(0,0,0,0.45), 0 0 12px rgba(255,255,255,0.12);
  transition: transform 0.08s, box-shadow 0.08s, opacity 0.2s;
}
.flavor-btn:active { transform: translateY(2px); box-shadow: 0 1px 0 rgba(0,0,0,0.45); }
.flavor-btn:disabled { opacity: 0.45; cursor: default; }
.btn-amai { background: linear-gradient(180deg, #ffc2d1, #ff9eb5); }
.btn-nigai { background: linear-gradient(180deg, #d3ab7d, #b08968); }
.btn-karai { background: linear-gradient(180deg, #ff9d7a, #ff6b4a); }
.btn-shizuka { background: linear-gradient(180deg, #bcd9ea, #7fb3d5); }
.message { min-height: 24px; text-align: center; margin-top: 12px; font-size: 14px; color: #ffd76a; }
.slot {
  margin-top: 6px; height: 108px; border-radius: 10px; position: relative; overflow: hidden;
  background: linear-gradient(180deg, #04061a, #0a0f2c);
  border: 1px solid #33427c;
  box-shadow: inset 0 10px 18px rgba(0,0,0,0.8);
  display: flex; align-items: flex-end; justify-content: center;
}
.slot::before {
  content: "とりだし口"; position: absolute; top: 6px; left: 10px;
  font-size: 10px; color: #5f6fa8; letter-spacing: 0.2em;
}
.can {
  width: 52px; height: 78px; border-radius: 9px 9px 11px 11px; position: relative;
  border: 1px solid rgba(255,255,255,0.55);
  box-shadow: inset 0 8px 8px rgba(255,255,255,0.4), inset 0 -10px 10px rgba(0,0,0,0.3), 0 4px 10px rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
}
.can .can-label {
  writing-mode: vertical-rl; font-size: 11px; font-weight: bold; color: rgba(10, 14, 40, 0.85);
  max-height: 68px; overflow: hidden; letter-spacing: 0.08em;
}
.can.dropping { animation: drop 0.6s cubic-bezier(0.3, 0.6, 0.6, 1); }
@keyframes drop {
  0% { transform: translateY(-110px); opacity: 0; }
  25% { opacity: 1; }
  70% { transform: translateY(2px); }
  85% { transform: translateY(-7px); }
  100% { transform: translateY(0); }
}
.can.stuck { transform: rotate(-24deg) translateY(-16px); }
.can-rare { background: linear-gradient(160deg, #ffe98a, #ffb347 55%, #ff8a5c); }
.can-amai { background: linear-gradient(160deg, #ffd3dd, #ff9eb5); }
.can-nigai { background: linear-gradient(160deg, #e0c096, #b08968); }
.can-karai { background: linear-gradient(160deg, #ffb59d, #ff6b4a); }
.can-shizuka { background: linear-gradient(160deg, #d6e9f5, #7fb3d5); }
.shake-btn {
  display: none; margin: 12px auto 0; border: none; cursor: pointer;
  background: linear-gradient(180deg, #ffe98a, #ffb347); color: #3a2403;
  font-size: 15px; font-weight: bold; padding: 10px 26px; border-radius: 999px;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.shake-btn.show { display: block; }
.result {
  margin-top: 18px; background: rgba(16, 24, 58, 0.85);
  border: 1px solid #3b4c8f; border-radius: 14px; padding: 16px;
  display: none;
}
.result.show { display: block; }
.result .tag {
  display: inline-block; font-size: 11px; padding: 2px 10px; border-radius: 999px;
  background: #26336b; color: #cfe0ff; margin-bottom: 8px;
}
.result .tag.rare { background: #6b4e12; color: #ffe98a; }
.result h2 { font-size: 20px; margin-bottom: 6px; color: #ffffff; }
.result p { font-size: 14px; line-height: 1.7; color: #c6d2f5; }
.pocket-btn {
  margin-top: 12px; border: none; cursor: pointer; width: 100%;
  background: linear-gradient(180deg, #5f74c9, #4256a6); color: #fff;
  font-size: 15px; font-weight: bold; padding: 11px; border-radius: 10px;
  box-shadow: 0 3px 0 rgba(0,0,0,0.4);
}
.pocket-btn:disabled { opacity: 0.5; cursor: default; }
.pocket { margin-top: 22px; }
.pocket h3 { font-size: 16px; color: #cfe0ff; margin-bottom: 8px; }
.pocket ul { list-style: none; }
.pocket li {
  background: rgba(16, 24, 58, 0.7); border: 1px solid #2c3a6e; border-radius: 10px;
  padding: 9px 12px; margin-bottom: 7px; display: flex; align-items: center; gap: 8px;
  font-size: 13px;
}
.pocket .dot { width: 12px; height: 12px; border-radius: 50%; flex: none; border: 1px solid rgba(255,255,255,0.4); }
.pocket .pname { font-weight: bold; color: #fff; }
.pocket .pdate { color: #8fa0cf; font-size: 11px; margin-left: auto; }
.pocket .remove {
  border: none; background: none; color: #ff9eb5; cursor: pointer; font-size: 15px; padding: 2px 4px;
}
.pocket .empty { color: #8fa0cf; font-size: 13px; }
.note { margin-top: 14px; font-size: 11px; color: #7787b5; text-align: center; line-height: 1.7; }
"""

# Unit 2: スクリプト
SCRIPT = """
const POOLS = {
  amai: { label: "あまい", cans: [
    { name: "はちみつ雲の缶", desc: "ふわっと甘い雲をひとくち。今日の疲れが少しだけほどける味。" },
    { name: "いちごミルクの夜", desc: "ほんのりピンクの優しさ。子どもの頃の帰り道みたいな安心感。" },
    { name: "キャラメル星屑", desc: "甘い星が口の中でパチパチはじける、小さなご褒美。" },
    { name: "プリンの月", desc: "まんまるの月にスプーンを入れるような、やわらかい甘さ。" },
    { name: "さとうきびの風", desc: "遠くの島の風が運んできた、素朴でまっすぐな甘さ。" },
    { name: "メープル図書室", desc: "静かな図書室で本を開くときの、落ち着いた甘い香り。" },
    { name: "わたあめの夢", desc: "つかもうとすると溶けてしまう、儚くて甘い夢の味。" },
    { name: "桃のコンポート", desc: "やさしく煮た桃みたいに、気持ちがほんわり温まる。" },
    { name: "バニラの手紙", desc: "封を開けたときのバニラの香り。誰かの優しい言葉みたい。" },
    { name: "黒糖の子守唄", desc: "深い甘さがゆっくり溶けて、眠気をそっと連れてくる。" }
  ]},
  nigai: { label: "にがい", cans: [
    { name: "深煎り珈琲の缶", desc: "ほろ苦さの奥に、静かな決意が隠れている大人の味。" },
    { name: "抹茶の沈黙", desc: "苦いのに清々しい。何も言わない時間の美しさ。" },
    { name: "カカオ85%の真夜中", desc: "甘さをそぎ落とした真夜中の味。思考が冴えてくる。" },
    { name: "よもぎの丘", desc: "春の丘の匂い。少し苦い思い出と一緒に飲み干す。" },
    { name: "炭焼きの煙", desc: "遠くの焚き火の煙みたいな、懐かしい苦み。" },
    { name: "柚子皮のアクセント", desc: "ほんのひとかけらの苦みが、全体を引き締める。" },
    { name: "苦瓜の夏休み", desc: "大人になってから好きになる味。成長の証。" },
    { name: "エスプレッソの雨", desc: "苦い雨が窓を打つ。そんな夜に似合う濃さ。" },
    { name: "薬草の小瓶", desc: "体に効きそうな苦さ。明日の自分への小さな投資。" },
    { name: "焦げパンの端っこ", desc: "ちょっと焦げた端っこが、なぜか一番おいしい。" }
  ]},
  karai: { label: "からい", cans: [
    { name: "唐辛子の星", desc: "小さな星が舌の上で燃える。眠気が吹き飛ぶ辛さ。" },
    { name: "山椒の稲妻", desc: "ピリッと痺れる稲妻。目が覚めるような刺激。" },
    { name: "わさびの滝", desc: "ツーンと鼻に抜ける滝のしぶき。爽快で少し泣ける。" },
    { name: "カレーの火山", desc: "噴火寸前の火山みたいに、体の芯から熱くなる。" },
    { name: "生姜の焚き火", desc: "ポカポカと燃え続ける小さな焚き火。冷えた夜の味方。" },
    { name: "黒胡椒の夜風", desc: "ピリッと辛い夜風が、頬を刺して通り過ぎる。" },
    { name: "ラー油の月食", desc: "赤い月がゆっくり欠けていくような、じわじわくる辛さ。" },
    { name: "ハラペーニョの祭り", desc: "陽気な祭りの熱気。辛いのに楽しい、そんな気分。" },
    { name: "からし菜の春", desc: "ほろ辛い春の味。新しい始まりにちょうどいい刺激。" },
    { name: "七味の七変化", desc: "七つの味がくるくる変わる。最後まで飽きない辛さ。" }
  ]},
  shizuka: { label: "しずか", cans: [
    { name: "深海の缶", desc: "深い海の底の静けさ。音が遠くに消えていく。" },
    { name: "雪の図書館", desc: "雪が音を吸い込む夜の、ページをめくる静寂。" },
    { name: "湖面の月", desc: "波ひとつない湖に映る月。心がすっと静まる。" },
    { name: "苔むした庭", desc: "ずっと昔から静かにそこにある庭の、緑の沈黙。" },
    { name: "星屑の毛布", desc: "星の光を織った毛布。包まれると呼吸が深くなる。" },
    { name: "雨上がりの夜", desc: "雨がやんだばかりの街の、洗われたような静けさ。" },
    { name: "白湯の湯気", desc: "何も足さない、何も引かない。湯気だけがゆらゆら。" },
    { name: "図書室の椅子", desc: "誰もいない図書室の椅子が、静かに順番を待っている。" },
    { name: "砂浜の足跡", desc: "波が足跡を消していく。静かで、少しだけ切ない。" },
    { name: "眠る猫の隣", desc: "すやすや眠る猫の隣の、穏やかで温かい空気。" }
  ]}
};
const RARE = [
  { name: "星空の缶", desc: "開けると星空が広がる。今夜だけの特別な一杯。" },
  { name: "昨日の夢", desc: "昨夜見たはずの夢の続きが入っている。思い出せるかな。" },
  { name: "ねむけの予報", desc: "明日の朝は気持ちよく起きられます。ねむけ予報士の太鼓判つき。" },
  { name: "月の裏側", desc: "誰にも見えない月の裏側の味。想像するしかない。" },
  { name: "花火の余韻", desc: "打ち上げ花火が終わったあとの、耳に残る静かな残響。" },
  { name: "タイムカプセルの手紙", desc: "十年後の自分に宛てた手紙。まだ開けちゃだめ。" },
  { name: "オーロラの欠片", desc: "北の空の光を小さく切り取った、冷たくて美しい一杯。" },
  { name: "午前3時の約束", desc: "こんな時間に起きている人だけが飲める、秘密の味。" }
];
const STUCK_RATE = 0.12;
const POCKET_KEY = "yorujihanki-pocket";
let current = null;
let busy = false;

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function setButtonsEnabled(on) {
  document.querySelectorAll(".flavor-btn").forEach(function (b) { b.disabled = !on; });
}

function showCan(can, flavorKey, isRare, animate) {
  const slot = document.getElementById("slot");
  slot.innerHTML = "";
  const el = document.createElement("div");
  el.className = "can " + (isRare ? "can-rare" : "can-" + flavorKey) + (animate ? " dropping" : "");
  const label = document.createElement("span");
  label.className = "can-label";
  label.textContent = can.name;
  el.appendChild(label);
  slot.appendChild(el);
  return el;
}

function showResult(can, tagText, isRare) {
  current = { name: can.name, flavor: tagText };
  const result = document.getElementById("result");
  const tag = document.getElementById("result-tag");
  tag.textContent = tagText;
  tag.className = "tag" + (isRare ? " rare" : "");
  document.getElementById("result-name").textContent = can.name;
  document.getElementById("result-desc").textContent = can.desc;
  const btn = document.getElementById("pocket-btn");
  btn.disabled = false;
  btn.textContent = "ポケットに入れる";
  result.classList.add("show");
}

function pressFlavor(flavorKey) {
  if (busy) return;
  busy = true;
  setButtonsEnabled(false);
  document.getElementById("shake-btn").classList.remove("show");
  document.getElementById("result").classList.remove("show");
  const msg = document.getElementById("message");
  const pool = POOLS[flavorKey];
  const can = pick(pool.cans);
  msg.textContent = "ガシャン…";
  if (Math.random() < STUCK_RATE) {
    const el = showCan(can, flavorKey, false, false);
    el.classList.add("stuck");
    msg.textContent = "あれ、つかえた… ゆすってみよう。";
    document.getElementById("shake-btn").classList.add("show");
    busy = false;
    return;
  }
  showCan(can, flavorKey, false, true);
  setTimeout(function () {
    msg.textContent = "出てきたよ。";
    showResult(can, pool.label, false);
    setButtonsEnabled(true);
    busy = false;
  }, 620);
}

function shake() {
  if (busy) return;
  busy = true;
  document.getElementById("shake-btn").classList.remove("show");
  const machine = document.getElementById("machine");
  machine.classList.remove("shaking");
  void machine.offsetWidth;
  machine.classList.add("shaking");
  const msg = document.getElementById("message");
  msg.textContent = "ガタガタガタ…！";
  setTimeout(function () {
    const can = pick(RARE);
    showCan(can, null, true, true);
    msg.textContent = "おや、メニューにない缶が出てきた。";
    showResult(can, "レア", true);
    setButtonsEnabled(true);
    busy = false;
  }, 580);
}

function loadPocket() {
  try {
    const raw = localStorage.getItem(POCKET_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr : [];
  } catch (e) { return []; }
}

function savePocket(arr) {
  localStorage.setItem(POCKET_KEY, JSON.stringify(arr));
}

const FLAVOR_COLORS = { "あまい": "#ff9eb5", "にがい": "#b08968", "からい": "#ff6b4a", "しずか": "#7fb3d5", "レア": "#ffb347" };

function renderPocket() {
  const arr = loadPocket();
  document.getElementById("pocket-count").textContent = arr.length;
  const list = document.getElementById("pocket-list");
  list.innerHTML = "";
  if (arr.length === 0) {
    const li = document.createElement("li");
    li.className = "empty";
    li.textContent = "まだ何も入っていません。気に入った缶を入れてみてね。";
    list.appendChild(li);
    return;
  }
  arr.forEach(function (item, idx) {
    const li = document.createElement("li");
    const dot = document.createElement("span");
    dot.className = "dot";
    dot.style.background = FLAVOR_COLORS[item.flavor] || "#ccc";
    const name = document.createElement("span");
    name.className = "pname";
    name.textContent = item.name;
    const fl = document.createElement("span");
    fl.textContent = "（" + item.flavor + "）";
    const date = document.createElement("span");
    date.className = "pdate";
    date.textContent = item.date;
    const rm = document.createElement("button");
    rm.className = "remove";
    rm.textContent = "×";
    rm.title = "ポケットから出す";
    rm.addEventListener("click", function () {
      const a = loadPocket();
      a.splice(idx, 1);
      savePocket(a);
      renderPocket();
    });
    li.appendChild(dot); li.appendChild(name); li.appendChild(fl); li.appendChild(date); li.appendChild(rm);
    list.appendChild(li);
  });
}

function addToPocket() {
  if (!current) return;
  const arr = loadPocket();
  const now = new Date();
  const date = now.getFullYear() + "/" + (now.getMonth() + 1) + "/" + now.getDate();
  arr.unshift({ name: current.name, flavor: current.flavor, date: date });
  savePocket(arr);
  renderPocket();
  const btn = document.getElementById("pocket-btn");
  btn.disabled = true;
  btn.textContent = "ポケットに入れたよ";
}

document.querySelectorAll(".flavor-btn").forEach(function (b) {
  b.addEventListener("click", function () { pressFlavor(b.dataset.flavor); });
});
document.getElementById("shake-btn").addEventListener("click", shake);
document.getElementById("pocket-btn").addEventListener("click", addToPocket);
renderPocket();
"""

# Unit 3: ページ本体
PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>夜の自販機 yorujihanki</title>
<style>{{ css|safe }}</style>
</head>
<body>
<div class="stars"></div>
<div class="moon"></div>
<div class="wrap">
  <header>
    <h1>夜の自販機</h1>
    <p class="sub">真夜中の自販機。出てくるのは飲み物じゃなくて、今夜の気分。</p>
  </header>

  <div class="machine" id="machine">
    <div class="window">
      <div class="sample"><div class="mini-can" style="background:linear-gradient(160deg,#ffd3dd,#ff9eb5)"></div><div class="cap">あまい</div></div>
      <div class="sample"><div class="mini-can" style="background:linear-gradient(160deg,#e0c096,#b08968)"></div><div class="cap">にがい</div></div>
      <div class="sample"><div class="mini-can" style="background:linear-gradient(160deg,#ffb59d,#ff6b4a)"></div><div class="cap">からい</div></div>
      <div class="sample"><div class="mini-can" style="background:linear-gradient(160deg,#d6e9f5,#7fb3d5)"></div><div class="cap">しずか</div></div>
    </div>
    <div class="buttons">
      <button class="flavor-btn btn-amai" data-flavor="amai">あまい</button>
      <button class="flavor-btn btn-nigai" data-flavor="nigai">にがい</button>
      <button class="flavor-btn btn-karai" data-flavor="karai">からい</button>
      <button class="flavor-btn btn-shizuka" data-flavor="shizuka">しずか</button>
    </div>
    <div class="message" id="message">ボタンを押してみて。</div>
    <div class="slot" id="slot"></div>
    <button class="shake-btn" id="shake-btn">ゆする</button>
  </div>

  <div class="result" id="result">
    <span class="tag" id="result-tag"></span>
    <h2 id="result-name"></h2>
    <p id="result-desc"></p>
    <button class="pocket-btn" id="pocket-btn">ポケットに入れる</button>
  </div>

  <div class="pocket">
    <h3>ポケット（<span id="pocket-count">0</span>）</h3>
    <ul id="pocket-list"></ul>
  </div>

  <p class="note">ポケットの中身は、このブラウザの中だけに保存されます（サーバーには送られません）。<br>
  たまに缶がつかえることがあります。ゆすると、メニューにないものが出てくるかも。</p>
</div>
<script>{{ script|safe }}</script>
</body>
</html>
"""


# Unit 4: ルーティング
@app.route("/")
def index():
    return render_template_string(PAGE, css=CSS, script=SCRIPT)


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
