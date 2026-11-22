import { AudienceType, UserDataFunctions, type RayfinContext } from '@microsoft/fabric-user-data-functions';
import { DATA_AGENT_ID, DATA_AGENT_WORKSPACE_ID } from './agent-config.js';
import { DataAgentMcpClient } from './data-agent-mcp.js';

const udf = new UserDataFunctions();
const MAX_QUESTION_LENGTH = 500;

/**
 * Ask the published Fabric Data Agent through its MCP endpoint.
 *
 * Runs server-side with the app identity (the Fabric app item owner), so no
 * Fabric token reaches the browser and no external proxy is needed.
 */
udf.func(
  'askDataAgent',
  async (ctx: RayfinContext<Record<string, any>, AudienceType.Fabric>, question: string): Promise<string> => {
    const trimmed = question.trim();
    if (!trimmed || trimmed.length > MAX_QUESTION_LENGTH) {
      throw new Error(`Question must be 1-${MAX_QUESTION_LENGTH} characters.`);
    }
    const url =
      `https://api.fabric.microsoft.com/v1/mcp/workspaces/${DATA_AGENT_WORKSPACE_ID}` +
      `/dataagents/${DATA_AGENT_ID}/agent`;
    const client = new DataAgentMcpClient(url, ctx.Tokens.Fabric);
    return client.ask(trimmed);
  },
  [],
);
