import { api, fcfa, media, CATEGORY_LABELS, COUNTRIES } from "./api.js";
import { mountLayout, updateCartCount } from "./layout.js";
import { cart } from "./cart.js";

mountLayout();
const state = { q: "", category: "", page: 1, size: 12 };
const grid = document.getElementById("grid");
const pager = document.getElementById("pager");
const chips = document.getElementById("chips");
const cats = document.getElementById("cats");

cats.innerHTML = Object.entries(CATEGORY_LABELS).map(([k, v]) =>
  `<button class="cat" data-cat="${k}" aria-pressed="false"><img src="assets/img/categories/${k}.svg" alt="" loading="lazy"><span>${v}</span></button>`).join("");
chips.innerHTML = [["", "Tout voir"], ...Object.entries(CATEGORY_LABELS)]
  .map(([k, v]) => `<button class="chip" data-cat="${k}" aria-pressed="${k === ""}">${v}</button>`).join("");

function setCategory(cat) {
  state.category = cat; state.page = 1;
  document.querySelectorAll("[data-cat]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.cat === cat));
  load();
}
chips.addEventListener("click", (e) => { const b = e.target.closest("[data-cat]"); if (b) setCategory(b.dataset.cat); });
cats.addEventListener("click", (e) => {
  const b = e.target.closest("[data-cat]"); if (!b) return;
  setCategory(b.dataset.cat); document.getElementById("boutique").scrollIntoView({ behavior: "smooth" });
});
let t;
document.getElementById("q").addEventListener("input", (e) => {
  clearTimeout(t); t = setTimeout(() => { Object.assign(state, { q: e.target.value, page: 1 }); load(); }, 300);
});

function card(p) {
  const img = p.image_url ? `<img src="${media(p.image_url)}" alt="${p.name}" loading="lazy">` : `<div class="placeholder">${p.name[0]}</div>`;
  return `<article class="card">
    <a class="thumb" href="produit.html?id=${p.id}">${img}<span class="badge">${COUNTRIES[p.vendor_country] || p.vendor_country}</span></a>
    <div class="body"><span class="cat-name">${CATEGORY_LABELS[p.category] || p.category}</span>
      <a class="name" href="produit.html?id=${p.id}" style="text-decoration:none">${p.name}</a>
      <span class="vendor">par ${p.vendor_name}</span>
      <div class="foot"><span class="price">${fcfa(p.price_xof)}</span>
      <button class="btn ghost small" data-add="${p.id}" ${p.stock ? "" : "disabled"}>${p.stock ? "Ajouter" : "Épuisé"}</button></div></div></article>`;
}

let current = [];
grid.addEventListener("click", (e) => {
  const b = e.target.closest("[data-add]"); if (!b) return;
  cart.add(current.find((p) => p.id === b.dataset.add)); updateCartCount();
  b.textContent = "Ajouté ✓"; setTimeout(() => (b.textContent = "Ajouter"), 1200);
});

async function load() {
  grid.setAttribute("aria-busy", "true");
  try {
    const page = await api.products(state);
    current = page.items;
    grid.innerHTML = page.items.length ? page.items.map(card).join("") : "<p>Aucun produit ne correspond à votre recherche.</p>";
    const pages = Math.ceil(page.total / page.size);
    pager.innerHTML = pages > 1 ? Array.from({ length: pages }, (_, i) =>
      `<button class="chip" aria-pressed="${i + 1 === state.page}" data-p="${i + 1}">${i + 1}</button>`).join("") : "";
  } catch (e) { grid.innerHTML = `<div class="notice err">${e.message}</div>`; }
  grid.removeAttribute("aria-busy");
}
pager.addEventListener("click", (e) => { const b = e.target.closest("[data-p]"); if (b) { state.page = +b.dataset.p; load(); } });
load();
