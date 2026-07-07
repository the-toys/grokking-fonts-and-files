// Shared behavior: sidebar build + active state, progress (localStorage),
// copy-to-clipboard, "mark complete" buttons, and the EN/中文 language toggle.
// Chinese pages use the `.zh.html` suffix and share this script.

const ZH = /\.zh\.html$/.test(location.pathname);

const MODULES = [
  { n: 1, file: "01-sfnt-container.html", title: "The sfnt container", zh: "sfnt 容器" },
  { n: 2, file: "02-cmap-glyphs.html", title: "cmap & glyph IDs", zh: "cmap 与字形 ID" },
  { n: 3, file: "03-outlines.html", title: "Outlines", zh: "轮廓" },
  { n: 4, file: "04-metrics.html", title: "Metrics & the em", zh: "度量与 em" },
  { n: 5, file: "05-families.html", title: "Identity & families", zh: "身份与家族" },
  { n: 6, file: "06-shaping.html", title: "Shaping & layout", zh: "整形与布局" },
  { n: 7, file: "07-packaging.html", title: "Packaging & frontiers", zh: "打包与前沿" },
];

const T = ZH ? {
  brand: "吃透字体文件",
  tagline: "动手拆解 OpenType",
  reset: "清除进度",
  confirmReset: "确定要清除全部学习进度吗？",
  copy: "复制", copied: "已复制！",
  markDone: "标记本模块完成", isDone: "✓ 本模块已完成",
  toggleLabel: "EN", toggleTitle: "Switch to English",
} : {
  brand: "Grokking Fonts & Files",
  tagline: "A hands-on tour of OpenType",
  reset: "reset progress",
  confirmReset: "Clear all progress?",
  copy: "copy", copied: "copied!",
  markDone: "Mark module complete", isDone: "✓ Module complete",
  toggleLabel: "中文", toggleTitle: "切换到中文版",
};

// Progress is shared between languages: keyed by module number only.
const KEY = "font-tutorial-progress";
const progress = () => JSON.parse(localStorage.getItem(KEY) || "{}");
const saveProgress = (p) => localStorage.setItem(KEY, JSON.stringify(p));

function localized(file) { return ZH ? file.replace(/\.html$/, ".zh.html") : file; }
function inModules() { return location.pathname.includes("/modules/"); }
function prefix() { return inModules() ? "" : "modules/"; }

function buildSidebar() {
  const el = document.getElementById("sidebar");
  if (!el) return;
  const here = location.pathname.split("/").pop();
  const done = progress();
  const links = MODULES.map(m => {
    const active = here === localized(m.file) ? " active" : "";
    const isdone = done[m.n] ? " done" : "";
    return `<li><a class="mod${active}${isdone}" href="${prefix()}${localized(m.file)}">
      <span class="num">${String(m.n).padStart(2, "0")}</span>
      <span class="lbl">${ZH ? m.zh : m.title}</span></a></li>`;
  }).join("");
  const home = (inModules() ? "../" : "") + localized("index.html");
  el.innerHTML = `
    <p class="brand"><a href="${home}">${T.brand}</a></p>
    <p class="tagline">${T.tagline}</p>
    <ol>${links}</ol>
    <button class="reset" id="reset-progress">${T.reset}</button>`;
  document.getElementById("reset-progress").onclick = () => {
    if (confirm(T.confirmReset)) { localStorage.removeItem(KEY); location.reload(); }
  };
}

function buildLangToggle() {
  const a = document.createElement("a");
  a.className = "lang-toggle";
  const here = location.pathname.split("/").pop() || "index.html";
  a.href = ZH ? here.replace(/\.zh\.html$/, ".html") : here.replace(/\.html$/, ".zh.html");
  a.textContent = T.toggleLabel;
  a.title = T.toggleTitle;
  document.body.appendChild(a);
}

function wireCopy() {
  document.querySelectorAll("pre").forEach(pre => {
    if (pre.querySelector(".copy")) return;
    const b = document.createElement("button");
    b.className = "copy"; b.textContent = T.copy;
    b.onclick = () => {
      const code = pre.querySelector("code") || pre;
      navigator.clipboard.writeText(code.innerText.trim());
      b.textContent = T.copied; setTimeout(() => b.textContent = T.copy, 1200);
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
    btn.textContent = done ? T.isDone : T.markDone;
  };
  btn.onclick = () => {
    const p = progress(); p[n] = !p[n]; saveProgress(p); refresh(); buildSidebar();
  };
  refresh();
}

document.addEventListener("DOMContentLoaded", () => {
  buildSidebar(); buildLangToggle(); wireCopy(); wireComplete();
});
