import type { FC } from 'react';
import { ResizablePanel } from './ResizablePanel';
import { TraceDetails } from './TraceDetails';

interface TraceDetailsPanelProps {
  trace: {
    id: string;
    name: string;
    status: string;
    startTime: string;
    endTime: string;
    duration: number;
    input: any;
    output: any;
    metadata: any;
  };
}

export const TraceDetailsPanel: FC<TraceDetailsPanelProps> = ({ trace }) => {
  return (
    <ResizablePanel>
      <TraceDetails trace={trace} />
    </ResizablePanel>
  );
}; 