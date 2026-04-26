import React, { useState, useRef } from 'react';
import { Upload, FolderUp, X, CheckCircle } from 'lucide-react';

export default function UploadZone({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState('idle'); // idle | uploading | success | error
  const [message, setMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleUpload = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.zip')) {
      setStatus('error');
      setMessage('Only .zip files supported. Please zip your project first.');
      return;
    }

    setStatus('uploading');
    setMessage(`Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        setStatus('success');
        setMessage(`✓ ${data.message}`);
        onUploadSuccess?.(data);
        setTimeout(() => setStatus('idle'), 4000);
      } else {
        setStatus('error');
        setMessage(data.detail || 'Upload failed.');
      }
    } catch (e) {
      setStatus('error');
      setMessage('Network error — is the backend running?');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleUpload(file);
  };

  const handleFileChange = (e) => {
    handleUpload(e.target.files[0]);
  };

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${status}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => status === 'idle' && fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".zip"
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {status === 'idle' && (
        <>
          <FolderUp size={20} color="#808080" />
          <span className="upload-label">Drop .zip to upload project</span>
        </>
      )}
      {status === 'uploading' && (
        <>
          <Upload size={20} color="#007acc" className="spinning" />
          <span className="upload-label uploading">{message}</span>
        </>
      )}
      {status === 'success' && (
        <>
          <CheckCircle size={20} color="#4ec9b0" />
          <span className="upload-label success">{message}</span>
        </>
      )}
      {status === 'error' && (
        <>
          <X size={20} color="#f48771" />
          <span className="upload-label error">{message}</span>
        </>
      )}
    </div>
  );
}
