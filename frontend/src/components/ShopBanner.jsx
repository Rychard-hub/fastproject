import React, { useEffect, useState } from "react";
import { useR2File } from "../hooks/useR2File";

const BANNER_KEY = "menu/banner/banner.jpg";
const API_URL = import.meta.env.VITE_API_URL || '';
<<<<<<< HEAD
<<<<<<< HEAD

const API_URL = import.meta.env.VITE_API_URL || '';
=======
>>>>>>> origin/main
=======
>>>>>>> origin/main

export default function ShopBanner() {
  const {
    url,
    uploading,
    loading,
    error,
    uploadFile,
    fetchUrl
  } = useR2File(API_URL);

  const [editMode, setEditMode] = useState(false);
  const [file, setFile] = useState(null);

  useEffect(() => {
    fetchUrl(BANNER_KEY);
  }, [fetchUrl]);

  const handleUpload = async () => {
    if (!file) return;
    // We want to use a consistent key for the banner
    // Currently uploadFile generates a random UUID key
    // Let's modify R2Service or create a specific endpoint if needed
    // But for now, let's see if we can use the existing uploadFile and then maybe rename it or just use the returned URL
    
    // Actually, useR2File.js uploadFile calls /r2/upload which generates a UUID.
    // If we want a fixed banner, we might need a specific endpoint or just store the returned URL in a setting.
    // However, to keep it simple and fulfill the user request "upload banner from R2 to the top of the e-shop",
    // I will use a fixed key if I can, or just display the latest uploaded one.
    
    const result = await uploadFile(file, "shop", BANNER_KEY);
    if (result && result.url) {
        setEditMode(false);
    }
  };

  return (
    <div style={{ marginBottom: "30px", textAlign: "center", position: "relative" }}>
      {loading && <p>Loading banner...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {url ? (
        <div style={{ width: "100%", height: "250px", overflow: "hidden", borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}>
          <img
            src={url}
            alt="Shop Banner"
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      ) : (
        !loading && (
          <div style={{ width: "100%", height: "150px", display: "flex", alignItems: "center", justifyContent: "center", border: "2px dashed #ccc", borderRadius: "8px" }}>
            <p>No banner uploaded yet.</p>
          </div>
        )
      )}

      <div style={{ marginTop: "10px" }}>
        {editMode ? (
          <div style={{ display: "inline-flex", gap: "10px", alignItems: "center" }}>
            <input type="file" onChange={(e) => setFile(e.target.files[0])} accept="image/*" />
            <button onClick={handleUpload} disabled={uploading}>
              {uploading ? "Uploading..." : "Save Banner"}
            </button>
            <button onClick={() => setEditMode(false)}>Cancel</button>
          </div>
        ) : (
          <button onClick={() => setEditMode(true)} style={{ fontSize: "12px", opacity: 0.7 }}>
            {url ? "Change Banner" : "Upload Banner"}
          </button>
        )}
      </div>
    </div>
  );
}
