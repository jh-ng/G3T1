const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

// Environment variables
const PORT = process.env.PORT || 5400;
const JWT_SECRET = process.env.JWT_SECRET || 'your_jwt_secret';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const ITINERARIES_TABLE = process.env.ITINERARIES_TABLE || 'itineraries';

// Create Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// JWT Authentication middleware
const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).json({ error: 'Authorization header missing' });
  }

  const token = authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Token missing' });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    console.log("JWT Payload:", payload);
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

// Routes
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'itinerary-microservice' });
});

// Direct database test
app.get('/direct-test', async (req, res) => {
  console.log('\n=== Starting Direct Database Test ===');
  console.log('SUPABASE_URL:', SUPABASE_URL ? 'Set' : 'Not set');
  console.log('SUPABASE_KEY:', SUPABASE_KEY ? 'Set' : 'Not set');
  console.log('ITINERARIES_TABLE:', ITINERARIES_TABLE);
  
  try {
    // Test 1: Raw query to list tables
    console.log('\nTest 1: Listing all tables in public schema...');
    const { data: tables, error: tablesError } = await supabase
      .from('pg_tables')
      .select('*')
      .eq('schemaname', 'public');
      
    if (tablesError) {
      console.error('Error listing tables:', tablesError);
    } else {
      console.log('Tables found:', tables);
    }
    
    // Test 2: Direct query on itineraries table
    console.log('\nTest 2: Querying itineraries table...');
    const { data: sample, error: sampleError } = await supabase
      .from('itineraries')
      .select('itineraryID, userID, travelDestination')
      .limit(1);
      
    if (sampleError) {
      console.error('Error querying itineraries:', sampleError);
    } else {
      console.log('Sample data:', sample);
    }
    
    // Test 3: Try an insert
    console.log('\nTest 3: Testing insert...');
    const testData = {
      userID: 7,
      travelDestination: 'Test Destination',
      startDate: new Date().toISOString(),
      endDate: new Date().toISOString(),
      travellers: 1,
      budget: 'TEST',
      dailyStartTime: '09:00',
      dailyEndTime: '17:00',
      geminiResponse: JSON.stringify({ test: true }),
      createdAt: new Date().toISOString()
    };
    
    console.log('Attempting to insert:', testData);
    const { data: insertData, error: insertError } = await supabase
      .from('itineraries')
      .insert(testData)
      .select();
      
    if (insertError) {
      console.error('Insert error:', insertError);
      console.error('Error details:', {
        code: insertError.code,
        message: insertError.message,
        details: insertError.details,
        hint: insertError.hint
      });
    } else {
      console.log('Insert successful:', insertData);
    }
    
    return res.json({
      message: 'Database tests completed',
      tables: tables,
      sample: sample,
      insertResult: insertData || insertError
    });
    
  } catch (error) {
    console.error('Test error:', error);
    return res.status(500).json({
      error: 'Test failed',
      details: error.message,
      stack: error.stack
    });
  }
});

// Simple test endpoint
app.get('/test-db', async (req, res) => {
  try {
    console.log('Testing Supabase connection...');
    console.log('SUPABASE_URL:', SUPABASE_URL ? 'Set' : 'Not set');
    console.log('SUPABASE_KEY:', SUPABASE_KEY ? 'Set' : 'Not set');
    
    // Try a simple query
    const { data, error } = await supabase
      .from('itineraries')
      .select('itineraryID')
      .limit(1);
    
    if (error) {
      console.error('Database error:', error);
      return res.status(500).json({ error: 'Database error', details: error });
    }
    
    return res.status(200).json({
      message: 'Database connection successful',
      data: data
    });
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ error: 'Server error', details: error.message });
  }
});

// Supabase test endpoint
app.get('/api/test-supabase', async (req, res) => {
  try {
    const { data, error } = await supabase
      .from(ITINERARIES_TABLE)
      .select('id')
      .limit(1);

    if (error) {
      return res.status(500).json({ status: 'error', message: 'Supabase connection failed', error });
    }

    return res.status(200).json({ status: 'ok', message: 'Supabase connection successful', data });
  } catch (error) {
    return res.status(500).json({ status: 'error', message: 'Supabase test failed', error: error.message });
  }
});

