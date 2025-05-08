import { useNotification } from '../contexts/NotificationContext';

export const useHandleRequest = async <T>(
  request: () => Promise<T>,
  successMessage?: string,
  errorMessage?: string
): Promise<T> => {
  try {
    const result = await request();
    if (successMessage) {
      const { addNotification } = useNotification();
      addNotification(successMessage, 'success');
    }
    return result;
  } catch (error) {
    const { addNotification } = useNotification();
    const message = errorMessage || 'An error occurred';
    const details = error instanceof Error ? error.message : 'Unknown error';
    addNotification(message, 'error', details);
    throw error;
  }
}