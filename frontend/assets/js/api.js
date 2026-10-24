// Client HTTP unique : toutes les pages passent par ici.
const CFG = window.AFRICASHOP_CONFIG || { API_BASE: "" };

export const fcfa = (n) => new Intl.NumberFormat("fr-FR").format(n) + " FCFA";
export const media = (url) => (!url ? "" : /^(https?:|data:)/.test(url) ? url : CFG.API_BASE + url);
export const COUNTRIES = { SN: "Sénégal", CI: "Côte d'Ivoire", ML: "Mali", BF: "Burkina Faso", GH: "Ghana", NG: "Nigeria", FR: "France", US: "États-Unis" };
export const CATEGORY_LABELS = { vetements: "Vêtements", artisanat: "Artisanat", cosmetiques: "Cosmétiques naturels", epicerie: "Épicerie fine", maison: "Maison" };

async function request(method, path, body, headers = {}) {
  const res = await fetch(CFG.API_BASE + path, {
    method,
    headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...authHeader(), ...headers },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.detail?.toString?.() || `Erreur ${res.status}`);
  return data;
}

// Phase 2 (Cognito) : le jeton d'accès est stocké par la page de connexion.
function authHeader() {
  const t = sessionStorage.getItem("africashop.token");
  return t ? { Authorization: `Bearer ${t}` } : {};
}

const http = {
  info: () => request("GET", "/api/info"),
  products: (params) => request("GET", "/api/products?" + new URLSearchParams(params)),
  product: (id) => request("GET", `/api/products/${id}`),
  vendors: () => request("GET", "/api/vendors"),
  createVendor: (v) => request("POST", "/api/vendors", v),
  createProduct: (p) => request("POST", "/api/products", p),
  presign: (vendorId, file) => request("POST", `/api/uploads/presign?vendor_id=${vendorId}`, { filename: file.name, content_type: file.type }),
  createOrder: (o) => request("POST", "/api/orders", o),
  order: (id) => request("GET", `/api/orders/${id}`),
  simulatePsp: (orderId, status) => request("POST", "/api/payments/webhook",
    { order_id: orderId, psp_reference: "SIM-" + Date.now(), status }, { "X-PSP-Signature": CFG.PSP_DEMO_SECRET }),
  // Upload DIRECT vers S3 (ou vers l'API en local) avec l'URL pré-signée
  upload: async (pre, file) => {
    const url = pre.upload_url.startsWith("http") ? pre.upload_url : CFG.API_BASE + pre.upload_url;
    const res = await fetch(url, { method: pre.method, headers: pre.headers, body: file });
    if (!res.ok) throw new Error(`Upload refusé (${res.status})`);
  },
};

// Sélection du mode : "simulation" (navigateur seul), "api" (backend), "auto" (API si joignable, sinon simulation)
import { mock } from "./mock.js";
let chosen;
async function backend() {
  if (chosen) return chosen;
  const mode = CFG.MODE || "auto";
  if (mode === "simulation") return (chosen = mock);
  if (mode === "api") return (chosen = http);
  try { await http.info(); chosen = http; } catch { chosen = mock; }
  return chosen;
}
export const api = new Proxy({}, { get: (_, name) => async (...args) => (await backend())[name](...args) });
