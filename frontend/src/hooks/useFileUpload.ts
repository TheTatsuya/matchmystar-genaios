import { useState, useCallback } from 'react';
import { fileApiService, FileMetadata } from '../services/fileApiService';

interface UseFileUploadReturn {
  uploadedFiles: string[];
  isUploading: boolean;
  uploadFile: (file: File, requestId?: string, sessionId?: string) => Promise<string>;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;
  getFileMetadata: (fileId: string) => Promise<FileMetadata>;
  getFilesByRequestId: (requestId: string) => Promise<FileMetadata[]>;
}

export const useFileUpload = (): UseFileUploadReturn => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = useCallback(async (file: File, requestId?: string, sessionId?: string) => {
    setIsUploading(true);
    try {
      const fileId = await fileApiService.uploadFile(file, requestId, sessionId);
      setUploadedFiles(prev => [...prev, fileId]);
      return fileId;
    } finally {
      setIsUploading(false);
    }
  }, []);

  const removeFile = useCallback((fileId: string) => {
    setUploadedFiles(prev => prev.filter(id => id !== fileId));
  }, []);

  const clearFiles = useCallback(() => {
    setUploadedFiles([]);
  }, []);

  const getFileMetadata = useCallback(async (fileId: string) => {
    return fileApiService.getFileMetadata(fileId);
  }, []);

  const getFilesByRequestId = useCallback(async (requestId: string) => {
    return fileApiService.getFilesByRequestId(requestId);
  }, []);

  return {
    uploadedFiles,
    isUploading,
    uploadFile,
    removeFile,
    clearFiles,
    getFileMetadata,
    getFilesByRequestId
  };
}; 