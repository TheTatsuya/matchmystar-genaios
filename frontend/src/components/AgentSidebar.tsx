import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { Search, Plus, MoreVertical } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import Sidebar from './Sidebar';
import UserMenu from './UserMenu';
import { AgentDTO } from '../types/agent';

interface AgentSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  agents: AgentDTO[];
  onAgentSelect: (agent: AgentDTO) => void;
  onCreateAgent: () => void;
  onEditAgent: (agent: AgentDTO) => void;
  onDeleteAgent: (agent: AgentDTO) => void;
}

const AgentSidebar: FC<AgentSidebarProps> = ({
  isOpen,
  onClose,
  agents,
  onCreateAgent,
}) => {
  const { theme } = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredAgents, setFilteredAgents] = useState<AgentDTO[]>(agents);

  useEffect(() => {
    if (searchQuery.length < 3) {
      setFilteredAgents(agents);
      return;
    }

    const queryWords = searchQuery.toLowerCase().split(' ');
    const filtered = agents.filter(agent => {
      const agentText = `${agent.name} ${agent.description}`.toLowerCase();
      return queryWords.every(word => agentText.includes(word));
    });
    setFilteredAgents(filtered);
  }, [searchQuery, agents]);

  return (
    <Sidebar isOpen={isOpen} onClose={onClose}>
      {/* Create Agent Button */}
      <div className="p-4">
        <button 
          onClick={onCreateAgent}
          className={`flex items-center justify-center w-full p-3 ${
            theme === 'light'
              ? 'bg-light-secondary-primary text-light-bg hover:bg-light-secondary-secondary'
              : 'bg-dark-secondary-primary text-dark-bg hover:bg-dark-secondary-secondary'
          } rounded-md transition-colors`}>
          <Plus className="h-5 w-5 mr-2" />
          <span>Create Agent</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="px-4 mb-4">
        <div className={`relative ${
          theme === 'light' ? 'bg-light-bg' : 'bg-dark-bg'
        } rounded-md shadow-sm`}>
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className={`h-5 w-5 ${
              theme === 'light' ? 'text-light-text' : 'text-dark-text'
            }`} />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={`block w-full pl-10 pr-3 py-2 border ${
              theme === 'light'
                ? 'border-light-secondary-secondary text-light-text bg-light-bg'
                : 'border-dark-secondary-secondary text-dark-text bg-dark-bg'
            } rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              theme === 'light'
                ? 'focus:ring-light-secondary-primary'
                : 'focus:ring-dark-secondary-primary'
            }`}
            placeholder="Search agents..."
          />
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto px-4">
        {filteredAgents.map((agent) => (
          <div
            key={agent.id}
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('text/plain', JSON.stringify(agent));
            }}
            className={`mb-4 p-4 rounded-lg cursor-move ${
              theme === 'light'
                ? 'bg-light-bg border border-light-secondary-secondary hover:border-light-secondary-primary'
                : 'bg-dark-bg border border-dark-secondary-secondary hover:border-dark-secondary-primary'
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className={`font-medium ${
                  theme === 'light' ? 'text-light-text' : 'text-dark-text'
                }`}>
                  {agent.name}
                </h3>
                <p className={`text-sm mt-1 ${
                  theme === 'light' ? 'text-light-text-secondary' : 'text-dark-text-secondary'
                }`}>
                  {agent.description.length > 100
                    ? `${agent.description.substring(0, 100)}...`
                    : agent.description}
                </p>
              </div>
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: Implement dropdown menu
                  }}
                  className={`p-1 rounded-full hover:bg-opacity-10 ${
                    theme === 'light'
                      ? 'hover:bg-light-secondary-secondary'
                      : 'hover:bg-dark-secondary-secondary'
                  }`}
                >
                  <MoreVertical className={`h-5 w-5 ${
                    theme === 'light' ? 'text-light-text' : 'text-dark-text'
                  }`} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* User Menu */}
      <div className="mt-auto">
        <UserMenu />
      </div>
    </Sidebar>
  );
};

export default AgentSidebar; 