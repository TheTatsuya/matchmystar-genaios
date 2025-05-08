import type { FC, ReactNode } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { getThemeColors } from '../utils/themeUtils';
import { PlusIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

interface PageCardProps {
  title: string;
  isActive: boolean;
  icon?: ReactNode;
  onClick: () => void;
  plusBtnNav?: string;
}

const PageCard: FC<PageCardProps> = ({ title, isActive, icon, onClick, plusBtnNav }) => {
  const { theme } = useTheme();
  const colors = getThemeColors(theme);

  return (
    <div
      className={`
        w-full rounded-lg transition-all duration-150
        flex items-center space-x-3 border border-gray-200 border-solid
        ${isActive
          ? `bg-light-secondary-primary/40 text-light-bg hover:bg-light-secondary-secondary `
          : `${colors.text} hover:bg-gray-100 dark:hover:bg-gray-800`
        }
        transform hover:scale-[1.02] active:scale-[0.98]
        focus:outline-none focus:ring-2 focus:ring-offset-2
        ${theme === 'light'
          ? 'focus:ring-light-secondary-primary focus:ring-offset-white'
          : 'focus:ring-dark-secondary-primary focus:ring-offset-dark-bg'
        }
      `}
    >
    <button
      onClick={onClick}
      className="px-4 py-3 flex items-center justify-between w-full"
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      <span className="flex-1 text-left font-medium">{title}</span>
    </button>
    {plusBtnNav && (
        <div className="flex items-center pr-2">
            <Link 
              to={plusBtnNav} 
              className={`flex-shrink-0 p-2 rounded-md transition-colors bg-[#FF5722] text-white hover:bg-[#E64A19] shadow-lg`}
            >
              <PlusIcon className="h-6 w-6" />
            </Link>
        </div>
      )}
    </div>
  );
};

export default PageCard;
