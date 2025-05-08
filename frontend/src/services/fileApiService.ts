import { apiService } from './apiService';
import { tokenService } from './apiService';
import { environment } from '../common/environment';

export interface FileMetadata {
  id: string;
  session_id: string;
  request_id: string;
  original_name: string;
  mimetype: string;
  internal_id: string;
  internal_name: string;
  from_agent: boolean;
}

export const fileApiService = {
  /**
   * Upload a file to the server
   * @param file - The file to upload
   * @param requestId - Optional request ID
   * @param sessionId - Optional session ID
   * @returns The file ID
   */
  async uploadFile(file: File, requestId?: string, sessionId?: string): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (requestId) {
      formData.append('request_id', requestId);
    }
    
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await apiService.post<{ id: string }>('/files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.id;
  },

  /**
   * Download a file by its ID
   * @param fileId - The ID of the file to download
   */
  async downloadFile(fileId: string): Promise<void> {
    const response = await fetch(`${environment.apiBaseUrl}/files/${fileId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${tokenService.getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    const filename = contentDisposition?.split('filename=')[1]?.replace(/"/g, '') || 'downloaded-file';
    
    // Get the blob
    const blob = await response.blob();
    
    // Create a download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  },

  /**
   * Get metadata for a specific file
   * @param fileId - The ID of the file
   * @returns File metadata
   */
  async getFileMetadata(fileId: string): Promise<FileMetadata> {
    const response = await apiService.get<FileMetadata>(`/files/${fileId}/metadata`);
    return response.data;
  },

  /**
   * Get all files associated with a request ID
   * @param requestId - The request ID
   * @returns Array of file metadata
   */
  async getFilesByRequestId(requestId: string): Promise<FileMetadata[]> {
    const response = await apiService.get<FileMetadata[]>(`/files/request/${requestId}`);
    return response.data;
  }
}; 