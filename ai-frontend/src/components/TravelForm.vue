<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="travel-form-card">
          <div class="form-header">
            <v-icon size="40" color="primary" class="mb-4">mdi-airplane</v-icon>
            <h1 class="text-h3 font-weight-light mb-2">Travel Itinerary Generator</h1>
            <p class="text-subtitle-1 text-medium-emphasis">Plan your perfect trip with AI</p>
          </div>
          
          <v-form @submit.prevent="handleSubmit" class="form-content">
            <div class="location-field mb-6">
              <label class="v-label text-subtitle-2 mb-1">Destination</label>
              <ReactAutocompleteWrapper
                v-model="formData.destination"
                placeholder="Enter a destination"
                @place-selected="handlePlaceSelected"
              />
            </div>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formattedStartDate"
                  label="Start Date"
                  readonly
                  required
                  variant="outlined"
                  :rules="[
                    v => !!v || 'Start date is required',
                    v => new Date(v) >= new Date().setHours(0,0,0,0) || 'Start date cannot be in the past'
                  ]"
                  :min="today"
                  id="startDate"
                  class="rounded-lg date-field"
                  bg-color="surface"
                  style="cursor: pointer"
                  @click="showStartDatePicker = true"
                >
                </v-text-field>
                <v-date-picker
                  v-model="formData.startDate"
                  v-if="showStartDatePicker"
                  :min="today"
                  @update:model-value="showStartDatePicker = false"
                  format="YYYY-MM-DD"
                ></v-date-picker>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formattedEndDate"
                  label="End Date"
                  readonly
                  required
                  variant="outlined"
                  :rules="[
                    v => !!v || 'End date is required',
                    v => !formData.startDate || new Date(v) >= new Date(formData.startDate) || 'End date must be after start date',
                    v => !formData.startDate || (new Date(v) <= new Date(maxEndDate)) || 'Maximum trip duration is 7 days (inclusive)'
                  ]"
                  :min="formattedStartDate"
                  :max="maxEndDate"
                  id="endDate"
                  :disabled="!formattedStartDate"
                  class="rounded-lg date-field"
                  bg-color="surface"
                  style="cursor: pointer"
                  @click="() => { if (formattedStartDate) showEndDatePicker = true }"
                >
                </v-text-field>
                
                <v-date-picker
                  v-model="formData.endDate"
                  v-if="showEndDatePicker"
                  :min="formattedStartDate"
                  :max="maxEndDate"
                  @update:model-value="showEndDatePicker = false"
                  format="YYYY-MM-DD"
                ></v-date-picker>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.numTravelers"
                  label="Number of Travelers"
                  :items="[1,2,3,4,5,6,7,8]"
                  required
                  variant="outlined"
                  :rules="[v => !!v || 'Number of travelers is required']"
                  id="numTravelers"
                  class="rounded-lg"
                  bg-color="surface"
                ></v-select>
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.budget"
                  label="Budget"
                  :items="['Low', 'Medium', 'High', 'Very High']"
                  required
                  variant="outlined"
                  :rules="[v => !!v || 'Budget is required']"
                  id="budget"
                  class="rounded-lg"
                  bg-color="surface"
                ></v-select>
              </v-col>
            </v-row>

            <div class="text-caption text-medium-emphasis mb-6">
              <v-icon size="small" color="info" class="mr-1">mdi-information</v-icon>
              Trip duration is limited to a maximum of 7 days
            </div>

            <v-btn
              type="submit"
              color="primary"
              block
              class="submit-btn"
              :loading="loading"
              :disabled="loading || !formData.destination"
              id="submitBtn"
              size="large"
              elevation="2"
            >
              <v-icon left class="mr-2">mdi-map-marker-path</v-icon>
              Generate Itinerary
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import ReactAutocompleteWrapper from './ReactAutocompleteWrapper.vue'

