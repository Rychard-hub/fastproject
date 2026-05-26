import { useState, useCallback } from "react";
import { v4 as uuid } from "uuid";

export function useR2File(apiBase = "http://api.rychdesigns.uk") {
  const [url, setUrl] = useState("");
  const [objectKey, setObjectKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // Upload file → FastAPI → R2
  // -----------------------------
  const uploadFile = useCallback(async (file, folder = "uploads", customKey = null) => {
    if (!file) return null;

    setUploading(true);
    setError("");

    try {
      // Generate key with UUID on frontend as requested, or use customKey if provided
      const key = customKey || `${folder}/${uuid()}-${file.name}`;
      
      const formData = new FormData();
      formData.append("file", file);

      // We use custom_key query param for our backend to use our generated key
      const res = await fetch(`${apiBase}/r2/upload?custom_key=${encodeURIComponent(key)}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();

      if (data.url) {
        setUrl(data.url);
        setObjectKey(key);
      }

      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setUploading(false);
    }
  }, [apiBase]);

  // -----------------------------
  // Get signed URL
  // -----------------------------
  const fetchUrl = useCallback(async (key) => {
    if (!key) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${apiBase}/r2/url?object_key=${key}`);

      if (!res.ok) throw new Error("Failed to fetch signed URL");

      const data = await res.json();
      setUrl(data.url);
      setObjectKey(key);
      return data.url;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  // -----------------------------
  // Delete file
  // -----------------------------
  const deleteFile = useCallback(async (key) => {
    if (!key) return false;

    setDeleting(true);
    setError("");

    try {
      const res = await fetch(
        `${apiBase}/r2/delete?object_key=${key}`,
        { method: "DELETE" }
      );

      if (!res.ok) throw new Error("Delete failed");

      setUrl("");
      setObjectKey("");
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setDeleting(false);
    }
  }, [apiBase]);

  // -----------------------------
  // Reset state
  // -----------------------------
  const reset = useCallback(() => {
    setUrl("");
    setObjectKey("");
    setError("");
  }, []);

  return {
    url,
    objectKey,
    loading,
    uploading,
    deleting,
    error,
    uploadFile,
    fetchUrl,
    deleteFile,
    reset,
  };
}
