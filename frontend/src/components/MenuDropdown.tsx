import type { FC } from 'react';
import { Settings, LogOut } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

interface MenuDropdownProps {
  isOpen: boolean;
  onLogout: () => void;
}

const MenuDropdown: FC<MenuDropdownProps> = ({ isOpen, onLogout }) => {
  const { theme } = useTheme();

  if (!isOpen) return null;

  return (
    <div className={`absolute bottom-full right-0 mb-2 w-48 rounded-md shadow-lg ${
      theme === 'light' ? 'bg-white' : 'bg-dark-bg'
    } ring-1 ring-black ring-opacity-5`}>
      <div className="py-1">
        <button
          className={`flex items-center w-full px-4 py-2 text-sm ${
            theme === 'light' ? 'text-light-text hover:bg-gray-100' : 'text-dark-text hover:bg-dark-bgAlt'
          }`}
        >
          <Settings className="h-4 w-4 mr-3" />
          Settings
        </button>
        <button
          onClick={onLogout}
          className={`flex items-center w-full px-4 py-2 text-sm ${
            theme === 'light' ? 'text-light-text hover:bg-gray-100' : 'text-dark-text hover:bg-dark-bgAlt'
          }`}
        >
          <LogOut className="h-4 w-4 mr-3" />
          Log out
        </button>
      </div>
    </div>
  );
};

export default MenuDropdown; 