export default {
  name: 'TravelForm',
  components: {
    ReactAutocompleteWrapper
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const showStartDatePicker = ref(false)
    const showEndDatePicker = ref(false)

    const today = computed(() => {
      const date = new Date()
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    })

    const maxEndDate = computed(() => {
      if (!formData.value.startDate) return null
      try {
        const startDate = new Date(formData.value.startDate)
        const maxDate = new Date(startDate)
        // Add full days to avoid time zone issues
        maxDate.setHours(0, 0, 0, 0)
        maxDate.setDate(startDate.getDate() + 6)
        return `${maxDate.getFullYear()}-${String(maxDate.getMonth() + 1).padStart(2, '0')}-${String(maxDate.getDate()).padStart(2, '0')}`
      } catch (error) {
        console.error('Error calculating max end date:', error)
        return null
      }
    })

    const formData = ref({
      destination: '',
      startDate: '',
      endDate: '',
      numTravelers: 1,
      budget: 'Medium'
    })

    const formatDate = (date) => {
      if (!date) return ''
      // If it's already in YYYY-MM-DD format, return as is
      if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) return date
      // Otherwise, convert to YYYY-MM-DD format
      const d = new Date(date)
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    const formattedStartDate = computed({
      get: () => formatDate(formData.value.startDate),
      set: (val) => { formData.value.startDate = val }
    })

    const formattedEndDate = computed({
      get: () => formatDate(formData.value.endDate),
      set: (val) => { formData.value.endDate = val }
    })

    const handlePlaceSelected = (place) => {
      if (place) {
        console.log('Full Place Response:', place);
        console.log('Place Properties:', {
          formatted: place.properties.formatted,
          name: place.properties.name,
          city: place.properties.city,
          state: place.properties.state,
          country: place.properties.country,
          lat: place.properties.lat,
          lon: place.properties.lon,
          type: place.properties.result_type,
          category: place.properties.category
        });
        
        // Construct a more detailed destination string
        const locationParts = [];
        if (place.properties.name) locationParts.push(place.properties.name);
        if (place.properties.city) locationParts.push(place.properties.city);
        if (place.properties.state) locationParts.push(place.properties.state);
        if (place.properties.country) locationParts.push(place.properties.country);
        
        formData.value.destination = locationParts.join(', ') || place.properties.formatted;
      }
    }

    const handleSubmit = async () => {
      if (!formData.value.destination) {
        alert('Please select a destination')
        return
      }

      if (!formData.value.startDate || !formData.value.endDate) {
        alert('Please select both start and end dates')
        return
      }

      try {
        loading.value = true
        const response = await axios.post('http://localhost:3000/api/itinerary', {
          destination: formData.value.destination,
          startDate: formattedStartDate.value,
          endDate: formattedEndDate.value,
          numTravelers: formData.value.numTravelers,
          budget: formData.value.budget
        })

        // Log the response for debugging
        console.log('API Response:', response.data)

        // Store the complete response data
        sessionStorage.setItem('itineraryData', JSON.stringify(response.data))
        router.push('/itinerary')
      } catch (error) {
        console.error('Error generating itinerary:', error)
        if (error.response?.status === 404) {
          alert('The itinerary generation service is not available. Please make sure the backend server is running.')
        } else {
          alert('Failed to generate itinerary. Please try again.')
        }
      } finally {
        loading.value = false
      }
    }

    const openDatePicker = (event, fieldId) => {
      event.preventDefault();
      const field = document.getElementById(fieldId);
      if (field) {
        const input = field.querySelector('input');
        if (input) {
          input.click();
        }
      }
    };

    const formatDisplayDate = (dateStr) => {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short', 
          day: 'numeric',
          year: 'numeric'
        });
      } catch (error) {
        return dateStr;
      }
    };

    return {
      formData,
      loading,
      handleSubmit,
      handlePlaceSelected,
      today,
      maxEndDate,
      showStartDatePicker,
      showEndDatePicker,
      formattedStartDate,
      formattedEndDate,
      formatDisplayDate
    }
  }
}
</script>

<style scoped>
.fill-height {
  background-color: #f8f9fd;
  padding: 24px;
  width: 100%;
  min-height: 100vh;
  max-width: none;
  margin: 0;
  box-shadow: none;
}

.travel-form-card {
  border: 1px solid rgba(0, 0, 0, 0.07) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
  background: #ffffff;
  padding: 2rem;
}

.travel-form-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05) !important;
}

.form-header {
  text-align: center;
  margin-bottom: 3rem;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 12px;
}

.form-header h1 {
  color: #374151;
  font-weight: 500;
}

.form-header p {
  color: #6a7280;
}

