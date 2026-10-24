import { api, fcfa, media, CATEGORY_LABELS, COUNTRIES } from "./api.js";
import { mountLayout } from "./layout.js";

mountLayout();
const sel = document.getElementById("vendor_id");
const msg = document.getElementById("msg");
document.getElementById("category").innerHTML = Object.entries(CATEGORY_LABELS).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
document.getElementById("vcountry").innerHTML = ["SN", "CI", "ML", "BF", "GH", "NG"].map((c) => `<option value="${c}">${COUNTRIES[c]}</option>`).join("");

async function loadVendors() {
  const vs = await api.vendors();
  sel.innerHTML = vs.map((v) => `<option value="${v.id}">${v.name} — ${COUNTRIES[v.country] || v.country}</option>`).join("");
}

const preview = document.getElementById("preview");
document.getElementById("photo").addEventListener("change", (e) => {
  const f = e.target.files[0]; preview.innerHTML = f ? `<img src="${URL.createObjectURL(f)}" alt="" style="max-height:160px;border-radius:4px">` : "";
});

document.getElementById("vendor-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    await api.createVendor({ name: f.get("name"), country: f.get("country"), city: f.get("city") });
    e.target.reset(); await loadVendors();
    msg.innerHTML = `<div class="notice ok">Boutique créée : vous pouvez publier votre premier produit.</div>`;
  } catch (err) { msg.innerHTML = `<div class="notice err">${err.message}</div>`; }
});

document.getElementById("product-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const file = f.get("photo");
  try {
    let image_key = "";
    if (file && file.size) {
      if (file.size > 5 * 1024 * 1024) throw new Error("Photo trop lourde (5 Mo maximum)");
      const pre = await api.presign(f.get("vendor_id"), file);   // 1. l'API signe l'autorisation
      await api.upload(pre, file);                                // 2. le navigateur envoie DIRECTEMENT au stockage
      image_key = pre.key;
    }
    const p = await api.createProduct({                           // 3. l'API enregistre le produit
      vendor_id: f.get("vendor_id"), name: f.get("pname"), description: f.get("description"),
      category: f.get("category"), price_xof: +f.get("price"), stock: +f.get("stock"), image_key,
    });
    msg.innerHTML = `<div class="notice ok">« ${p.name} » est en ligne à ${fcfa(p.price_xof)}. <a href="produit.html?id=${p.id}">Voir la fiche</a></div>`;
    e.target.reset(); preview.innerHTML = "";
  } catch (err) { msg.innerHTML = `<div class="notice err">${err.message}</div>`; }
});
loadVendors();
