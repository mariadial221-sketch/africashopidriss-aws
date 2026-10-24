// Panier côté navigateur (localStorage). Aucune donnée de paiement n'y est jamais stockée.
const KEY = "africashop.cart";
const read = () => JSON.parse(localStorage.getItem(KEY) || "[]");
const write = (items) => localStorage.setItem(KEY, JSON.stringify(items));

export const cart = {
  items: read,
  count: () => read().reduce((n, i) => n + i.quantity, 0),
  add(product, quantity = 1) {
    const items = read();
    const found = items.find((i) => i.product_id === product.id);
    if (found) found.quantity += quantity;
    else items.push({ product_id: product.id, name: product.name, price_xof: product.price_xof, image_url: product.image_url, quantity });
    write(items);
  },
  setQty(id, q) { write(read().map((i) => (i.product_id === id ? { ...i, quantity: q } : i)).filter((i) => i.quantity > 0)); },
  clear: () => write([]),
  total: () => read().reduce((s, i) => s + i.price_xof * i.quantity, 0),
};
