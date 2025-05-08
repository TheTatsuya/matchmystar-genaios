import type { FC } from 'react';
import { useRef, useState } from 'react';
import { MoreVertical } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { useLogout } from '../hooks/useLogout';
import UserAvatar from './UserAvatar';
import MenuDropdown from './MenuDropdown';

const UserMenu: FC = () => {
  const { theme } = useTheme();
  const { user } = useAuth();
  const { logout } = useLogout();
  const menuRef = useRef<HTMLDivElement>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="p-4 border-t border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <UserAvatar username={user?.username || ''} />
          <span className={`text-sm font-medium ${
            theme === 'light' ? 'text-light-text' : 'text-dark-text'
          }`}>
            {user?.username}
          </span>
        </div>
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className={`p-1 rounded-full hover:bg-gray-100 ${
              theme === 'light' ? 'text-light-text' : 'text-dark-text'
            }`}
          >
            <MoreVertical className="h-5 w-5" />
          </button>
          <MenuDropdown isOpen={isMenuOpen} onLogout={logout} />
        </div>
      </div>
    </div>
  );
};

export default UserMenu; 