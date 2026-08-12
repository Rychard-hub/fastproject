
import { useEffect, useState } from 'react'
import { useR2File } from "../hooks/useR2File";
import { getAdminKey, setAdminKey, adminHeaders } from "../adminAuth";

const API_URL = import.meta.env.VITE_API_URL || '';

/**
 * @typedef {Object} Post
 * @property {number} id
 * @property {string} title
 * @property {string} content
 * @property {string} author
 * @property {string|null} file_path
 * @property {string} created_at
 * @property {string} updated_at
 * @property {boolean} publishe
 */

/**
 * @param {{ post: Post }} props
 */
function BlogPost({ post }) {
    const [expanded, setExpanded] = useState(false);
    
    const { 
        id, 
        title, 
        content, 
        author, 
        file_path, 
        created_at 
    } = post;

    const isLong = content.length > 200;
    const displayedContent = expanded || !isLong ? content : content.substring(0, 200) + '...';

    const shareUrl = window.location.href; // In a real app, this might be a specific post URL
    const shareText = `Check out this blog post: ${title}`;

    const isImage = file_path && (
        file_path.toLowerCase().endsWith('.jpg') || 
        file_path.toLowerCase().endsWith('.jpeg') || 
        file_path.toLowerCase().endsWith('.png') || 
        file_path.toLowerCase().endsWith('.gif') ||
        file_path.toLowerCase().endsWith('.webp')
    );

    return (
        <article key={id} style={{ padding: '20px', border: '1px solid #eee', borderRadius: '8px' }}>
            <h3>{title}</h3>
            <p><small>By {author} on {new Date(created_at).toLocaleDateString()}</small></p>
            
            {file_path && isImage && (
                <div style={{ marginBottom: '15px' }}>
                    <img 
                        src={file_path.startsWith('http') ? file_path : `${API_URL}${file_path}`} 
                        alt={title} 
                        style={{ maxWidth: '70%', height: 'auto', borderRadius: '4px' }}
                    />
                </div>
            )}

            <p style={{ whiteSpace: 'pre-wrap' }}>{displayedContent}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '10px' }}>
                {isLong && (
                    <button 
                        onClick={() => setExpanded(!expanded)} 
                        style={{ 
                            background: 'none', 
                            border: 'none', 
                            color: '#007bff', 
                            cursor: 'pointer', 
                            padding: 0, 
                            textDecoration: 'underline',
                            fontSize: '14px'
                        }}
                    >
                        {expanded ? 'Read less' : 'Read more'}
                    </button>
                )}
                
                <div style={{ display: 'flex', gap: '10px', marginLeft: isLong ? 'auto' : '0' }}>
                    <span style={{ fontSize: '14px', color: '#666' }}>Share:</span>
                    <a 
                        href={`mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(`I thought you might be interested in this post: ${title}\n\n${shareUrl}`)}`}
                        title="Share via Email"
                        style={{ textDecoration: 'none', fontSize: '14px' }}
                    >
                        📧
                    </a>
                    <a 
                        href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`}
                        target="_blank" 
                        rel="noopener noreferrer"
                        title="Share on Twitter"
                        style={{ textDecoration: 'none', fontSize: '14px' }}
                    >
                        🐦
                    </a>
                    <a 
                        href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`}
                        target="_blank" 
                        rel="noopener noreferrer"
                        title="Share on Facebook"
                        style={{ textDecoration: 'none', fontSize: '14px' }}
                    >
                        📘
                    </a>
                </div>
            </div>
        </article>
    );
}

export function AvatarUploader() {
  const [file, setFile] = useState(null);

  const {
    url,
    uploading,
    loading,
    deleting,
    error,
    uploadFile,
    deleteFile
  } = useR2File(API_URL);

  return (
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px dashed #ccc', borderRadius: '8px' }}>
      <h3>Avatar Manager</h3>

      {error && <p style={{ color: "red" }}>{error}</p>}
      {uploading && <p>Uploading...</p>}
      {loading && <p>Loading...</p>}
      {deleting && <p>Deleting...</p>}

      {url && (
        <img
          src={url}
          alt="avatar"
          style={{ width: 120, height: 120, objectFit: 'cover', borderRadius: "50%", marginBottom: 10 }}
        />
      )}

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={() => uploadFile(file, "avatars")}>
          Upload Avatar
        </button>

        <button onClick={() => deleteFile("avatars/my-avatar.jpg")}>
          Delete Avatar
        </button>
      </div>
    </div>
  );
}

function AdminLogin({ adminKey, onKeyChange }) {
    const [input, setInput] = useState('');

    if (adminKey) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px', fontSize: '14px', color: '#666' }}>
                <span>🔓 Admin mode on</span>
                <button
                    type="button"
                    onClick={() => onKeyChange('')}
                    style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}
                >
                    Log out
                </button>
            </div>
        );
    }

    return (
        <form
            onSubmit={(e) => { e.preventDefault(); onKeyChange(input); setInput(''); }}
            style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '15px' }}
        >
            <input
                type="password"
                placeholder="Admin key (leave empty to browse as visitor)"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                style={{ padding: '6px', fontSize: '13px', flex: 1 }}
            />
            <button type="submit" style={{ padding: '6px 12px', fontSize: '13px', cursor: 'pointer' }}>
                Unlock admin
            </button>
        </form>
    );
}

