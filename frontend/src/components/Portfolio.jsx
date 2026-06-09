import React, { useEffect, useState } from 'react';
import FaceExercise from './FaceExercise';

const API_URL = import.meta.env.VITE_API_URL || '';

const Portfolio = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/portfolio`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        setProjects(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching portfolio", err);
        setError(`Failed to load portfolio: ${err.message}`);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading portfolio...</p>;
  
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  if (projects.length === 0) return <p>No portfolio projects available.</p>;

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>My Portfolio</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px' }}>
        {projects.map((project, index) => (
          <div key={index} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
            <h3>{project.title}</h3>
            <p>{project.description}</p>
            <a 
              href={project.link} 
              target={project.link.startsWith('#') ? "_self" : "_blank"} 
              rel="noopener noreferrer" 
              style={{ color: '#007bff', textDecoration: 'none' }}
            >
              View Project →
            </a>
          </div>
        ))}
      </div>
      <FaceExercise />
    </div>
  );
};

export default Portfolio;
