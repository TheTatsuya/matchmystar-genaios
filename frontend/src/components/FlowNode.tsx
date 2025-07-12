import type { FC } from 'react';
import { useRef, useEffect } from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import { NodeProps, Handle, Position } from 'reactflow';
import { ShieldX, Trash2 } from 'lucide-react';

interface FlowNodeData {
  label: string;
  description: string;
  color: string;
  type: string;
  isActive: boolean;
  flow?: any[];
  onDelete: (nodeId: string) => void;
  isDeletable?: boolean;
}

export const FlowNode: FC<NodeProps<FlowNodeData>> = ({ data, id }) => {
  const nodeRef = useRef<HTMLDivElement>(null);
  const isActive = data.isActive === true || data.isActive === undefined;

  useEffect(() => {
    if (nodeRef.current) {
      const height = nodeRef.current.offsetHeight;
      // Emit height to parent through custom event
      const event = new CustomEvent('nodeHeight', {
        detail: { nodeId: id, height },
      });
      window.dispatchEvent(event);
    }
  }, [id, data.flow]);

  return (
    <Box
      ref={nodeRef}
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        position: 'relative',
      }}
    >
      {data.isDeletable && (
        <IconButton
          size="small"
          onClick={e => {
            e.stopPropagation();
            if (data.onDelete) {
              data.onDelete(id);
            }
          }}
          sx={{
            position: 'absolute',
            top: -10,
            right: -10,
            color: '#c1121f',
            p: 0.5,
          }}
        >
          <Trash2 size={12} />
        </IconButton>
      )}
      <Handle
        type="target"
        position={Position.Top}
        style={{
          top: -13,
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          bottom: -13,
        }}
      />
      <Typography
        variant="subtitle1"
        sx={{
          mb: data.flow ? 0.5 : 0,
          maxWidth: '100%',
          overflowWrap: 'break-word',
          textAlign: 'center',
        }}
      >
        {isActive ? (
          data.label
        ) : (
          <Typography
            component="span"
            sx={{ display: 'flex', gap: 0.5, color: '#c1121f' }}
          >
            <ShieldX /> {data.label}
          </Typography>
        )}
      </Typography>
      {data?.type && (
        <Typography
          variant="caption"
          sx={{
            position: 'absolute',
            top: -8,
            left: -8,
            padding: '0 4px',
            fontSize: 8,
            border: '1px solid #E65100',
            color: '#E65100',
            borderRadius: 2,
          }}
        >
          {data.type}
        </Typography>
      )}
      {data.flow && (
        <Box
          sx={{
            width: '90%',
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5,
            overflow: 'auto',
            py: 0.5,
          }}
        >
          {data.flow.map((step: any, index: number) => (
            <Box
              key={index}
              id={`flow-node-${id}-${index}`}
              onClick={e => {
                e.stopPropagation();
                const event = new CustomEvent('flowStepClick', {
                  detail: { step, nodeId: id },
                });
                window.dispatchEvent(event);
              }}
              sx={{
                maxWidth: '180px',
                wordBreak: 'break-all',
                textAlign: 'center',
                p: 0.5,
                bgcolor: '#fff',
                borderRadius: '4px',
                border: `1px solid ${step.is_success ? '#4CAF50' : '#F44336'}`,
                minHeight: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'grey.100',
                },
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {step.name}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};
