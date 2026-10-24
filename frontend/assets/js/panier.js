import { api, fcfa, media } from "./api.js";
import { mountLayout, updateCartCount } from "./layout.js";
import { cart } from "./cart.js";

mountLayout();
const lines = document.getElementById("lines");
const out = document.getElementById("result");

function render() {
  const items = cart.items();
  lines.innerHTML = items.length ? items.map((i) => `<div class="line-item">
      ${i.image_url ? `<img src="${media(i.image_url)}" alt="">` : "<div></div>"}
      <div><div class="name">${i.name}</div><span class="fine">${fcfa(i.price_xof)} l'unité</span><br>
      <label class="fine">Qté <input type="number" min="0" max="50" value="${i.quantity}" data-id="${i.product_id}" style="width:4rem;margin-left:.3rem"></label></div>
      <strong>${fcfa(i.price_xof * i.quantity)}</strong></div>`).join("") +
      `<div class="totals"><span>Total</span><span>${fcfa(cart.total())}</span></div>`
    : `<p>Votre panier est vide.</p><a class="btn ghost" href="index.html#boutique">Découvrir la boutique</a>`;
  document.getElementById("pay").disabled = !items.length;
}
lines.addEventListener("change", (e) => { if (e.target.dataset.id) { cart.setQty(e.target.dataset.id, +e.target.value); render(); updateCartCount(); } });

document.getElementById("checkout").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    const order = await api.createOrder({
      customer_email: f.get("email"), customer_country: f.get("country"), payment_method: f.get("method"),
      lines: cart.items().map(({ product_id, quantity }) => ({ product_id, quantity })),
    });
    out.innerHTML = `<div class="notice info">Commande <b>${order.id.slice(0, 8)}</b> enregistrée (${fcfa(order.total_xof)}) — statut <b>${order.status}</b>.
      <br><span class="fine">En production, vous seriez redirigé vers la page sécurisée du prestataire de paiement. Simulez sa réponse :</span><br>
      <button type="button" class="btn small" data-s="SUCCEEDED">Paiement accepté</button>
      <button type="button" class="btn ghost small" data-s="FAILED">Paiement refusé</button></div>`;
    out.onclick = async (ev) => {
      const s = ev.target.dataset.s; if (!s) return;
      const r = await api.simulatePsp(order.id, s);
      out.innerHTML = r.status === "PAID"
        ? `<div class="notice ok">Merci ! Commande <b>${r.id.slice(0, 8)}</b> payée. Les artisans préparent votre colis.</div>`
        : `<div class="notice err">Paiement refusé pour la commande ${r.id.slice(0, 8)} : le stock a été libéré.</div>`;
      if (r.status === "PAID") { cart.clear(); render(); updateCartCount(); }
    };
  } catch (err) { out.innerHTML = `<div class="notice err">${err.message}</div>`; }
});
render();
