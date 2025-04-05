const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// Google Places API endpoint and API key
const GOOGLE_PLACES_API_URL = "https://places.googleapis.com/v1/places:searchText";
const GOOGLE_PLACES_API_KEY = process.env.GOOGLE_PLACES_API_KEY;

app.post('/search', async (req, res) => {
  const { textQuery } = req.body;
  if (!textQuery) {
    return res.status(400).json({ error: "Missing 'textQuery' parameter" });
  }

  const payload = { textQuery };

  try {
    const response = await axios.post(GOOGLE_PLACES_API_URL, payload, {
      headers: {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': GOOGLE_PLACES_API_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel,places.regularOpeningHours,places.priceLevel'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error making request to Google Places API:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start the server on the specified port (default: 4500)
const PORT = process.env.PORT || 4500;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});

