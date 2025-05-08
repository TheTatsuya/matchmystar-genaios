import type { FC } from 'react';
import { Box } from '@mui/material';
import { Notification } from './Notification';
import { useNotification } from '../contexts/NotificationContext';

export const NotificationContainer: FC = () => {
  const { notifications, removeNotification } = useNotification();

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 16,
        right: 16,
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
      }}
    >
      {notifications.map((notification) => (
        <Notification
          key={notification.id}
          notification={notification}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </Box>
  );
};
