// Test script for ai-microservice API calls
require('dotenv').config();
const axios = require('axios');

// Create a custom axios instance to track requests
const interceptedCalls = [];
const axiosInstance = axios.create();
axiosInstance.interceptors.request.use(request => {
  interceptedCalls.push({
    url: request.url,
    params: request.params
  });
  return request;
});

// Import app with getLocationData
const app = require('./app');

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
    
    // Temporarily replace axios.get to track calls using our custom instance
    const originalAxiosGet = axios.get;
    axios.get = (url, config) => {
      console.log(`Making API call to: ${url}`);
      console.log(`  with params: ${JSON.stringify(config.params)}`);
      
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
    
    // Call the function
    const result = await app.getLocationData(testPreferences, destination);
    
    // Restore original axios.get
    axios.get = originalAxiosGet;
    
    // Print all calls made
    console.log("\nAPI Calls Summary:");
    console.log(`  Total API calls made: ${interceptedCalls.length}`);
    
    // Analyze calls
    const actualTypeParams = [];
    const callLog = [];
    
    axios.get.mock = { calls: [] };
    axios.get.mock.calls = callLog;
    
    console.log("\nAPI Calls Made:");
    interceptedCalls.forEach((call, index) => {
      console.log(`\nCall ${index + 1}:`);
      console.log(`  URL: ${call.url}`);
      console.log(`  Params: ${JSON.stringify(call.params)}`);
      
      if (call.params && call.params.type) {
        actualTypeParams.push(call.params.type);
      }
      
      // Build call log for later analysis
      callLog.push([call.url, { params: call.params }]);
    });
    
    // Verify correct text queries were constructed
    const expectedTravelSiteQueries = testPreferences.travelSites.map(site => 
      `${site} in ${destination}`
    );
    
    const expectedDietQueries = testPreferences.diet.map(diet => 
      `${diet} Food in ${destination}`
    );
    
    const allExpectedQueries = [...expectedTravelSiteQueries, ...expectedDietQueries];
    const allActualQueries = axios.get.mock.calls.map(call => call[1].params.type);
    
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
    
    // Print the result
    console.log("\nResult from getLocationData:", JSON.stringify(result, null, 2));
    
    console.log("\nTest complete!");
  } catch (error) {
    console.error("Error during test:", error);
  }
}

runTest(); 