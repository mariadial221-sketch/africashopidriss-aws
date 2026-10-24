// Mode SIMULATION : toute l'API est rejouée dans le navigateur (localStorage).
// Permet d'héberger le site seul sur S3 (aucun serveur) puis de basculer vers la vraie API.
const K = "africashop.sim.v2";
const uid = () => Math.random().toString(16).slice(2, 10) + Date.now().toString(16);
const VENDORS = [["Atelier Soumbédioune", "SN", "Dakar"], ["Coopérative Karité de Koudougou", "BF", "Koudougou"],
  ["Pagnes & Wax Treichville", "CI", "Abidjan"], ["Bogolan de Ségou", "ML", "Ségou"]];
const PRODUCTS = [[0, "Boubou brodé homme", "vetements", 45000, "Bazin riche brodé main, coupe ample."],
  [0, "Panier tressé de Thiès", "artisanat", 12000, "Fibres de rônier, tressage traditionnel."],
  [0, "Café Touba moulu 500 g", "epicerie", 3500, "Café parfumé au poivre de Guinée (djar)."],
  [1, "Beurre de karité brut 250 g", "cosmetiques", 4500, "Non raffiné, coopérative de femmes."],
  [1, "Savon noir au karité", "cosmetiques", 2000, "Saponifié à froid, sans parfum ajouté."],
  [2, "Robe en wax", "vetements", 38000, "Coupe évasée, coton 100 %."],
  [2, "Sac cabas en pagne", "artisanat", 15000, "Doublure coton, anses renforcées."],
  [3, "Plaid bogolan 150x200", "maison", 55000, "Teinture à la boue fermentée, motifs Ségou."],
  [3, "Coussin bogolan", "maison", 9000, "Housse amovible, motif tortue."],
  [0, "Bissap séché 250 g", "epicerie", 2500, "Fleurs d'hibiscus de Kaolack."],
  [1, "Huile de baobab 100 ml", "cosmetiques", 6500, "Pressée à froid, peaux sèches."],
  [2, "Masque Gouro décoratif", "artisanat", 27000, "Bois sculpté, finition patinée."]];

const SLUGS = ["boubou", "panier-thies", "cafe-touba", "karite", "savon-noir", "robe-wax", "cabas-pagne", "plaid-bogolan", "coussin-bogolan", "bissap", "huile-baobab", "masque"];

function db() {
  let s = JSON.parse(localStorage.getItem(K) || "null");
  if (!s) {
    const vendors = VENDORS.map(([name, country, city]) => ({ id: uid(), name, country, city }));
    const products = PRODUCTS.map(([v, name, category, price_xof, description], i) => ({
      id: uid(), vendor_id: vendors[v].id, name, category, price_xof, description, stock: 25, image_url: `assets/img/products/${SLUGS[i]}.svg`, created: i }));
    s = { vendors, products, orders: [] };
    localStorage.setItem(K, JSON.stringify(s));
  }
  return s;
}
const save = (s) => { try { localStorage.setItem(K, JSON.stringify(s)); } catch { throw new Error("Stockage du navigateur plein : photo trop lourde pour la simulation"); } };
const fail = (msg) => { throw new Error(msg); };
const view = (s, p) => { const v = s.vendors.find((x) => x.id === p.vendor_id) || {}; return { ...p, vendor_name: v.name, vendor_country: v.country }; };
const delay = (x) => new Promise((r) => setTimeout(() => r(x), 120));

export const mock = {
  info: () => delay({ env: "simulation", database: "navigateur", storage: "navigateur", events: "aucun", auth: "aucune", instance_id: "aucun serveur", az: "S3 / local" }),
  products: async ({ q = "", category = "", page = 1, size = 12 }) => {
    const s = db(); const ql = q.toLowerCase();
    const all = s.products.filter((p) => (!category || p.category === category) && (!ql || (p.name + p.description).toLowerCase().includes(ql)))
      .sort((a, b) => b.created - a.created);
    return delay({ items: all.slice((page - 1) * size, page * size).map((p) => view(s, p)), total: all.length, page: +page, size: +size });
  },
  product: async (id) => { const s = db(); const p = s.products.find((x) => x.id === id) || fail("Produit introuvable"); return delay(view(s, p)); },
  vendors: async () => delay([...db().vendors].sort((a, b) => a.name.localeCompare(b.name))),
  createVendor: async (v) => { const s = db(); const n = { id: uid(), ...v }; s.vendors.push(n); save(s); return delay(n); },
  createProduct: async (p) => {
    const s = db(); if (!s.vendors.some((v) => v.id === p.vendor_id)) fail("Vendeur introuvable");
    const n = { id: uid(), ...p, image_url: p.image_key || "", created: Date.now() }; delete n.image_key;
    s.products.push(n); save(s); return delay(view(s, n));
  },
  // En simulation, la « clé » de la photo est directement l'image encodée (data URL)
  presign: async () => delay({ upload_url: "", method: "SIM", headers: {}, key: "", public_url: "" }),
  upload: (pre, file) => new Promise((ok, ko) => { const r = new FileReader(); r.onload = () => { pre.key = r.result; ok(); }; r.onerror = ko; r.readAsDataURL(file); }),
  createOrder: async (o) => {
    const s = db(); let total = 0;
    for (const l of o.lines) {
      const p = s.products.find((x) => x.id === l.product_id) || fail("Produit introuvable");
      if (p.stock < l.quantity) fail(`Stock insuffisant pour « ${p.name} »`);
      p.stock -= l.quantity; total += p.price_xof * l.quantity;
    }
    const n = { id: uid(), status: "PENDING_PAYMENT", total_xof: total, payment_method: o.payment_method, lines: o.lines, created_at: new Date().toISOString() };
    s.orders.push(n); save(s); return delay(n);
  },
  order: async (id) => delay(db().orders.find((x) => x.id === id) || fail("Commande introuvable")),
  simulatePsp: async (id, status) => {
    const s = db(); const o = s.orders.find((x) => x.id === id) || fail("Commande introuvable");
    if (o.status === "PENDING_PAYMENT") {
      o.status = status === "SUCCEEDED" ? "PAID" : "PAYMENT_FAILED";
      if (o.status === "PAYMENT_FAILED") o.lines.forEach((l) => { s.products.find((p) => p.id === l.product_id).stock += l.quantity; });
      save(s);
    }
    return delay(o);
  },
  reset: () => localStorage.removeItem(K),
};
