// Test script for ai-microservice API calls (without starting the server)
require('dotenv').config();
const axios = require('axios');

// Create a test environment
const PLACES_MICROSERVICE_URL = process.env.PLACES_MICROSERVICE_URL || 'http://localhost:4500';
const callLog = [];

// Create our own version of getLocationData to test
const processLocationData = (places, budget) => {
  const LOCATION_DATA = {
    attractions: [],
    food: []
  };

  if (!places) return LOCATION_DATA;

  places.forEach(place => {
    const placeData = {
      name: place.name,
      address: place.address || "",
      rating: place.rating || 0,
      types: place.types || [],
      price_level: place.price_level
    };

    // Basic categorization
    if (place.types?.includes('restaurant') || place.types?.includes('food')) {
      LOCATION_DATA.food.push(placeData);
    } else {
      LOCATION_DATA.attractions.push(placeData);
    }
  });

  return LOCATION_DATA;
};

// The modified version of getLocationData function we want to test
const getLocationData = async (preferences, destination) => {
  const LOCATION_DATA = {
    attractions: [],
    food: []
  };

  try {
    // Mock axios.get to track calls
    const originalAxiosGet = axios.get;
    axios.get = (url, config) => {
      console.log(`API Call Made:`);
      console.log(`  URL: ${url}`);
      console.log(`  Params: ${JSON.stringify(config.params)}`);
      
      callLog.push([url, config]);
      
      // Return mock data
      return Promise.resolve({
        data: {
          results: [
            {
              name: "Test Place",
              address: "123 Test St",
              rating: 4.5,
              types: ["food"],
              price_level: 2
            }
          ]
        }
      });
    };

    // Get places for travel sites
    for (const site of preferences.travelSites) {
      const query = `${site} in ${destination}`;
      const response = await axios.get(`${PLACES_MICROSERVICE_URL}/api/places`, {
        params: {
          location: destination,
          type: query
        }
      });
      
      const processedData = processLocationData(response.data.results, preferences.budget);
      LOCATION_DATA.attractions = [...LOCATION_DATA.attractions, ...processedData.attractions];
      LOCATION_DATA.food = [...LOCATION_DATA.food, ...processedData.food];
    }

    // Handle food places based on dietary preferences
    for (const diet of preferences.diet) {
      if (diet === 'None') {
        // Make a general food query
        const query = `Food in ${destination}`;
        const response = await axios.get(`${PLACES_MICROSERVICE_URL}/api/places`, {
          params: {
            location: destination,
            type: query
          }
        });
        
        const processedData = processLocationData(response.data.results, preferences.budget);
        LOCATION_DATA.food = [...LOCATION_DATA.food, ...processedData.food];
      } else if (diet !== 'Allergy') { // Skip allergy preferences
        // Query for each dietary restriction
        const query = `${diet} Food in ${destination}`;
        const response = await axios.get(`${PLACES_MICROSERVICE_URL}/api/places`, {
          params: {
            location: destination,
            type: query
          }
        });
        
        const processedData = processLocationData(response.data.results, preferences.budget);
        LOCATION_DATA.food = [...LOCATION_DATA.food, ...processedData.food];
      }
    }

    // Restore original axios.get
    axios.get = originalAxiosGet;
    
    return LOCATION_DATA;
  } catch (error) {
    console.error('Error fetching location data:', error);
    return null;
  }
};

// Sample preferences and destination
const testPreferences = {
  travelStyle: ["Active"],
  travelSites: ["Nature Sites", "Cultural Sites"],
  diet: ["Vegetarian", "Vegan"],
  startTime: "08:30",
  endTime: "22:00",
  budget: "MEDIUM"
};

const destination = "Singapore";

// Run the test
async function runTest() {
  try {
    console.log("Testing getLocationData function with:");
    console.log("  Destination:", destination);
    console.log("  Preferences:", JSON.stringify(testPreferences, null, 2));
    
    // Call the function
    const result = await getLocationData(testPreferences, destination);
    
    // Verify correct text queries were constructed
    const expectedTravelSiteQueries = testPreferences.travelSites.map(site => 
      `${site} in ${destination}`
    );
    
    const expectedDietQueries = testPreferences.diet.map(diet => 
      `${diet} Food in ${destination}`
    );
    
    const allExpectedQueries = [...expectedTravelSiteQueries, ...expectedDietQueries];
    const allActualQueries = callLog.map(call => call[1].params.type);
    
    console.log("\nExpected queries:");
    allExpectedQueries.forEach(q => console.log(`  - ${q}`));
    
    console.log("\nActual queries:");
    allActualQueries.forEach(q => console.log(`  - ${q}`));
    
    const missingQueries = allExpectedQueries.filter(q => !allActualQueries.includes(q));
    const unexpectedQueries = allActualQueries.filter(q => !allExpectedQueries.includes(q));
    
    if (missingQueries.length === 0 && unexpectedQueries.length === 0) {
      console.log("\n✅ SUCCESS: All expected queries were made correctly!");
    } else {
      console.log("\n❌ ERROR: Queries do not match expectations!");
      if (missingQueries.length > 0) {
        console.log("  Missing queries:", missingQueries);
      }
      if (unexpectedQueries.length > 0) {
        console.log("  Unexpected queries:", unexpectedQueries);
      }
    }
    
    console.log("\nResult from getLocationData:", JSON.stringify(result, null, 2));
    
    console.log("\nTest complete!");
  } catch (error) {
    console.error("Error during test:", error);
  }
}

runTest(); 