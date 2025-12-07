// Cloudflare Pages Function - Proxy para SalesQuest API via Tunnel
export async function onRequest(context) {
  const { request, params } = context;
  const url = new URL(request.url);

  // URL do backend via Traefik (HTTPS estável)
  const BACKEND_URL = 'https://vendasvox.agenciacafeonline.com.br';

  // Construir URL backend
  const path = params.catchall ? params.catchall.join('/') : '';
  const backendUrl = `${BACKEND_URL}/api/${path}${url.search}`;

  // CORS Preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400'
      }
    });
  }

  try {
    // Clonar body apenas se necessário
    let body = null;
    if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
      body = await request.arrayBuffer();
    }

    const response = await fetch(backendUrl, {
      method: request.method,
      headers: new Headers(request.headers),
      body: body
    });

    // Retornar resposta com CORS
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: new Headers({
        ...Object.fromEntries(response.headers),
        'Access-Control-Allow-Origin': '*'
      })
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return new Response(
      JSON.stringify({ error: error.message, timestamp: new Date().toISOString() }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  }
}
