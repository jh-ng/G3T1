<template>
  <div class="travel-form-container">
    <h2>Travel Itinerary Generator</h2>
    <form @submit.prevent="handleSubmit" class="travel-form">
      <div class="form-group">
        <label>Travel Destination:</label>
        <div ref="autocompleteContainer" class="autocomplete-container"></div>
      </div>

      <div class="form-group">
        <label>Number of Travelers:</label>
        <input
          type="number"
          min="1"
          v-model="numTravelers"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label>Budget:</label>
        <select 
          v-model="budget"
          class="form-input"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="very high">Very High</option>
        </select>
      </div>

      <div class="form-group">
        <label>Start Date:</label>
        <input
          type="date"
          v-model="startDate"
          :min="today"
          @change="handleStartDateChange"
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label>End Date:</label>
        <input
          type="date"
          v-model="endDate"
          :min="startDate || today"
          class="form-input"
        />
      </div>

      <button type="submit" class="submit-button">Generate Itinerary</button>
    </form>

    <div v-if="itinerary" class="itinerary-container">
      <h3>Generated Itinerary:</h3>
      <p>{{ itinerary }}</p>
      <button @click="saveItinerary" class="save-button">Save Itinerary</button>
      <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { addressAutocomplete } from '../utils/autocomplete';

export default defineComponent({
  name: 'TravelForm',
  setup() {
    const budget = ref('medium');
    const startDate = ref('');
    const endDate = ref('');
    const destination = ref('');
    const numTravelers = ref(1);
    const itinerary = ref('');
    const saveMessage = ref('');
    const autocompleteContainer = ref(null);
    let cleanup;

    const today = new Date().toISOString().split('T')[0];

    onMounted(() => {
      if (autocompleteContainer.value) {
        cleanup = addressAutocomplete(
          autocompleteContainer.value,
          (data) => {
            if (data) {
              destination.value = data.properties.formatted;
            }
          },
          {
            placeholder: "Enter travel destination",
            apiKey: process.env.VUE_APP_GEOAPIFY_API_KEY || 'ad5c628ef0b34120a4d722598aba6de5'
          }
        );
      }
    });

    onUnmounted(() => {
      if (cleanup) {
        cleanup();
      }
    });

    const handleStartDateChange = () => {
      if (endDate.value && startDate.value > endDate.value) {
        endDate.value = '';
      }
    };

    const saveItinerary = async () => {
      try {
        const response = await axios.post('http://localhost:3000/api/saveItinerary', {
          userID: 'user123',
          itinerary: itinerary.value,
          prompt: "Your generated prompt details here"
        });
        saveMessage.value = response.data.message;
      } catch (error) {
        console.error('Error saving itinerary:', error);
        saveMessage.value = 'Error saving itinerary';
      }
    };

    const handleSubmit = async () => {
      const formData = {
        budget: budget.value,
        startDate: startDate.value,
        endDate: endDate.value,
        destination: destination.value,
        numTravelers: numTravelers.value,
      };

      try {
        const response = await axios.post('http://localhost:3000/api/itinerary', formData);
        itinerary.value = response.data.itinerary;
      } catch (error) {
        console.error('Error generating itinerary:', error);
      }
    };

    return {
      budget,
      startDate,
      endDate,
      destination,
      numTravelers,
      itinerary,
      saveMessage,
      autocompleteContainer,
      today,
      handleStartDateChange,
      saveItinerary,
      handleSubmit
    };
  }
});
</script>

<style scoped>
.travel-form-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.travel-form-container h2 {
  color: #4CAF50;
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
}

.travel-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
}

.form-input {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: #fff;
  color: #2c3e50;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.form-input:hover {
  border-color: #4CAF50;
}

.autocomplete-container {
  position: relative;
  width: 100%;
}

.submit-button, .save-button {
  padding: 12px 24px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 1rem;
}

.submit-button:hover, .save-button:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
}

.submit-button:active, .save-button:active {
  transform: translateY(0);
  box-shadow: none;
}

.itinerary-container {
  margin-top: 2rem;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.itinerary-container h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.save-message {
  margin-top: 1rem;
  color: #4CAF50;
  font-weight: 500;
}

/* Custom styles for date inputs */
input[type="date"] {
  appearance: none;
  -webkit-appearance: none;
  background-color: #fff;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  color: #2c3e50;
  cursor: pointer;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  color: #4CAF50;
  cursor: pointer;
}

/* Custom styles for number input */
input[type="number"] {
  appearance: textfield;
  -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Custom styles for select */
select.form-input {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234CAF50' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1em;
  padding-right: 2.5rem;
  cursor: pointer;
}
</style> 