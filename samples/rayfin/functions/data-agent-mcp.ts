// Minimal MCP (Streamable HTTP) client for a published Fabric Data Agent.
// The endpoint is not a plain REST API: it requires initialize -> tools/list -> tools/call.

const PROTOCOL_VERSION = '2025-03-26';
// The Fabric UDF host aborts invocations at 250 seconds, so stay below it.
const REQUEST_TIMEOUT_MS = 240_000;
const MAX_ANSWER_LENGTH = 4_000;

type JsonRpcResponse = {
  jsonrpc: '2.0';
  id?: number | string;
  result?: Record<string, unknown>;
  error?: { code: number; message: string };
};

type ToolDescriptor = {
  name: string;
  inputSchema?: { properties?: Record<string, unknown> };
};

function parseBody(contentType: string | null, body: string, id: number): JsonRpcResponse {
  if (contentType?.includes('text/event-stream')) {
    const messages = body
      .split(/\r?\n/)
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trim())
      .filter((data) => data.length > 0)
      .map((data) => JSON.parse(data) as JsonRpcResponse);
    const match = messages.find((message) => message.id === id);
    if (!match) {
      throw new Error('MCP response did not contain the requested message.');
    }
    return match;
  }
  return JSON.parse(body) as JsonRpcResponse;
}

export class DataAgentMcpClient {
  private readonly url: string;
  private readonly token: string;
  private sessionId: string | undefined;
  private nextId = 1;

  constructor(url: string, token: string) {
    this.url = url;
    this.token = token;
  }

  private headers(): Record<string, string> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      Accept: 'application/json, text/event-stream',
      'MCP-Protocol-Version': PROTOCOL_VERSION,
    };
    if (this.sessionId) {
      headers['Mcp-Session-Id'] = this.sessionId;
    }
    return headers;
  }

  private async post(payload: Record<string, unknown>): Promise<Response> {
    const response = await fetch(this.url, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    if (!response.ok) {
      // Do not echo the response body: it may contain tenant details.
      throw new Error(`Data Agent MCP request failed with HTTP ${response.status}.`);
    }
    return response;
  }

  private async request(method: string, params: Record<string, unknown>): Promise<Record<string, unknown>> {
    const id = this.nextId++;
    const response = await this.post({ jsonrpc: '2.0', id, method, params });
    this.sessionId = response.headers.get('Mcp-Session-Id') ?? this.sessionId;
    const contentType = response.headers.get('Content-Type')?.toLowerCase() ?? '';
    if (!contentType.includes('application/json') && !contentType.includes('text/event-stream')) {
      throw new Error(`Data Agent MCP returned an unexpected content type for ${method}.`);
    }
    const message = parseBody(contentType, await response.text(), id);
    if (message.error) {
      throw new Error(`Data Agent MCP error ${message.error.code}: ${message.error.message}`);
    }
    return message.result ?? {};
  }

  async ask(question: string): Promise<string> {
    await this.request('initialize', {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: {},
      clientInfo: { name: 'taxi-insights', version: '1.0.0' },
    });
    await this.post({ jsonrpc: '2.0', method: 'notifications/initialized' });

    const listed = await this.request('tools/list', {});
    const tools = (listed['tools'] as ToolDescriptor[] | undefined) ?? [];
    const tool = tools[0];
    if (!tool) {
      throw new Error('The Data Agent MCP server exposed no tools. Is the agent published?');
    }
    const argumentName = Object.keys(tool.inputSchema?.properties ?? {})[0];
    if (!argumentName) {
      throw new Error('The Data Agent tool does not declare a question argument.');
    }

    const called = await this.request('tools/call', {
      name: tool.name,
      arguments: { [argumentName]: question },
    });
    const content = (called['content'] as { type: string; text?: string }[] | undefined) ?? [];
    const answer = content
      .filter((block) => block.type === 'text' && block.text)
      .map((block) => block.text)
      .join('\n')
      .trim();
    if (called['isError'] === true) {
      throw new Error(answer || 'The Data Agent returned an error.');
    }
    if (!answer) {
      return 'The Data Agent returned no text answer.';
    }
    return answer.length > MAX_ANSWER_LENGTH ? `${answer.slice(0, MAX_ANSWER_LENGTH)}…` : answer;
  }
}
