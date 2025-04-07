// Copy this code and execute it in your browser console after logging in
// This will test the token decoding functionality directly with your itinerary microservice

(async function() {
  // Get the JWT token from localStorage
  const token = localStorage.getItem('token');
  
  if (!token) {
    console.error('No JWT token found in localStorage. Please login first.');
    return;
  }
  
  console.log('Retrieved token from localStorage:', token.substring(0, 20) + '...');
  
  try {
    // First try direct access to the itinerary service
    console.log('Attempting direct API call to itinerary service...');
    const response = await fetch('http://localhost:5400/api/verify-token', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ SUCCESS! Token successfully verified:');
      console.log('User ID:', data.user.id);
      console.log('Username:', data.user.username);
      console.log('Full response:', data);
      return;
    } else {
      console.warn(`Direct call failed with status: ${response.status}`);
      const errorText = await response.text();
      console.warn('Error:', errorText);
    }
  } catch (error) {
    console.error('Error making direct request:', error.message);
  }
  
  try {
    // Try through Kong gateway as fallback
    console.log('Attempting API call through Kong gateway...');
    const gatewayResponse = await fetch('http://localhost:8000/api/verify-token', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      mode: 'cors'  // Try with explicit CORS mode
    });
    
    if (gatewayResponse.ok) {
      const gatewayData = await gatewayResponse.json();
      console.log('✅ SUCCESS! Token successfully verified through gateway:');
      console.log('User ID:', gatewayData.user.id);
      console.log('Username:', gatewayData.user.username);
      console.log('Full response:', gatewayData);
    } else {
      console.error(`Gateway call failed with status: ${gatewayResponse.status}`);
      const errorText = await gatewayResponse.text();
      console.error('Error:', errorText);
    }
  } catch (error) {
    console.error('Error making gateway request:', error.message);
    console.log('Try running the server directly and accessing it without the gateway.');
  }
})(); 