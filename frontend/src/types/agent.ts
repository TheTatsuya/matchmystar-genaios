export interface AgentDTO {
  agent_id: string;
  agent_name: string;
  agent_description: string;
  agent_input_schema: {
    type?: string;
    function?: {
      name: string;
      description: string;
      parameters: {
        type: string;
        properties: Record<string, {
          type: string;
          description: string;
        }>;
        required?: string[];
      };
    };
    [key: string]: any;
  };
  is_active:boolean
}


export interface AgentCreate {
  id: string;
  name: string;
  description: string;
  input_parameters: string | Record<string, any>;
  output_parameters?: string | Record<string, any>;
}

export interface Flow {
  agent_id: string;
}

export interface AgentFlowDTO {
  id: string;
  name: string;
  description: string;
  flow: Flow[];
  created_at: string;
  updated_at: string;
}

export interface AgentFlowCreate {
  name: string;
  description: string;
  flow: Flow[];
}

export interface AgentFlowUpdate {
  name: string;
  description: string;
  flow: Flow[];
}

export interface AgentTrace {
  name: string;
  input: {
    content: string;
    [key: string]: any;
  };
  output: {
    content: string;
    additional_kwargs?: {
      tool_calls?: Array<{
        id: string;
        function: {
          arguments: string;
          name: string;
        };
        type: string;
      }>;
    };
    [key: string]: any;
  };
  is_success: boolean;
  id?: string;
  execution_time?: number;
  flow?: Array<{
    id?: string;
    name: string;
    input: any;
    output: any;
    execution_time?: number;
    is_success: boolean;
  }>;
}
