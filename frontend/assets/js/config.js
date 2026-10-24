// MODE : "auto" (vraie API si joignable, sinon simulation dans le navigateur)
//        "simulation" (site 100 % statique, ex. S3 seul)  |  "api" (backend obligatoire)
window.AFRICASHOP_CONFIG = {
  MODE: "auto",
  API_BASE: "",                  // "" = même origine (CloudFront /api/* ou FastAPI en local)
  PSP_DEMO_SECRET: "dev-secret"  // simulation PSP uniquement : un vrai secret ne va JAMAIS dans le front
};