// Get diagnostic information about the tables
app.get('/api/diagnostic/tables', async (req, res) => {
  try {
    console.log("GET /api/diagnostic/tables");
    console.log("Query params:", req.query);
    console.log("Body:", req.body);

    // List all tables
    const { data: tables, error: tablesError } = await supabase
      .from('pg_tables')
      .select('schemaname, tablename')
      .eq('schemaname', 'public');

    if (tablesError) {
      return res.status(500).json({ error: 'Failed to list tables', details: tablesError });
    }

    // Get itineraries table info
    const { data: itinerariesInfo, error: itinerariesError } = await supabase
      .from(ITINERARIES_TABLE)
      .select('id')
      .limit(1);

    if (itinerariesError) {
      return res.status(500).json({ error: `Failed to query ${ITINERARIES_TABLE}`, details: itinerariesError });
    }

    return res.status(200).json({
      tables: tables,
      itineraries: {
        tableName: ITINERARIES_TABLE,
        exists: true,
        sample: itinerariesInfo
      }
    });
  } catch (error) {
    return res.status(500).json({ error: 'Server error', details: error.message });
  }
});

// Save an itinerary
app.post('/api/itineraries', authenticateJWT, async (req, res) => {
  try {
    const { itinerary, travelDetails } = req.body;
    
    if (!itinerary || !travelDetails) {
      return res.status(400).json({ error: 'Missing itinerary or travel details' });
    }
    
    console.log("\n=== Starting itinerary save ===");
    console.log("Table name:", ITINERARIES_TABLE);
    console.log("User ID:", req.user.user_id);
    console.log("Travel Details:", JSON.stringify(travelDetails, null, 2));
    
    const itineraryData = {
      userID: req.user.user_id,
      travelDestination: travelDetails.destination,
      startDate: travelDetails.startDate || travelDetails.start_date,
      endDate: travelDetails.endDate || travelDetails.end_date,
      travellers: travelDetails.numTravelers || travelDetails.number_of_travelers,
      budget: travelDetails.budget,
      dailyStartTime: travelDetails.dailyStartTime || travelDetails.daily_start_time,
      dailyEndTime: travelDetails.dailyEndTime || travelDetails.daily_end_time,
      geminiResponse: JSON.stringify({
        itinerary: itinerary,
        travelDetails: travelDetails
      }),
      createdAt: new Date().toISOString()
    };
    
    console.log("\nPrepared data for insert:", JSON.stringify(itineraryData, null, 2));
    console.log("\nAttempting to save itinerary...");
    
    const { data, error } = await supabase
      .from(ITINERARIES_TABLE)
      .insert(itineraryData)
      .select();
    
    if (error) {
      console.error('\nError saving itinerary:');
      console.error('Error object:', error);
      console.error('Error code:', error.code);
      console.error('Error message:', error.message);
      console.error('Error details:', error.details);
      console.error('Error hint:', error.hint);
      return res.status(500).json({ 
        error: 'Failed to save itinerary', 
        details: error,
        attempted_data: itineraryData 
      });
    }
    
    console.log("\nItinerary saved successfully!");
    console.log("Saved data:", data);
    
    return res.status(201).json({
      message: 'Itinerary saved successfully',
      itinerary: data[0]
    });
  } catch (error) {
    console.error('\nServer error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message,
      stack: error.stack
    });
  }
});

