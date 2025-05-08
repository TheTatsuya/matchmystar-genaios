import { useState, useEffect, useCallback } from 'react';
import { apiService, AIModel } from '../services/apiService';
import { useToast } from './useToast';

export const useAIModels = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const fetchModels = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getAIModels();
      setModels(response.data);
    } catch (err) {
      setError('Failed to fetch AI models');
      toast.showError('Failed to fetch AI models');
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchModels();
    
    // Cleanup function
    return () => {
      setLoading(false);
      setError(null);
      setModels([]);
    };
  }, [fetchModels]);

  return {
    models,
    loading,
    error,
    refetch: fetchModels
  };
}; 