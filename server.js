import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(join(__dirname, 'public')));

// Special handling for review.html to inject PLACE_ID
app.get('/review.html', (req, res) => {
  const fs = require('fs');
  const path = join(__dirname, 'public', 'review.html');
  
  fs.readFile(path, 'utf8', (err, data) => {
    if (err) {
      res.status(500).send('Error loading review page');
      return;
    }
    
    // Replace PLACE_ID placeholder with actual Place ID
    const modifiedHtml = data.replace(/PLACE_ID/g, process.env.PLACE_ID || 'PLACE_ID');
    res.send(modifiedHtml);
  });
});

// Authentication endpoint
app.post('/auth', (req, res) => {
  const { password } = req.body;
  
  if (password === process.env.ACCESS_PASSWORD) {
    res.status(200).json({ success: true });
  } else {
    res.status(401).json({ success: false, message: 'Invalid password' });
  }
});

// AI suggestion endpoint
app.post('/suggest', async (req, res) => {
  try {
    const { answers } = req.body;
    
    // Build prompt for OpenAI
    const prompt = `Draft FOUR 1-3-sentence first-person Google reviews using this JSON feedback: ${JSON.stringify(answers)}. 
    Each review should be natural, positive, and mention specific details from the feedback. 
    Return only the review text, one per line, no numbering or formatting.`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant that writes authentic, positive Google reviews based on patient feedback.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: 250,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content;
    
    // Split the response into individual suggestions
    const suggestions = content.split('\n').filter(line => line.trim().length > 0);
    
    res.json({ suggestions });
  } catch (error) {
    console.error('Error generating suggestions:', error);
    res.status(500).json({ 
      error: 'Failed to generate suggestions',
      suggestions: [
        "The staff was incredibly professional and caring throughout my visit.",
        "I received excellent care and would highly recommend this clinic to others.",
        "The facility was clean and modern, and the treatment was top-notch.",
        "Outstanding service from start to finish - thank you for taking such good care of me!"
      ]
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🏥 ClinicReviewKiosk running on http://localhost:${PORT}`);
  console.log(`📱 Open on iPad in full-screen mode for kiosk experience`);
});

export default app; 