// Get all itineraries for a user
app.get('/api/itineraries', authenticateJWT, async (req, res) => {
  try {
    const { data, error } = await supabase
      .from(ITINERARIES_TABLE)
      .select('*')
      .eq('userID', req.user.user_id)
      .order('createdAt', { ascending: false });
    
    if (error) {
      console.error('Error fetching itineraries:', error);
      return res.status(500).json({ error: 'Failed to fetch itineraries', details: error });
    }
    
    return res.status(200).json({
      message: 'Itineraries fetched successfully',
      itineraries: data
    });
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Get a specific itinerary by ID
app.get('/api/itineraries/:id', authenticateJWT, async (req, res) => {
  try {
    const { id } = req.params;
    console.log(`Fetching itinerary with ID: ${id}`);
    
    const { data, error } = await supabase
      .from(ITINERARIES_TABLE)
      .select('*')
      .eq('itineraryID', id)
      .eq('userID', req.user.user_id)
      .single();
    
    if (error) {
      console.error('Error fetching itinerary:', error);
      return res.status(404).json({ error: 'Itinerary not found', details: error });
    }
    
    if (!data) {
      console.log('No data found for itinerary');
      return res.status(404).json({ error: 'Itinerary not found' });
    }
    
    console.log('Itinerary data found:', {
      itineraryID: data.itineraryID,
      userID: data.userID,
      travelDestination: data.travelDestination,
      geminiResponseLength: data.geminiResponse ? data.geminiResponse.length : 0,
      hasGeminiResponse: !!data.geminiResponse
    });
    
    // Log the structure of geminiResponse to understand its format
    if (data.geminiResponse) {
      try {
        const parsedResponse = JSON.parse(data.geminiResponse);
        console.log('GeminiResponse structure:', {
          keys: Object.keys(parsedResponse),
          hasItinerary: !!parsedResponse.itinerary,
          itineraryType: parsedResponse.itinerary ? (Array.isArray(parsedResponse.itinerary) ? 'array' : typeof parsedResponse.itinerary) : 'none',
          hasTravelDetails: !!parsedResponse.travelDetails,
          sampleItineraryKeys: parsedResponse.itinerary && Array.isArray(parsedResponse.itinerary) && parsedResponse.itinerary.length > 0 
            ? Object.keys(parsedResponse.itinerary[0]) 
            : []
        });
      } catch (parseError) {
        console.error('Error parsing geminiResponse:', parseError);
      }
    }
    
    return res.status(200).json({
      message: 'Itinerary fetched successfully',
      itinerary: data
    });
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Delete an itinerary
app.delete('/api/itineraries/:id', authenticateJWT, async (req, res) => {
  try {
    const { id } = req.params;
    
    // First check if the itinerary belongs to the user
    const { data: checkData, error: checkError } = await supabase
      .from(ITINERARIES_TABLE)
      .select('itineraryID')
      .eq('itineraryID', id)
      .eq('userID', req.user.user_id)
      .single();
    
    if (checkError || !checkData) {
      console.error('Error checking itinerary ownership:', checkError);
      return res.status(404).json({ 
        error: 'Itinerary not found or you do not have permission to delete it',
        details: checkError
      });
    }
    
    // Proceed with deletion
    const { error: deleteError } = await supabase
      .from(ITINERARIES_TABLE)
      .delete()
      .eq('itineraryID', id)
      .eq('userID', req.user.user_id);
    
    if (deleteError) {
      console.error('Error deleting itinerary:', deleteError);
      return res.status(500).json({ 
        error: 'Failed to delete itinerary', 
        details: deleteError 
      });
    }
    
    return res.status(200).json({
      message: 'Itinerary deleted successfully'
    });
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message 
    });
  }
});

// Test endpoint for Supabase connection
app.get('/api/test-db', async (req, res) => {
  try {
    console.log('Testing database connection...');
    
    // Test 1: List all tables
    console.log('Test 1: Listing tables...');
    const { data: tables, error: tablesError } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public');
    
    if (tablesError) {
      console.error('Error listing tables:', tablesError);
      return res.status(500).json({ error: 'Failed to list tables', details: tablesError });
    }
    
    // Test 2: Try to select from itineraries table
    console.log('Test 2: Querying itineraries table...');
    const { data: itineraries, error: itinerariesError } = await supabase
      .from('itineraries')
      .select('itineraryID')
      .limit(1);
    
    if (itinerariesError) {
      console.error('Error querying itineraries:', itinerariesError);
      return res.status(500).json({ error: 'Failed to query itineraries', details: itinerariesError });
    }
    
    return res.status(200).json({
      message: 'Database connection successful',
      tables: tables,
      itinerariesTest: itineraries
    });
  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({ error: 'Server error', details: error });
  }
});

// Start the server
const server = app.listen(PORT, () => {
  console.log(`Itinerary Microservice running on port ${PORT}`);
});
