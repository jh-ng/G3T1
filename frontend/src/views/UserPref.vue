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

    <!-- Start Time - 24hr format -->
    <div class="form-section">
      <label>What time do you prefer starting your day? (24-hour format)</label>
      <div class="time-input-wrapper">
        <select 
          v-model="startHour"
          class="time-select hour-select"
          :class="{ 'required-warning': triedSubmit && !form.start_time }">
          <option value="" disabled>HH</option>
          <option v-for="hour in hours" :key="hour" :value="hour">{{ hour.toString().padStart(2, '0') }}</option>
        </select>
        <span class="time-separator">:</span>
        <select 
          v-model="startMinute"
          class="time-select minute-select"
          :class="{ 'required-warning': triedSubmit && !form.start_time }">
          <option value="" disabled>MM</option>
          <option v-for="minute in minutes" :key="minute" :value="minute">{{ minute.toString().padStart(2, '0') }}</option>
        </select>
      </div>
    </div>

    <!-- End Time - 24hr format -->
    <div class="form-section">
      <label>What time do you prefer your day to end? (24-hour format)</label>
      <div class="time-input-wrapper">
        <select 
          v-model="endHour"
          class="time-select hour-select"
          :class="{ 'required-warning': triedSubmit && !form.end_time }">
          <option value="" disabled>HH</option>
          <option v-for="hour in hours" :key="hour" :value="hour">{{ hour.toString().padStart(2, '0') }}</option>
        </select>
        <span class="time-separator">:</span>
        <select 
          v-model="endMinute"
          class="time-select minute-select"
          :class="{ 'required-warning': triedSubmit && !form.end_time }">
          <option value="" disabled>MM</option>
          <option v-for="minute in minutes" :key="minute" :value="minute">{{ minute.toString().padStart(2, '0') }}</option>
        </select>
      </div>
    </div>

    <!-- Submit -->
    <div class="form-section">
      <button @click="submitPreferences">Submit Preferences</button>
    </div>
  </div>
</template>

<script setup>
import authService from '@/services/auth';
import "vue-select/dist/vue-select.css";
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import { reactive, ref, watch } from 'vue'

const triedSubmit = ref(false)
// Removed unused variables
// const currentUser = authService.getCurrentUser();
// const user = currentUser.id

// Generate hour and minute options
const hours = Array.from({ length: 24 }, (_, i) => i)
const minutes = Array.from({ length: 60 }, (_, i) => i)

// Time selectors
const startHour = ref('')
const startMinute = ref('')
const endHour = ref('')
const endMinute = ref('')

const form = reactive({
  travel_style: [],
  tourist_sites: [],
  diet: [],
  start_time: '',
  end_time: ''
})

// Watch for time changes and update the form
watch([startHour, startMinute], () => {
  if (startHour.value !== '' && startMinute.value !== '') {
    const hour = startHour.value.toString().padStart(2, '0')
    const minute = startMinute.value.toString().padStart(2, '0')
    form.start_time = `${hour}:${minute}`
  } else {
    form.start_time = ''
  }
})

watch([endHour, endMinute], () => {
  if (endHour.value !== '' && endMinute.value !== '') {
    const hour = endHour.value.toString().padStart(2, '0')
    const minute = endMinute.value.toString().padStart(2, '0')
    form.end_time = `${hour}:${minute}`
  } else {
    form.end_time = ''
  }
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
    (form.diet.includes('Allergy') && !form.allergy_detail?.length)
  ) {
    alert('Please fill in all required fields');
    return;
  }

  try {
    // Only update first login status
    await authService.updateFirstLoginStatus();
    alert('Preferences saved successfully!');
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

.time-input-wrapper {
  display: flex;
  align-items: center;
}

.time-select {
  padding: 0.4rem;
  border-radius: 0.3rem;
  border: 1px solid #ccc;
  background-color: rgba(255, 255, 255, 0.801);
  color: black;
}

.hour-select, .minute-select {
  width: 80px;
  text-align: center;
}

.time-separator {
  margin: 0 10px;
  font-weight: bold;
  font-size: 18px;
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

.required-warning {
  border: 1px solid #ff4b2b !important;
}
</style>