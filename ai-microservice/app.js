// app.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');

const app = express();
app.use(express.json());
app.use(cors());

// Initialize the Google Generative AI client with your API key
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
// Initialize Gemini model (here we're using "gemini-2.0-flash", adjust as needed)
const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

/**
 * Simulated function to get user preferences from the USER microservice.
 */
const getUserPreferences = async (userID) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve("User prefers outdoor activities, museums, and local cuisine.");
    }, 500);
  });
};

/**
 * Simulated function to get location data from the LOCATION microservice.
 */
const getLocationData = async ({ fromLocation, toLocation, startDate, endDate, budget, tastePreferences }) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        flightData: "Direct flight available with moderate pricing.",
        attractions: "Historical landmarks, parks, and art museums.",
        eateries: "Local eateries with authentic cuisine."
      });
    }, 500);
  });
};

/**
 * Function to call the Gemini API to generate itinerary content.
 */
const callGeminiAPI = async (prompt) => {
  try {
    // Use the Google Generative AI library to generate content.
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    return text;
  } catch (error) {
    console.error("Error generating content:", error);
    return "Error: Unable to generate itinerary from Gemini API.";
  }
};

/**
 * Endpoint to generate an itinerary.
 */
app.post('/api/itinerary', async (req, res) => {
  try {
    const { budget, startDate, endDate, fromLocation, toLocation, userID } = req.body;
    const effectiveUserID = userID || "defaultUser";

    // Retrieve simulated user preferences and location data
    const tastePreferences = await getUserPreferences(effectiveUserID);
    const locationData = await getLocationData({ fromLocation, toLocation, startDate, endDate, budget, tastePreferences });

    // Craft standardised prompt
    const prompt = `
      Generate a travel itinerary based on the following details:
      - User Preferences: ${tastePreferences}
      - Flight Details: ${locationData.flightData}
      - Attractions: ${locationData.attractions}
      - Eateries: ${locationData.eateries}
      - Travel Dates: ${startDate} to ${endDate}
      - Budget: ${budget}
      - From: ${fromLocation}
      - To: ${toLocation}
    `;
    console.log("Crafted Prompt:", prompt);

    // Call the Gemini API to generate the itinerary
    const generatedItinerary = await callGeminiAPI(prompt);
    res.json({ itinerary: generatedItinerary });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred while generating the itinerary.' });
  }
});

/**
 * Additional endpoints to maintain a local copy of userIDs,
 * as notified by the USER microservice.
 */
const localUsers = [];

app.post('/api/user', (req, res) => {
  const { userID } = req.body;
  if (!userID) {
    return res.status(400).json({ error: 'userID is required' });
  }
  if (!localUsers.includes(userID)) {
    localUsers.push(userID);
    console.log('User added:', userID);
    res.json({ message: 'User added successfully', localUsers });
  } else {
    res.status(400).json({ error: 'User already exists' });
  }
});

app.put('/api/user/:userID', (req, res) => {
  const { userID } = req.params;
  if (!localUsers.includes(userID)) {
    return res.status(404).json({ error: 'User not found' });
  }
  console.log('User updated:', userID);
  res.json({ message: 'User updated successfully' });
});

app.delete('/api/user/:userID', (req, res) => {
  const { userID } = req.params;
  const index = localUsers.indexOf(userID);
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  localUsers.splice(index, 1);
  console.log('User deleted:', userID);
  res.json({ message: 'User deleted successfully', localUsers });
});


// Send itinerary to USER microservice
const saveItineraryToUserMicroservice = async (userID, itinerary) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log(`Itinerary for user ${userID} saved to USER microservice.`);
        resolve({ success: true, message: 'Itinerary saved to USER microservice.' });
      }, 500);
    });
  };

const aiLogs = []; // In-memory storage for logs

// Save Itinerary
app.post('/api/saveItinerary', async (req, res) => {
    try {
      const { userID, itinerary, prompt } = req.body;
      if (!userID || !itinerary) {
        return res.status(400).json({ error: 'userID and itinerary are required' });
      }
  
      // Simulate sending the itinerary to the USER microservice
      const userServiceResponse = await saveItineraryToUserMicroservice(userID, itinerary);
  
      // Create a log entry
      const logEntry = {
        timestamp: new Date().toISOString(),
        userID,
        itinerary,
        prompt, // Optional: include the prompt used to generate the itinerary
        userServiceResponse
      };
  
      // Store the log entry (in memory for now)
      aiLogs.push(logEntry);
      console.log("New AI log entry:", logEntry);
  
      res.json({
        message: 'Itinerary saved successfully.',
        logEntry
      });
    } catch (error) {
      console.error('Error saving itinerary:', error);
      res.status(500).json({ error: 'An error occurred while saving the itinerary.' });
    }
  });
  




// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is listening on port ${PORT}`);
});



