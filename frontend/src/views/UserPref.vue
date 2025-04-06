<template>
    <div class="form-container">
      <h1 class="title">Welcome!</h1>
      <p class="description">
        Before you begin your travel planning journey, we would greatly appreciate receiving your preferences to optimize your future itineraries to your liking! You may select more than one option in the first three questions.
      </p>
  
      <!-- Travel Style -->
      <div class="form-section">
        <label>What is your preferred travelling style?</label>
        <Multiselect
          v-model="form.travel_style"
          :options="travelStyles"
          placeholder="Select your travel style"
          multiple
          :class="{ 'required-warning': triedSubmit && !form.travel_style.length }"
        />
      </div> 
  
      <!-- Tourist Sites -->
      <div class="form-section">
        <label>What attractions do you prefer to visit?</label>
        <Multiselect
          v-model="form.tourist_sites"
          :options="touristSites"
          placeholder="Select preferred sites"
          multiple
          :class="{ 'required-warning': triedSubmit && !form.tourist_sites.length }"
        />
      </div>
  
      <!-- Dietary Restrictions -->
      <div class="form-section">
        <label>What dietary restrictions do you have?</label>
        <Multiselect
          v-model="form.diet"
          :options="dietOptions"
          placeholder="Select dietary restrictions"
          multiple
          :class="{ 'required-warning': triedSubmit && !form.diet.length }"
        />
      </div>
  
      <!-- Start Time -->
      <div class="form-section">
        <label>What time do you prefer starting your day?</label>
        <input type="time" v-model="form.start_time" 
        :class="{ 'required-warning': triedSubmit && !form.start_time }"
        />
      </div>
  
      <!-- End Time -->
      <div class="form-section">
        <label>What time do you prefer your day to end?</label>
        <input type="time" v-model="form.end_time" 
        :class="{ 'required-warning': triedSubmit && !form.end_time }"
        />
      </div>
  
      <!-- Submit -->
      <div class="form-section">
        <button @click="submitPreferences">Submit Preferences</button>
      </div>
    </div>
  </template>
  
  <script setup>
  import authService from '@/services/auth';
  // import vSelect from "vue-select";
  import "vue-select/dist/vue-select.css";
  import Multiselect from 'vue-multiselect'
  import 'vue-multiselect/dist/vue-multiselect.min.css'
  import { reactive, ref } from 'vue'
  
  const triedSubmit = ref(false)
  // const token = authService.getToken();
  const currentUser = authService.getCurrentUser();
  const user = currentUser.id 
  
  const form = reactive({
    travel_style: [],
    tourist_sites: [],
    diet: [],
    start_time: '',
    end_time: ''
  })
  
  const travelStyles = ['Active', 'Cultural', 'Family', 'Shopping', 'Solo']
  const touristSites = ['Nature Sites', 'Cultural Sites', 'Leisure Attractions', 'Sports Activities']
  const dietOptions = ['Halal', 'Vegetarian', 'Kosher', 'None']
  

  async function submitPreferences() {
    triedSubmit.value = true

      if (
        !form.travel_style.length ||
        !form.tourist_sites.length ||
        !form.diet.length ||
        !form.start_time ||
        !form.end_time ||
        (form.diet.includes('Allergy') && !form.allergy_detail.length)
      ) {
        alert('Please fill in all required fields');
        return;
      }

  const token = localStorage.getItem('token'); 
  const user_pref_payload = {
    uid: user,
    taste_preferen: form
  };

  try {
    const res = await fetch(`http://localhost:5002/api/user/${user}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(user_pref_payload)
    });

    const result = await res.json();
    if (res.ok) {
      alert('Preferences saved successfully!');
    } else {
      alert('Error: ' + result.error);
    }
  } catch (err) {
    console.error(err);
    alert('Network error');
  }
}
  
  </script>
  
  <style>
  .form-container {
    max-width: 650px;
    margin: 40px auto;
    background: #fff;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    font-family: "Segoe UI", sans-serif;
    color: black;
  }
  
  h1.title {
    text-align: center;
    margin-bottom: 1rem;
    color: #ff4b2b;
  }
  
  p.description {
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
  }
  
  .form-section {
    margin-bottom: 1.5rem;
  }
  
  label {
    display: block;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }
  
  input[type="time"] {
    width: 100%;
    padding: 0.4rem;
    border-radius: 0.3rem;
    border: 1px solid #ccc;
    background-color: rgba(255, 255, 255, 0.801);
    color: black;
  }
  
  input[type="time"]::-webkit-calendar-picker-indicator {
    filter: invert(10);
    opacity: 10;
  }
  
  button {
    background-color: #ff4b2b;
    color: white;
    padding: 0.7rem 1.2rem;
    border: none;
    border-radius: 0.4rem;
    cursor: pointer;
    font-weight: bold;
  }
  
  button:hover {
    background-color: #e43e1b;
  }
  </style>
  