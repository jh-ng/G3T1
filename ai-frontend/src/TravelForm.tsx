import React, { useState } from 'react';
import axios from 'axios';

const TravelForm: React.FC = () => {
  const [budget, setBudget] = useState('medium');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [fromLocation, setFromLocation] = useState('');
  const [toLocation, setToLocation] = useState('');
  // REMOVE responseMessage if you prefer using itinerary
  // const [responseMessage, setResponseMessage] = useState('');
  const [itinerary, setItinerary] = useState('');
  const [saveMessage, setSaveMessage] = useState('');

  // Function to save itinerary
  const saveItinerary = async () => {
    try {
      const response = await axios.post('http://localhost:3000/api/saveItinerary', {
        userID: 'user123', // Replace with the actual user ID as needed
        itinerary,
        prompt: "Your generated prompt details here" // Optionally include the prompt
      });
      setSaveMessage(response.data.message);
    } catch (error) {
      console.error('Error saving itinerary:', error);
      setSaveMessage('Error saving itinerary');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = {
      budget,
      startDate,
      endDate,
      fromLocation,
      toLocation,
    };

    try {
      // Backend on port 3000
      const response = await axios.post('http://localhost:3000/api/itinerary', formData);
      // Store the generated itinerary in state
      setItinerary(response.data.itinerary);
    } catch (error) {
      console.error('Error generating itinerary:', error);
      // Optionally, you could still set a message here for errors
      // setItinerary('Error generating itinerary');
    }
  };

  return (
    <div>
      <h2>Travel Itinerary Generator</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Budget:</label>
          <select value={budget} onChange={(e) => setBudget(e.target.value)}>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <div>
          <label>Start Date:</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        <div>
          <label>End Date:</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
        <div>
          <label>From Location:</label>
          <input
            type="text"
            value={fromLocation}
            onChange={(e) => setFromLocation(e.target.value)}
          />
        </div>
        <div>
          <label>To Location:</label>
          <input
            type="text"
            value={toLocation}
            onChange={(e) => setToLocation(e.target.value)}
          />
        </div>
        <button type="submit">Generate Itinerary</button>
      </form>
      {itinerary && (
        <div>
          <h3>Generated Itinerary:</h3>
          <p>{itinerary}</p>
          <button onClick={saveItinerary}>Save Itinerary</button>
          {saveMessage && <p>{saveMessage}</p>}
        </div>
      )}
    </div>
  );
};

export default TravelForm;
