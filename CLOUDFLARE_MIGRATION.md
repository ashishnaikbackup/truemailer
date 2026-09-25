# Cloudflare consolidation status

The Cloudflare Worker has now been connected to the canonical `ashishnaikbackup/truemailer` repository and the consolidated frontend has been deployed successfully.

## Current architecture

- GitHub: `ashishnaikbackup/truemailer` is the single source repository.
- `frontend/`: production website assets.
- `cloudflare/worker.js`: edge proxy for `/verify`, `/status`, and `/health` plus Workers Assets frontend serving.
- Render: `truemailer-api` remains the verification backend at `https://truemailer-api.onrender.com`.
- UptimeRobot: monitors `https://truemailer-api.onrender.com/health` every 5 minutes.
- GitHub Actions: `render-keepalive.yml` also pings the Render health endpoint every five minutes with retries.

## Verified production behavior

The consolidated Cloudflare deployment has been manually tested with:

1. A normal Gmail address — DNS/MX/provider/blocklist/disposable checks returned successfully.
2. `test@mailinator.com` — disposable and blocklisted detection returned correctly.
3. A deliberately nonexistent domain — DNS/MX failure and low trust result returned correctly.

The frontend keeps verification results and API errors on the same page instead of navigating back to the start.

## Legacy repositories

`truemailer-blocklist-data` is no longer required by the production API because its useful data has been consolidated into the main repository.

`truemailer-web` should remain available as a rollback/reference copy until the final public production route/custom domain has been confirmed on the consolidated Cloudflare deployment. After that confirmation, archive the repository rather than deleting it immediately.

## Final production checklist

- [x] Main repository contains backend, data, frontend and Cloudflare Worker.
- [x] Cloudflare is connected to `main`.
- [x] Workers Assets serves `frontend/`.
- [x] Render API URL remains unchanged.
- [x] Gmail verification tested.
- [x] Disposable/blocklist verification tested.
- [x] Nonexistent-domain verification tested.
- [x] UptimeRobot health monitor is currently Up.
- [x] GitHub keepalive added for Render cold-start protection.
- [ ] Confirm the public/custom domain, if one is used, points to the consolidated deployment.
- [ ] Archive `truemailer-web` after the public route is confirmed stable.
