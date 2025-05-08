import { ChangeEvent, FC, useEffect, useState } from 'react';
import { Box, TextField, IconButton, InputAdornment } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { Settings } from '../../contexts/SettingsContext';
import { AIModelGrid } from '../AIModelGrid';
import { AIModel } from '../../services/apiService';
import { ModelConfig } from '../../services/modelService';

interface AzureOpenAISettingsProps {
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

export const AzureOpenAISettings: FC<AzureOpenAISettingsProps> = ({ 
  settings,
  availableModels,
  disabledModelCreate,
  tooltipMessage,
  onSettingsChange,
  onModelSelect,
  onModelCreate,
  onModelEdit,
  onModelDelete
}) => {
  const [showApiKey, setShowApiKey] = useState(false);
  const [url, setUrl] = useState<string>(settings.azureOpenAi.endpoint);
  const [apiKey, setApiKey] = useState<string>(settings.azureOpenAi.api_key);
  const [version, setVersion] = useState<string>(settings.azureOpenAi.api_version);
  const [deploymentName, setDeploymentName] = useState<string>(settings.azureOpenAi.deployment_name);

  const handleUrlChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    setUrl(value.trim());
  };

  const handleApiKeyChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {  
    const { value } = e.target;
    setApiKey(value.trim());
  };

  const handleVersionChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target; 
    setVersion(value.trim());
  };

  const handleDeploymentNameChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { value } = e.target;
    setDeploymentName(value.trim());
  };  

  useEffect(() => {
    onSettingsChange({ azureOpenAi: { endpoint: url, api_key: apiKey, api_version: version, deployment_name: deploymentName } });
  }, [url, apiKey, version, deploymentName]);

  return (
    <>
      <Box>
        <TextField
          fullWidth
          name="azureEndpoint"
          label="Endpoint"
          value={url}
          onChange={handleUrlChange}
          placeholder="Enter Azure OpenAI endpoint"
        />
      </Box>

      <Box>
        <TextField
          fullWidth
          type={showApiKey ? "text" : "password"}
          name="azureApiKey"
          label="API Key"
          value={apiKey}
          onChange={handleApiKeyChange}
          placeholder="Enter Azure OpenAI API key"
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={() => setShowApiKey(!showApiKey)}
                  edge="end"
                >
                  {showApiKey ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Box>

      <Box>
        <TextField
          fullWidth
          name="azureApiVersion"
          label="API Version"
          value={version}
          onChange={handleVersionChange}
          placeholder="Enter Azure OpenAI API version"
        />
      </Box>

      <Box>
        <TextField
          fullWidth
          name="azureDeploymentName"
          label="Deployment Name"
          value={deploymentName}
          onChange={handleDeploymentNameChange}
          placeholder="Enter Azure OpenAI deployment name"
        />
      </Box>

      <Box>
        <label className="block text-sm font-medium text-gray-700 mb-4">
          Available Models
        </label>
        <AIModelGrid
          models={availableModels}
          selectedModel={settings.model}
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