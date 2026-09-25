# Cloudflare consolidation plan

The production Cloudflare service should not be switched until the current Render API and UptimeRobot monitor are stable.

## Target architecture

- GitHub: `ashishnaikbackup/truemailer` is the single source repository.
- `frontend/`: production website assets.
- `cloudflare/worker.js`: edge proxy for `/verify`, `/status`, and `/health`.
- Render: `truemailer-api` remains the verification backend at `https://truemailer-api.onrender.com`.
- UptimeRobot: monitor `https://truemailer-api.onrender.com/health` every 5 minutes.

## Cloudflare switch

When ready, configure the existing Cloudflare Worker/Pages deployment to use this repository and deploy the included `wrangler.toml` configuration. It uses Workers Assets to serve `frontend/` and keeps API routes pointed at the existing Render service.

Before switching production:

1. Confirm Render `/health` returns 2xx and UptimeRobot is Up.
2. Preview the new Cloudflare deployment.
3. Test `/`, `/verify`, and `/health`.
4. Test Gmail, a known disposable domain, and a nonexistent domain.
5. Only then switch the production route/domain.
6. Keep `truemailer-web` intact until the production switch has been verified.
7. After verification, `truemailer-web` can be archived rather than immediately deleted.