function Blog() {
    const [posts, setPosts] = useState([])
    const [title, setTitle] = useState('')
    const [content, setContent] = useState('')
    const [author, setAuthor] = useState('')
    const [file, setFile] = useState(null)
    const [loading, setLoading] = useState(true)
    const [adminKey, setAdminKeyState] = useState(getAdminKey())

    const [error, setError] = useState('')

    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

    const fetchPosts = () => {
        fetch(`${API_URL}/blog/`)
            .then(res => res.json())
            .then(data => {
                setPosts(data)
                setLoading(false)
            })
            .catch(err => {
                console.error("Error fetching blog posts", err)
                setLoading(false)
            })
    }

    useEffect(() => {
        fetchPosts()
    }, [])

    const handleAdminKeyChange = (key) => {
        setAdminKey(key)
        setAdminKeyState(key)
    }

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        setError('');
        
        if (selectedFile) {
            if (selectedFile.size > MAX_FILE_SIZE) {
                setError(`File is too large. Max size is ${MAX_FILE_SIZE / (1024 * 1024)}MB.`);
                e.target.value = null; // Reset input
                setFile(null);
                return;
            }

            if (selectedFile.type === 'text/plain') {
                const reader = new FileReader();
                reader.onload = (event) => {
                    setContent(event.target.result + "\n\n" + content);
                };
                reader.readAsText(selectedFile);
            }
        }
        setFile(selectedFile);
    }

    const [uploading, setUploading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setUploading(true)
        
        try {
            let filePathDirect = null;
            
            // OPTIONAL: Direct upload to R2 from frontend
            if (file && (file instanceof File || file instanceof Blob)) {
                try {
                    // 1. Get presigned URL from backend
                    const presignedRes = await fetch(`${API_URL}/blog/presigned-url?filename=${encodeURIComponent(file.name)}`, {
                        headers: adminHeaders()
                    });
                    if (presignedRes.ok) {
                        const { url, file_path } = await presignedRes.json();
                        
                        // 2. Upload directly to R2
                        const uploadRes = await fetch(url, {
                            method: 'PUT',
                            body: file,
                            headers: {
                                'Content-Type': file.type
                            }
                        });
                        
                        if (uploadRes.ok) {
                            filePathDirect = file_path;
                            console.log("Uploaded directly to R2:", filePathDirect);
                        } else {
                            console.warn("Direct R2 upload failed, falling back to backend upload");
                        }
                    }
                } catch (err) {
                    console.error("Error during direct R2 upload:", err);
                }
            }

            const formData = new FormData();
            formData.append('title', title);
            formData.append('content', content);
            formData.append('author', author);
            
            if (filePathDirect) {
                formData.append('file_path_direct', filePathDirect);
            } else if (file instanceof File || file instanceof Blob) {
                formData.append('file', file);
            }

            const res = await fetch(`${API_URL}/blog/`, {
                method: 'POST',
                headers: adminHeaders(),
                body: formData,
            });

            if (res.ok) {
                setTitle('')
                setContent('')
                setAuthor('')
                setFile(null)
                setError('')
                e.target.reset();
                fetchPosts()
            } else if (res.status === 401) {
                setError('Admin key is invalid. Please log in again.')
                handleAdminKeyChange('')
            } else {
                const errorData = await res.json();
                setError(errorData.detail || 'Failed to create post');
            }
        } catch (err) {
            console.error("Error creating blog post", err)
            setError('An error occurred during upload');
        } finally {
            setUploading(false)
        }
    }

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h1>Blog Posts</h1>

            <AdminLogin adminKey={adminKey} onKeyChange={handleAdminKeyChange} />

            {adminKey && <AvatarUploader />}

            {adminKey && (
            <section style={{ marginBottom: '40px', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
                <h2>Create New Post</h2>
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <input 
                        type="text" 
                        placeholder="Title" 
                        value={title} 
                        onChange={(e) => setTitle(e.target.value)} 
                        required 
                        style={{ padding: '8px' }}
                    />
                    <input 
                        type="text" 
                        placeholder="Author" 
                        value={author} 
                        onChange={(e) => setAuthor(e.target.value)} 
                        required 
                        style={{ padding: '8px' }}
                    />
                    <textarea 
                        placeholder="Content" 
                        value={content} 
                        onChange={(e) => setContent(e.target.value)} 
                        required 
                        rows="5"
                        style={{ padding: '8px' }}
                    />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                        <label htmlFor="file-upload" style={{ fontSize: '14px', color: '#666' }}>Upload Photo or Text File (Max 5MB):</label>
                        <input 
                            id="file-upload"
                            type="file" 
                            onChange={handleFileChange}
                            accept="image/*,.txt"
                            style={{ padding: '8px' }}
                        />
                    </div>
                    {error && <p style={{ color: 'red', fontSize: '14px', margin: '0' }}>{error}</p>}
                    <button 
                        type="submit" 
                        disabled={uploading}
                        style={{ 
                            padding: '10px', 
                            cursor: uploading ? 'not-allowed' : 'pointer', 
                            backgroundColor: uploading ? '#888' : '#333', 
                            color: 'white', 
                            border: 'none' 
                        }}
                    >
                        {uploading ? 'Uploading...' : 'Post It!'}
                    </button>
                </form>
            </section>
            )}

            <section>
                {loading ? (
                    <p>Loading posts...</p>
                ) : posts.length === 0 ? (
                    <p>No blog posts found.</p>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        {posts.map(post => (
                            <BlogPost key={post.id} post={post} />
                        ))}
                    </div>
                )}
            </section>
        </div>
    )
}

export default Blog

