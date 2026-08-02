import React, { useState, useCallback, useEffect } from 'react';
import { UploadCloud, File, X, CheckCircle, AlertCircle, Loader2, Database } from 'lucide-react';
import { uploadFiles, getDocuments, deleteDocument, getStatistics, reindex } from '../services/api';

const UploadManager = () => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [docs, st] = await Promise.all([getDocuments(), getStatistics()]);
      setDocuments(docs);
      setStats(st);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
    // Poll for updates while processing
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const processUploads = async (filesToUpload) => {
    if (!filesToUpload || filesToUpload.length === 0) return;

    const newUploads = Array.from(filesToUpload).map(file => ({
      id: Math.random().toString(36).substring(7),
      file,
      name: file.name,
      progress: 0,
      status: 'uploading'
    }));

    setUploadingFiles(prev => [...prev, ...newUploads]);

    try {
      await uploadFiles(filesToUpload, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadingFiles(prev => 
          prev.map(item => 
            newUploads.some(u => u.id === item.id) 
              ? { ...item, progress } 
              : item
          )
        );
      });

      // Update status to processing (handled by backend background task)
      setUploadingFiles(prev => 
        prev.map(item => 
          newUploads.some(u => u.id === item.id) 
            ? { ...item, status: 'processing', progress: 100 } 
            : item
        )
      );

      // Refresh list
      setTimeout(fetchData, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadingFiles(prev => 
        prev.map(item => 
          newUploads.some(u => u.id === item.id) 
            ? { ...item, status: 'error' } 
            : item
        )
      );
    }
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processUploads(e.dataTransfer.files);
    }
  }, []);

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processUploads(e.target.files);
      e.target.value = null; // Reset input
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        setIsLoading(true);
        await deleteDocument(id);
        await fetchData();
      } catch (error) {
        console.error('Failed to delete document:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleReindex = async () => {
    if (window.confirm('Are you sure you want to completely clear the database? This cannot be undone.')) {
      try {
        setIsLoading(true);
        await reindex();
        await fetchData();
      } catch (error) {
        console.error('Failed to reindex:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 rounded-xl shadow-lg overflow-hidden border border-slate-200 dark:border-slate-800">
      <div className="bg-white dark:bg-slate-800 p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-white">Documents</h2>
        <button
          onClick={handleReindex}
          disabled={isLoading}
          className="text-xs flex items-center gap-1 bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50 px-3 py-1.5 rounded-full transition-colors"
        >
          <Database size={14} />
          Clear DB
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors ${
            isDragging 
              ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' 
              : 'border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            multiple
            onChange={handleFileInput}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            title="Upload documents"
          />
          <UploadCloud size={48} className="text-slate-400 dark:text-slate-500 mb-4" />
          <p className="text-slate-700 dark:text-slate-300 font-medium">
            Drag & drop files here
          </p>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            or click to browse
          </p>
          <p className="text-slate-400 dark:text-slate-500 text-xs mt-4">
            Supports PDF, DOCX, TXT, CSV, JSON, ZIP & more
          </p>
        </div>

        {/* Uploading List */}
        {uploadingFiles.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Processing</h3>
            <div className="space-y-2">
              {uploadingFiles.filter(u => u.status !== 'completed').map((file) => (
                <div key={file.id} className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-3">
                  <div className="p-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-md">
                    <File size={20} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-center mb-1">
                      <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate pr-4">
                        {file.name}
                      </p>
                      {file.status === 'error' && <AlertCircle size={16} className="text-red-500" />}
                      {file.status === 'processing' && <Loader2 size={16} className="text-indigo-500 animate-spin" />}
                      {file.status === 'uploading' && <span className="text-xs text-slate-500">{file.progress}%</span>}
                    </div>
                    {file.status === 'uploading' && (
                      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-1.5">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        ></div>
                      </div>
                    )}
                    {file.status === 'processing' && (
                      <p className="text-xs text-indigo-500">Processing document...</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Uploaded List */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Uploaded Documents</h3>
          {documents.length === 0 ? (
            <p className="text-slate-500 dark:text-slate-400 text-sm italic">No documents uploaded yet.</p>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="bg-white dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700 flex flex-col space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 overflow-hidden">
                      <div className="p-2 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded-md flex-shrink-0">
                        <File size={20} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate" title={doc.filename}>
                          {doc.filename}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 mt-1">
                          <span className="uppercase">{doc.content_type}</span>
                          <span>&bull;</span>
                          <span>{doc.chunks_count} chunks</span>
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-md transition-colors flex-shrink-0"
                      title="Delete"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Stats Footer */}
      {stats && (
        <div className="bg-slate-100 dark:bg-slate-950 p-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 dark:text-slate-400 grid grid-cols-2 gap-2">
          <div>
            <span className="block text-slate-400 dark:text-slate-500 mb-0.5">Vector DB Size</span>
            <span className="font-medium text-slate-700 dark:text-slate-300">{formatBytes(stats.vector_db_size_bytes)}</span>
          </div>
          <div>
            <span className="block text-slate-400 dark:text-slate-500 mb-0.5">Total Vectors</span>
            <span className="font-medium text-slate-700 dark:text-slate-300">{stats.total_embeddings}</span>
          </div>
          <div className="col-span-2 pt-2 mt-1 border-t border-slate-200 dark:border-slate-800">
            <span className="block text-slate-400 dark:text-slate-500 mb-0.5">Model</span>
            <span className="font-medium text-slate-700 dark:text-slate-300 truncate block" title={stats.embedding_model}>
              {stats.embedding_model}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadManager;
