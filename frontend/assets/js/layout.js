// En-tête, pied de page et bandeau technique partagés par toutes les pages.
import { api } from "./api.js";
import { cart } from "./cart.js";

const NAV = [["index.html", "Boutique"], ["index.html#histoire", "Nos artisans"], ["vendeur.html", "Espace vendeur"]];
const BAG = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>`;

export function mountLayout() {
  const here = location.pathname.split("/").pop() || "index.html";
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="mode" id="mode">Connexion à l'API…</div>
    <div class="announce">Livraison internationale depuis Dakar · Paiement Wave, Orange Money ou carte bancaire</div>
    <header class="site"><div class="wrap bar">
      <a class="brand" href="index.html"><strong>Africa<span>Shop</span></strong><small>L'artisanat d'Afrique de l'Ouest</small></a>
      <nav class="main" aria-label="Navigation principale">
        ${NAV.map(([h, l]) => `<a href="${h}" ${h === here ? 'aria-current="page"' : ""}>${l}</a>`).join("")}
        <a class="cart-link" href="panier.html" ${here === "panier.html" ? 'aria-current="page"' : ""}>${BAG} Panier <span class="cart-count" id="cart-count">${cart.count()}</span></a>
      </nav></div><div class="kente" aria-hidden="true"></div></header>`);
  document.body.insertAdjacentHTML("beforeend", `
    <footer class="site"><div class="kente" aria-hidden="true"></div><div class="wrap cols">
      <div><h4>AfricaShop</h4><p style="font-size:.92rem;max-width:34ch">Une place de marché qui relie les artisans et commerçants d'Afrique de l'Ouest aux amateurs du monde entier.</p></div>
      <div><h4>Boutique</h4><a href="index.html#boutique">Vêtements</a><a href="index.html#boutique">Artisanat</a><a href="index.html#boutique">Cosmétiques naturels</a><a href="index.html#boutique">Épicerie fine</a></div>
      <div><h4>Vendeurs</h4><a href="vendeur.html">Ouvrir une boutique</a><a href="vendeur.html">Publier un produit</a><a href="index.html#histoire">Notre engagement</a></div>
      <div><h4>Aide</h4><a href="#">Livraison et retours</a><a href="#">Paiement sécurisé</a><a href="#">Contact</a></div>
    </div><div class="wrap legal">© AfricaShop — application de simulation du projet AWS Cloud Foundations / Cloud Architecting. Produits, vendeurs et paiements fictifs. Illustrations originales.</div></footer>`);
  const mode = document.getElementById("mode");
  api.info().then((i) => {
    mode.innerHTML = `Mode <b>${i.env}</b> · base <b>${i.database}</b> · photos <b>${i.storage}</b> · événements <b>${i.events}</b> · auth <b>${i.auth}</b> · servi par <b>${i.instance_id}</b> (${i.az})`;
  }).catch(() => { mode.classList.add("down"); mode.textContent = "API injoignable — vérifiez le backend ou le health check du load balancer."; });
}

export const updateCartCount = () => { const el = document.getElementById("cart-count"); if (el) el.textContent = cart.count(); };
