import { api, fcfa, media, CATEGORY_LABELS, COUNTRIES } from "./api.js";
import { mountLayout, updateCartCount } from "./layout.js";
import { cart } from "./cart.js";

mountLayout();
const root = document.getElementById("product");
const crumbs = document.getElementById("crumbs");
const id = new URLSearchParams(location.search).get("id");
api.product(id).then((p) => {
  document.title = `${p.name} — AfricaShop`;
  const cat = CATEGORY_LABELS[p.category] || p.category;
  crumbs.innerHTML = `<a href="index.html">Accueil</a> / <a href="index.html#boutique">${cat}</a> / ${p.name}`;
  root.innerHTML = `<div class="arch">${p.image_url ? `<img src="${media(p.image_url)}" alt="${p.name}">` : `<div class="placeholder">${p.name[0]}</div>`}</div>
    <div><span class="cat-name">${cat}</span><h1>${p.name}</h1>
    <p class="maker">Fabriqué par <strong>${p.vendor_name}</strong> · ${COUNTRIES[p.vendor_country] || p.vendor_country}</p>
    <p class="price">${fcfa(p.price_xof)}</p>
    <p>${p.description}</p>
    <p class="fine">${p.stock > 0 ? `${p.stock} pièces disponibles` : "Rupture de stock"}</p>
    <div class="buy"><div class="qty"><button type="button" data-d="-1" aria-label="Moins">−</button><input id="qty" value="1" inputmode="numeric" aria-label="Quantité"><button type="button" data-d="1" aria-label="Plus">+</button></div>
    <button class="btn" id="add" ${p.stock ? "" : "disabled"}>Ajouter au panier</button></div>
    <div id="msg"></div>
    <details open><summary>Savoir-faire</summary><p>Pièce réalisée à la main par ${p.vendor_name}. Chaque article est unique : de légères variations de couleur et de motif font partie de son caractère.</p></details>
    <details><summary>Livraison</summary><p>Expédition depuis l'Afrique de l'Ouest sous 3 à 5 jours ouvrés ; livraison internationale suivie.</p></details>
    <details><summary>Paiement sécurisé</summary><p>Mobile Money ou carte bancaire via un prestataire certifié : AfricaShop ne voit jamais vos données de carte.</p></details></div>`;
  const qty = document.getElementById("qty");
  root.querySelector(".qty").addEventListener("click", (e) => {
    const d = +e.target.dataset.d || 0; qty.value = Math.min(Math.max(1, +qty.value + d), Math.max(1, p.stock));
  });
  document.getElementById("add").onclick = () => {
    cart.add(p, Math.max(1, +qty.value || 1)); updateCartCount();
    document.getElementById("msg").innerHTML = `<div class="notice ok">Ajouté au panier. <a href="panier.html">Voir le panier</a></div>`;
  };
}).catch((e) => { root.innerHTML = `<div class="notice err">${e.message}</div>`; });