.form-header .v-icon {
  padding: 8px;
  border-radius: 8px;
  background: rgba(106, 128, 224, 0.08);
  color: #6a80e0 !important;
}

.form-content {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 12px;
}

.location-field {
  text-align: left;
  position: relative;
  width: 100%;
  margin-bottom: 1.5rem;
}

.location-field .v-label {
  color: #6a7280;
  font-weight: 500;
  margin-bottom: 4px;
  font-size: 0.875rem;
  margin-left: 16px;
}

.submit-btn {
  margin-top: 2rem;
  height: 48px;
  font-size: 1.1rem;
  text-transform: none;
  letter-spacing: 0.5px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: linear-gradient(90deg, #6a80e0, #8c9eff) !important;
}

.submit-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.15);
}

:deep(.v-field) {
  border-radius: 12px !important;
  transition: all 0.3s ease;
  border: 1px solid rgba(106, 128, 224, 0.15);
}

:deep(.v-field:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.1);
  border-color: rgba(106, 128, 224, 0.3);
}

:deep(.v-field--focused) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.1);
  border-color: rgba(106, 128, 224, 0.5);
  background: linear-gradient(to bottom, #f0f4ff, #ffffff);
}

.location-field :deep(.geoapify-autocomplete-input) {
  width: 100%;
  padding: 16px;
  border: 1px solid rgba(106, 128, 224, 0.15);
  border-radius: 12px;
  background: #ffffff;
  font-family: inherit;
  font-size: 1rem;
  color: #374151;
  transition: all 0.3s ease;
}

.location-field :deep(.geoapify-autocomplete-input:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.1);
  border-color: rgba(106, 128, 224, 0.3);
}

.location-field :deep(.geoapify-autocomplete-input:focus) {
  outline: none;
  border-color: rgba(106, 128, 224, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.1);
  background: linear-gradient(to bottom, #f0f4ff, #ffffff);
}

.location-field :deep(.geoapify-autocomplete-items) {
  background: #ffffff;
  border: 1px solid rgba(106, 128, 224, 0.15);
  border-radius: 12px;
  margin-top: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
}

.location-field :deep(.geoapify-autocomplete-item) {
  padding: 12px 16px;
  cursor: pointer;
  color: #374151;
  transition: background-color 0.2s ease;
}

.location-field :deep(.geoapify-autocomplete-item:hover) {
  background-color: rgba(106, 128, 224, 0.1);
}

.location-field :deep(.geoapify-close-button) {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #6a7280;
  padding: 4px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.location-field :deep(.geoapify-close-button:hover) {
  background-color: rgba(106, 128, 224, 0.08);
}

/* Date field styles */
.date-field :deep(input) {
  color: #374151 !important;
  cursor: pointer;
  opacity: 1 !important;
}

.date-field :deep(.v-field__input) {
  cursor: pointer;
  color: #374151 !important;
  opacity: 1 !important;
}

.date-field :deep(.v-field) {
  cursor: pointer;
}

/* Hide the default calendar picker icon */
.date-field :deep(input[type="date"]::-webkit-calendar-picker-indicator) {
  display: none;
}

.date-field :deep(input[type="date"]) {
  color-scheme: light;
}

/* Fix for disabled state while keeping text visible */
.date-field.v-text-field--disabled :deep(input),
.date-field.v-text-field--disabled :deep(.v-field__input) {
  opacity: 1 !important;
  color: #374151 !important;
}

.date-field.v-text-field--disabled :deep(.v-field) {
  opacity: 1 !important;
}

.date-field.v-text-field--disabled :deep(.v-field--disabled) {
  opacity: 1 !important;
}

.date-field.v-text-field--disabled :deep(.v-field--variant-outlined.v-field--disabled) {
  opacity: 1 !important;
}

.text-caption {
  font-weight: 500;
  color: #6a7280;
  font-size: 0.85rem;
  opacity: 0.9;
}

@media (max-width: 960px) {
  .fill-height {
    padding: 16px;
    border-radius: 0;
  }
  
  .travel-form-card {
    padding: 1.5rem;
  }
  
  .form-content {
    padding: 12px;
  }
}

@media (min-width: 1600px) {
  .fill-height {
    max-width: 1300px;
  }
}
</style> 