// Cloudflare Pages Function - Proxy para SalesQuest API
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // Montar URL do backend
  const path = url.pathname.replace('/api', '');
  const backendUrl = `http://212.85.23.66:5200/api${path}${url.search}`;

  // OPTIONS para CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': '*',
      }
    });
  }

  try {
    // Fazer requisição ao backend
    const response = await fetch(backendUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });

    // Copiar resposta com CORS
    const newResponse = new Response(response.body, response);
    newResponse.headers.set('Access-Control-Allow-Origin', '*');
    newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    newResponse.headers.set('Access-Control-Allow-Headers', '*');

    return newResponse;
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}
