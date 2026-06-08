import React, { useState, useEffect } from 'react';

const FaceExercise = () => {
  const [data, setData] = useState({ benefits: [], routines: [], proTips: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://api.rychdesigns.uk/blog/face-exercises/data');
        const json = await response.json();
        
        // If the database is empty, seed it and fetch again
        if (json.benefits.length === 0 && json.routines.length === 0 && json.proTips.length === 0) {
          await fetch('http://api.rychdesigns.uk/blog/face-exercises/seed', { method: 'POST' });
          const retryResponse = await fetch('http://api.rychdesigns.uk/blog/face-exercises/data');
          const retryJson = await retryResponse.json();
          setData(retryJson);
        } else {
          setData(json);
        }
      } catch (err) {
        console.error("Failed to fetch face exercise data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const { benefits, routines, proTips } = data;

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading Natural Wellness...</div>;
  }

  return (
    <div id="face-yoga" style={{ marginTop: '50px', padding: '30px', backgroundColor: '#f9fbf9', borderRadius: '12px' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h2 style={{ color: '#2d5a27', fontSize: '2rem' }}>🌿 Natural Wellness</h2>
        <h3 style={{ fontSize: '1.5rem', margin: '10px 0' }}>Face Yoga & Exercises</h3>
        <p style={{ maxWidth: '600px', margin: '0 auto', fontSize: '1.1rem', color: '#555', lineHeight: '1.6' }}>
          Tone, lift, and rejuvenate your facial muscles naturally — no creams, no needles. 
          Just a few mindful minutes a day for a radiant, youthful glow.
        </p>
      </div>

      <div style={{ marginTop: '40px' }}>
        <h4 style={{ textAlign: 'center', fontSize: '1.3rem', marginBottom: '30px' }}>Why Facial Exercises?</h4>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '30px' }}>Science-backed benefits of a consistent face yoga practice</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '25px' }}>
          {benefits.map((benefit, index) => (
            <div key={index} style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
              <h5 style={{ color: '#2d5a27', fontSize: '1.1rem', marginBottom: '10px' }}>{benefit.title}</h5>
              <p style={{ fontSize: '0.95rem', color: '#666', lineHeight: '1.5' }}>{benefit.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '60px' }}>
        <h4 style={{ textAlign: 'center', fontSize: '1.5rem', marginBottom: '10px' }}>The Exercise Routine</h4>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '40px' }}>8 targeted moves for a full facial workout</p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '30px' }}>
          {routines.map((routine, index) => (
            <div key={index} style={{ backgroundColor: '#fff', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)', borderTop: '4px solid #2d5a27' }}>
              <div style={{ fontSize: '2rem', marginBottom: '10px' }}>{routine.icon}</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#2d5a27', textTransform: 'uppercase', backgroundColor: '#eef5ee', padding: '2px 8px', borderRadius: '4px' }}>{routine.level}</span>
                <span style={{ fontSize: '0.85rem', color: '#888' }}>{routine.target}</span>
              </div>
              <h5 style={{ fontSize: '1.2rem', marginBottom: '15px' }}>{routine.title}</h5>
              <ol style={{ paddingLeft: '20px', fontSize: '0.95rem', color: '#555', lineHeight: '1.5' }}>
                {routine.steps.map((step, sIdx) => (
                  <li key={sIdx} style={{ marginBottom: '8px' }}>{step}</li>
                ))}
              </ol>
              <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f0f7f0', borderRadius: '6px', fontSize: '0.9rem', color: '#2d5a27', fontWeight: 'bold', textAlign: 'center' }}>
                ⏱ {routine.timing}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '60px', padding: '40px', backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
        <h4 style={{ fontSize: '1.5rem', marginBottom: '30px', color: '#2d5a27' }}>Pro Tips</h4>
        <p style={{ color: '#666', marginBottom: '30px' }}>Get the most out of your facial fitness routine</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '30px' }}>
          {proTips.map((tip, index) => (
            <div key={index}>
              <h5 style={{ fontSize: '1.1rem', marginBottom: '10px', color: '#333' }}>{tip.title}</h5>
              <p style={{ fontSize: '0.95rem', color: '#666', lineHeight: '1.5' }}>{tip.content}</p>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '60px', textAlign: 'center', padding: '50px', backgroundColor: '#2d5a27', color: '#fff', borderRadius: '12px' }}>
        <h4 style={{ fontSize: '1.8rem', marginBottom: '20px' }}>🌸 Ready to Begin Your Journey?</h4>
        <p style={{ maxWidth: '700px', margin: '0 auto', fontSize: '1.1rem', lineHeight: '1.7', opacity: '0.9' }}>
          Commit to just 15 minutes each morning. Within 4–6 weeks, you'll notice improved tone, 
          brighter skin, and a more relaxed, confident expression.
        </p>
      </div>
    </div>
  );
};

export default FaceExercise;
