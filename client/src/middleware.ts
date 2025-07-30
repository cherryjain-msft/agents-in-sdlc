/**
 * Middleware for handling API requests in the Astro application.
 * 
 * This middleware intercepts API requests and forwards them to the Flask backend server,
 * enabling the frontend to communicate with the backend API seamlessly.
 */
import { defineMiddleware } from "astro:middleware";

// Get server URL from environment variable with fallback for local development
const API_SERVER_URL = process.env.API_SERVER_URL || 'http://localhost:5100';

/**
 * Middleware function to handle API request forwarding.
 * 
 * Intercepts requests to `/api/` endpoints and forwards them to the Flask backend server.
 * Non-API requests are passed through to normal Astro handling.
 * 
 * @param {Object} context - The Astro middleware context object
 * @param {Request} context.request - The incoming request
 * @param {Function} next - Function to call the next middleware or route handler
 * @returns {Promise<Response>} The response from either the API server or next handler
 */
export const onRequest = defineMiddleware(async (context, next) => {
  
  // Guard clause: if not an API request, pass through to regular Astro handling
  if (!context.request.url.includes('/api/')) {
    return await next();
  }
  
  const url = new URL(context.request.url);
  const apiPath = url.pathname + url.search;
  
  // Create a new request to the backend server
  const serverRequest = new Request(`${API_SERVER_URL}${apiPath}`, {
    method: context.request.method,
    headers: context.request.headers,
    body: context.request.method !== 'GET' && context.request.method !== 'HEAD' ? 
          await context.request.clone().arrayBuffer() : undefined,
  });
  
  try {
    // Forward the request to the API server
    const response = await fetch(serverRequest);
    const data = await response.arrayBuffer();
    
    // Return the response from the API server
    return new Response(data, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  } catch (error) {
    console.error('Error forwarding request to API:', error);
    return new Response(JSON.stringify({ error: 'Failed to reach API server' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});