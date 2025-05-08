import { useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSettings } from '../contexts/SettingsContext';

export const useLogout = () => {
  const { logout: authLogout } = useAuth();
  const { updateSettings } = useSettings();

  const logout = useCallback(() => {
    // Clear settings first
    updateSettings({
      openAi: { api_key: '' },
      azureOpenAi: {
        endpoint: '',
        api_key: '',
        api_version: '',
        deployment_name: '',
      },
      ollama: { base_url: '' },
      model: null,
      ai_provider: 'openai',
    });

    // Then perform auth logout which handles other cleanup
    authLogout();
  }, [authLogout, updateSettings]);

  return { logout };
}; 