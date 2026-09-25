const API_ORIGIN = "https://truemailer-api.onrender.com";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,HEAD,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-API-Key"
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    // API routes stay on the existing Render backend.
    if (url.pathname === "/verify" || url.pathname === "/status" || url.pathname === "/health") {
      const target = new URL(API_ORIGIN + url.pathname + url.search);
      const headers = new Headers(request.headers);
      headers.delete("host");

      const response = await fetch(new Request(target.toString(), {
        method: request.method,
        headers,
        body: request.method === "GET" || request.method === "HEAD" ? undefined : request.body,
        redirect: "follow"
      }));

      const out = new Response(response.body, response);
      for (const [key, value] of Object.entries(corsHeaders())) out.headers.set(key, value);
      return out;
    }

    // When Cloudflare Workers Assets is enabled, serve the frontend from
    // the same repository. This keeps the migration reversible: the current
    // production Worker can be switched only after the new deployment is tested.
    if (env.ASSETS) return env.ASSETS.fetch(request);

    return new Response("Truemailer edge is running. Configure Workers Assets to serve the frontend.", {
      status: 200,
      headers: { "content-type": "text/plain; charset=utf-8" }
    });
  }
};
