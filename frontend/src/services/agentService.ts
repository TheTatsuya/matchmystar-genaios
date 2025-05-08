import { AgentDTO, AgentCreate, AgentFlowDTO, AgentFlowCreate, AgentFlowUpdate } from '../types/agent';
import { apiService } from './apiService';

interface ActiveAgentsResponse {
  count_active_connections: number;
  active_connections: AgentDTO[];
}

export const agentService = {
  async getAgents(): Promise<AgentDTO[]> {
    const response = await apiService.get<AgentDTO[]>('/api/agents');
    return response.data;
  },

  async getActiveAgents(query: Record<string, string>): Promise<ActiveAgentsResponse> {
    const response = await apiService.get<ActiveAgentsResponse>('/api/agents/active', { params: query });
    return response.data;
  },

  async getAgent(id: string): Promise<AgentDTO> {
    const response = await apiService.get<AgentDTO>(`/api/agents/${id}`);
    return response.data;
  },

  async createAgent(agent: AgentCreate): Promise<AgentDTO> {
    const response = await apiService.post<AgentDTO>('/api/agents/register', agent);
    return response.data;
  },

  async deleteAgent(id: string): Promise<void> {
    await apiService.delete<void>(`/api/agents/${id}`);
  },

  async getAgentFlows(): Promise<AgentFlowDTO[]> {
    const response = await apiService.get<AgentFlowDTO[]>('/api/agentflows/');
    return response.data;
  },

  async getAgentFlow(id: string): Promise<AgentFlowDTO> {
    const response = await apiService.get<AgentFlowDTO>(`/api/agentflows/${id}`);
    return response.data;
  },

  async createAgentFlow(flow: AgentFlowCreate): Promise<AgentFlowDTO> {
    const response = await apiService.post<AgentFlowDTO>('/api/agentflows/register-flow', flow);
    return response.data;
  },

  async updateAgentFlow(id: string, flow: AgentFlowUpdate): Promise<void> {
    await apiService.patch<void>(`/api/agentflows/${id}`, flow);
  },

  async deleteAgentFlow(id: string): Promise<void> {
    await apiService.delete<void>(`/api/agentflows/${id}`);
  },
};
