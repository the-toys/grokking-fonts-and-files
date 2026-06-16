// Shared behavior: sidebar build + active state, progress (localStorage),
// copy-to-clipboard, and "mark complete" buttons.

const MODULES = [
  { n: 1, file: "01-sfnt-container.html", title: "The sfnt container", q: "How is a font file laid out?" },
  { n: 2, file: "02-cmap-glyphs.html", title: "cmap & glyph IDs", q: "How does a character become a glyph?" },
  { n: 3, file: "03-outlines.html", title: "Outlines", q: "How is a glyph drawn?" },
  { n: 4, file: "04-metrics.html", title: "Metrics & the em", q: "What makes text line up?" },
  { n: 5, file: "05-families.html", title: "Identity & families", q: "How do files become a family?" },
  { n: 6, file: "06-shaping.html", title: "Shaping & layout", q: "How do glyphs combine & move?" },
  { n: 7, file: "07-packaging.html", title: "Packaging & frontiers", q: "Collections, variable, web fonts" },
];

const KEY = "font-tutorial-progress";
const progress = () => JSON.parse(localStorage.getItem(KEY) || "{}");
const saveProgress = (p) => localStorage.setItem(KEY, JSON.stringify(p));

function inModules() { return location.pathname.includes("/modules/"); }
function prefix() { return inModules() ? "" : "modules/"; }

function buildSidebar() {
  const el = document.getElementById("sidebar");
  if (!el) return;
  const here = location.pathname.split("/").pop();
  const done = progress();
  const links = MODULES.map(m => {
    const active = here === m.file ? " active" : "";
    const isdone = done[m.n] ? " done" : "";
    return `<li><a class="mod${active}${isdone}" href="${prefix()}${m.file}">
      <span class="num">${String(m.n).padStart(2, "0")}</span>
      <span class="lbl">${m.title}</span></a></li>`;
  }).join("");
  const home = inModules() ? "../index.html" : "index.html";
  el.innerHTML = `
    <p class="brand"><a href="${home}">Grokking Fonts &amp; Files</a></p>
    <p class="tagline">A hands-on tour of OpenType</p>
    <ol>${links}</ol>
    <button class="reset" id="reset-progress">reset progress</button>`;
  document.getElementById("reset-progress").onclick = () => {
    if (confirm("Clear all progress?")) { localStorage.removeItem(KEY); location.reload(); }
  };
}

function wireCopy() {
  document.querySelectorAll("pre").forEach(pre => {
    if (pre.querySelector(".copy")) return;
    const b = document.createElement("button");
    b.className = "copy"; b.textContent = "copy";
    b.onclick = () => {
      const code = pre.querySelector("code") || pre;
      navigator.clipboard.writeText(code.innerText.trim());
      b.textContent = "copied!"; setTimeout(() => b.textContent = "copy", 1200);
    };
    pre.appendChild(b);
  });
}

function wireComplete() {
  const btn = document.getElementById("mark-complete");
  if (!btn) return;
  const n = Number(btn.dataset.module);
  const refresh = () => {
    const done = progress()[n];
    btn.classList.toggle("done", !!done);
    btn.textContent = done ? "✓ Module complete" : "Mark module complete";
  };
  btn.onclick = () => {
    const p = progress(); p[n] = !p[n]; saveProgress(p); refresh(); buildSidebar();
  };
  refresh();
}

document.addEventListener("DOMContentLoaded", () => {
  buildSidebar(); wireCopy(); wireComplete();
});
