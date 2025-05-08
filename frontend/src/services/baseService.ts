export class BaseService {
  protected async handleRequest<T>(
    request: () => Promise<T>,
    successMessage?: string,
    errorMessage?: string
  ): Promise<T> {
    try {
      const result = await request();
      if (successMessage) {
        const { addNotification } = useNotification();
        addNotification(successMessage, 'success');
      }
      return result;
    } catch (error) {
      const message = errorMessage || 'An error occurred';
      const details = error instanceof Error ? error.message : 'Unknown error';
      throw error;
    }
  }
}
