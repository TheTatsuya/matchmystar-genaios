import { apiService } from './apiService';

export interface ModelConfig {
  id: string;
  name: string;
  model: string;
  provider: string;
  system_prompt: string;
  temperature: number;
  credentials: Record<string, string>;
}

export const modelService = {
  async getPrompt() {
    const response = await apiService.get<{ system_prompt: string }>('/api/llm/model/prompt');

    return response.data?.system_prompt;
  },

  async getModels(): Promise<ModelConfig[]> {
    const response = await apiService.get<ModelConfig[]>('/api/llm/model/configs');
    return response.data;
  },

  async getModel(id: string): Promise<ModelConfig> {
    const response = await apiService.get<ModelConfig>(`/api/llm/model/config/${id}`);
    return response.data;
  },

  async createModel(model: Omit<ModelConfig, 'id'>): Promise<ModelConfig> {
    const response = await apiService.post<ModelConfig>('/api/llm/model/config', model);
    return response.data;
  },

  async updateModel(id: string, model: Partial<ModelConfig>): Promise<ModelConfig> {
    const response = await apiService.patch<ModelConfig>(`/api/llm/model/config/${id}`, model);
    return response.data;
  },

  async deleteModel(id: string): Promise<void> {
    await apiService.delete<void>(`/api/llm/model/config/${id}`);
  }
};
