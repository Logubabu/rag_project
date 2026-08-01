import React, { useState, useEffect } from 'react';
import { getDocuments, uploadFiles, deleteDocument } from '../services/api';
import { UploadCloud, Trash2, FileText, Loader } from 'lucide-react';

const FilesPage = () => {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to fetch documents', error);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleUpload(e.dataTransfer.files);
    }
  };

  const handleFileInput = async (e) => {
    if (e.target.files && e.target.files[0]) {
      await handleUpload(e.target.files);
    }
  };

  const handleUpload = async (files) => {
    setIsUploading(true);
    try {
      await uploadFiles(files);
      await fetchDocuments();
    } catch (error) {
      alert(error.response?.data?.detail || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteDocument(id);
      await fetchDocuments();
    } catch (error) {
      console.error('Failed to delete document', error);
    }
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Knowledge Base</h1>
      
      <div 
        className={`border-2 border-dashed rounded-xl p-10 text-center mb-10 transition-colors ${dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <UploadCloud className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-2">Drag and drop files here to upload</p>
        <p className="text-sm text-gray-400 mb-4">Supported: PDF, TXT, DOCX, CSV, JSON, ZIP, etc. (Max 20MB)</p>
        
        <label className="bg-indigo-600 text-white px-6 py-2 rounded-lg cursor-pointer hover:bg-indigo-700 transition-colors inline-flex items-center">
          {isUploading ? <Loader className="w-4 h-4 mr-2 animate-spin" /> : null}
          {isUploading ? 'Uploading...' : 'Select Files'}
          <input type="file" multiple className="hidden" onChange={handleFileInput} disabled={isUploading} />
        </label>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-xl">
          <h2 className="font-semibold text-gray-700">Uploaded Documents</h2>
          <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-full">{documents.length} files</span>
        </div>
        
        {documents.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No documents uploaded yet.
          </div>
        ) : (
          <ul className="divide-y divide-gray-100">
            {documents.map((doc) => (
              <li key={doc.id} className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4">
                  <div className="bg-indigo-50 p-2 rounded-lg">
                    <FileText className="w-6 h-6 text-indigo-500" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{doc.filename}</p>
                    <p className="text-sm text-gray-500">
                      {formatSize(doc.size)} • Uploaded on {new Date(doc.upload_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => handleDelete(doc.id)}
                  className="text-gray-400 hover:text-red-500 hover:bg-red-50 p-2 rounded-full transition-colors"
                  title="Delete Document"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default FilesPage;
