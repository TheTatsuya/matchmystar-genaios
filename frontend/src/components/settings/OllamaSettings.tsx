import { useEffect, useState } from 'react';
import type { ChangeEvent, FC } from 'react';
import { Box, TextField } from '@mui/material';
import { Settings } from '../../contexts/SettingsContext';
import { AIModelGrid } from '../AIModelGrid';
import { AIModel } from '../../services/apiService';
import { ModelConfig } from '../../services/modelService';

interface OllamaSettingsProps {
  settings: Settings;
  onSettingsChange: (data: Partial<Settings>) => void;
  availableModels: AIModel[];
  disabledModelCreate: boolean;
  tooltipMessage: string;
  onModelSelect: (model: AIModel) => void;
  onModelCreate: () => void;
  onModelEdit: (model: ModelConfig) => void;
  onModelDelete: (model: ModelConfig) => void;
}

export const OllamaSettings: FC<OllamaSettingsProps> = ({ 
  settings,
  availableModels,
  disabledModelCreate,
  tooltipMessage,
  onModelSelect,
  onModelCreate,
  onModelEdit,
  onModelDelete,
  onSettingsChange 
}) => {
  const [url, setUrl] = useState<string>(settings.ollama.base_url);
  const handleUrlChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    setUrl(value);
  };
  useEffect(() => {
    onSettingsChange({ ollama: { base_url: url } });
  }, [url]);

  return (
    <>
      <Box>
        <TextField
          fullWidth
          name="ollamaBaseUrl"
          label="Base URL"
          value={url || ''}
          onChange={handleUrlChange}
          placeholder="Enter Ollama base URL"
        />
      </Box>

      <Box>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          Available Models
        </label>
        <AIModelGrid
          selectedModel={settings.model || null}
          models={availableModels}
          onModelSelect={onModelSelect}
          onModelCreate={onModelCreate}
          onModelEdit={onModelEdit}
          onModelDelete={onModelDelete}
          disabledModelCreate={disabledModelCreate}
          tooltipMessage={tooltipMessage}
        />
      </Box>
    </>
  );
}; 