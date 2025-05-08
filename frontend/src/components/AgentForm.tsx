import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  IconButton,
  Paper,
  Grid,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { AgentDTO, AgentCreate } from '../types/agent';

interface Parameter {
  name: string;
  value: string;
}

interface AgentFormProps {
  agent?: AgentDTO;
  onSubmit: (data: AgentCreate) => void;
}

export const AgentForm: FC<AgentFormProps> = ({ agent, onSubmit }) => {
  const [name, setName] = useState(agent?.name || '');
  const [description, setDescription] = useState(agent?.description || '');
  const [inputParameters, setInputParameters] = useState<Parameter[]>(
    agent?.input_parameters
      ? Object.entries(agent.input_parameters).map(([name, value]) => ({
          name,
          value: JSON.stringify(value),
        }))
      : [{ name: '', value: '' }]
  );
  const [outputParameters, setOutputParameters] = useState<Parameter[]>(
    agent?.output_parameters
      ? Object.entries(agent.output_parameters).map(([name, value]) => ({
          name,
          value: JSON.stringify(value),
        }))
      : [{ name: '', value: '' }]
  );

  const handleAddParameter = (type: 'input' | 'output') => {
    if (type === 'input') {
      setInputParameters([...inputParameters, { name: '', value: '' }]);
    } else {
      setOutputParameters([...outputParameters, { name: '', value: '' }]);
    }
  };

  const handleRemoveParameter = (type: 'input' | 'output', index: number) => {
    if (type === 'input') {
      setInputParameters(inputParameters.filter((_, i) => i !== index));
    } else {
      setOutputParameters(outputParameters.filter((_, i) => i !== index));
    }
  };

  const handleParameterChange = (
    type: 'input' | 'output',
    index: number,
    field: 'name' | 'value',
    value: string
  ) => {
    if (type === 'input') {
      const newParameters = [...inputParameters];
      newParameters[index][field] = value;
      setInputParameters(newParameters);
    } else {
      const newParameters = [...outputParameters];
      newParameters[index][field] = value;
      setOutputParameters(newParameters);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    const inputParamsObj = inputParameters.reduce((acc, param) => {
      if (param.name) {
        acc[param.name] = JSON.parse(param.value || '{}');
      }
      return acc;
    }, {} as Record<string, any>);

    const outputParamsObj = outputParameters.reduce((acc, param) => {
      if (param.name) {
        acc[param.name] = JSON.parse(param.value || '{}');
      }
      return acc;
    }, {} as Record<string, any>);

    const formData = {
      id: agent?.id,
      name,
      description,
      input_parameters: inputParamsObj,
      output_parameters: outputParamsObj,
    };

    onSubmit(formData);
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={4}
            required
          />
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Input Parameters
            </Typography>
            {inputParameters.map((param, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  label="Name"
                  value={param.name}
                  onChange={(e) =>
                    handleParameterChange('input', index, 'name', e.target.value)
                  }
                />
                <TextField
                  label="Value"
                  value={param.value}
                  onChange={(e) =>
                    handleParameterChange('input', index, 'value', e.target.value)
                  }
                  fullWidth
                />
                <IconButton
                  onClick={() => handleRemoveParameter('input', index)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
            <Button
              startIcon={<AddIcon />}
              onClick={() => handleAddParameter('input')}
            >
              Add Input Parameter
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Output Parameters
            </Typography>
            {outputParameters.map((param, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  label="Name"
                  value={param.name}
                  onChange={(e) =>
                    handleParameterChange('output', index, 'name', e.target.value)
                  }
                />
                <TextField
                  label="Value"
                  value={param.value}
                  onChange={(e) =>
                    handleParameterChange('output', index, 'value', e.target.value)
                  }
                  fullWidth
                />
                <IconButton
                  onClick={() => handleRemoveParameter('output', index)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            ))}
            <Button
              startIcon={<AddIcon />}
              onClick={() => handleAddParameter('output')}
            >
              Add Output Parameter
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Button type="submit" variant="contained" color="primary">
            {agent ? 'Update Agent' : 'Create Agent'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
}; 