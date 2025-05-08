import type { FC } from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface UserAvatarProps {
  username: string;
}

const UserAvatar: FC<UserAvatarProps> = ({ username }) => {
  const { theme } = useTheme();

  const getInitial = (name: string) => name.charAt(0).toUpperCase();

  const getRandomColor = (name: string) => {
    const colors = [
      theme === 'light' ? 'bg-light-secondary-primary' : 'bg-dark-secondary-primary',
      theme === 'light' ? 'bg-light-secondary-secondary' : 'bg-dark-secondary-secondary',
    ];
    const index = name.length % colors.length;
    return colors[index];
  };

  return (
    <div className={`w-8 h-8 rounded-full ${getRandomColor(username)} flex items-center justify-center ${
      theme === 'light' ? 'text-light-bg' : 'text-dark-bg'
    } font-medium`}>
      {getInitial(username)}
    </div>
  );
};

export default UserAvatar; 