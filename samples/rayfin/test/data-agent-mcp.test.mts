// Runs with Node 22.18+ (type stripping): node --test samples/rayfin/test/
import assert from 'node:assert/strict';
import http from 'node:http';
import { test } from 'node:test';
import { DataAgentMcpClient } from '../functions/data-agent-mcp.ts';

function mockServer(handler: (method: string, body: any) => { status?: number; type: string; body: string }) {
  const seen: { method: string; auth?: string; session?: string }[] = [];
  const server = http.createServer(async (req, res) => {
    let raw = '';
    for await (const chunk of req) raw += chunk;
    const body = JSON.parse(raw);
    seen.push({ method: body.method, auth: req.headers.authorization, session: req.headers['mcp-session-id'] as string });
    const reply = handler(body.method, body);
    res.writeHead(reply.status ?? 200, { 'Content-Type': reply.type, 'Mcp-Session-Id': 's-1' });
    res.end(reply.body);
  });
  return { server, seen };
}

const json = (id: number, result: unknown) => JSON.stringify({ jsonrpc: '2.0', id, result });

test('performs initialize -> tools/list -> tools/call with SSE answer', async () => {
  const { server, seen } = mockServer((method, body) => {
    if (method === 'notifications/initialized') return { status: 202, type: 'text/plain', body: 'Accepted' };
    if (method === 'initialize') return { type: 'application/json', body: json(body.id, { capabilities: {} }) };
    if (method === 'tools/list') {
      return { type: 'application/json', body: json(body.id, { tools: [{ name: 'agent', inputSchema: { properties: { userQuestion: {} } } }] }) };
    }
    const result = { content: [{ type: 'text', text: `37,948 trips (${body.params.arguments.userQuestion})` }] };
    return { type: 'text/event-stream', body: `event: message\ndata: ${json(body.id, result)}\n\n` };
  });
  await new Promise<void>((resolve) => server.listen(0, resolve));
  const { port } = server.address() as { port: number };
  try {
    const answer = await new DataAgentMcpClient(`http://127.0.0.1:${port}/mcp`, 'token-value').ask('総トリップ数は？');
    assert.equal(answer, '37,948 trips (総トリップ数は？)');
    assert.deepEqual(seen.map((s) => s.method), ['initialize', 'notifications/initialized', 'tools/list', 'tools/call']);
    assert.ok(seen.every((s) => s.auth === 'Bearer token-value'));
    assert.deepEqual(seen.slice(1).map((s) => s.session), ['s-1', 's-1', 's-1']);
  } finally {
    server.close();
  }
});

test('does not echo the HTTP error body', async () => {
  const { server } = mockServer(() => ({ status: 403, type: 'application/json', body: '{"secret":"tenant-detail"}' }));
  await new Promise<void>((resolve) => server.listen(0, resolve));
  const { port } = server.address() as { port: number };
  try {
    await assert.rejects(new DataAgentMcpClient(`http://127.0.0.1:${port}/mcp`, 't').ask('q'), (error: Error) => {
      assert.match(error.message, /HTTP 403/);
      assert.doesNotMatch(error.message, /tenant-detail/);
      return true;
    });
  } finally {
    server.close();
  }
});
