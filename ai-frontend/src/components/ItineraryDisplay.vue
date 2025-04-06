<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <!-- Travel Details Card -->
        <v-card class="mb-6">
          <v-card-title class="text-h5">{{ travelDetails.destination || 'Travel Details' }}</v-card-title>
          <v-card-text>
            <v-row class="travel-details-row" justify="space-between" no-gutters>
              <v-col cols="12" sm="6" md="3" class="travel-detail-col">
                <div class="travel-detail-card">
                  <v-icon color="primary" class="detail-icon">mdi-calendar</v-icon>
                  <div class="detail-content">
                    <div class="text-subtitle-2">Travel Dates</div>
                    <div>{{ formatDate(travelDetails.start_date) }} - {{ formatDate(travelDetails.end_date) }}</div>
                  </div>
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="3" class="travel-detail-col">
                <div class="travel-detail-card">
                  <v-icon color="primary" class="detail-icon">mdi-account-group</v-icon>
                  <div class="detail-content">
                    <div class="text-subtitle-2">Travelers</div>
                    <div>{{ travelDetails.number_of_travelers }} {{ travelDetails.number_of_travelers === 1 ? 'person' : 'people' }}</div>
                  </div>
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="3" class="travel-detail-col">
                <div class="travel-detail-card">
                  <v-icon color="primary" class="detail-icon">mdi-clock-outline</v-icon>
                  <div class="detail-content">
                    <div class="text-subtitle-2">Daily Schedule</div>
                    <div>{{ travelDetails.daily_start_time }} - {{ travelDetails.daily_end_time }}</div>
                  </div>
                </div>
              </v-col>
              <v-col cols="12" sm="6" md="3" class="travel-detail-col">
                <div class="travel-detail-card">
                  <v-icon color="primary" class="detail-icon">mdi-currency-usd</v-icon>
                  <div class="detail-content">
                    <div class="text-subtitle-2">Budget</div>
                    <div>{{ travelDetails.budget }}</div>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Day Selection and Itinerary integrated in a single card -->
        <v-card class="itinerary-container mb-6">
          <div class="date-tabs-wrapper">
            <div class="date-tabs">
              <button 
                v-for="date in Object.keys(dailyItineraries)" 
                :key="date"
                class="date-tab" 
                :class="{ active: selectedDate === date }"
                @click="selectedDate = date"
              >
                <span class="day">{{ new Date(date).toLocaleDateString('en-US', { weekday: 'short' }) }}</span>
                <span class="date">{{ new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</span>
              </button>
            </div>
          </div>
          
          <div class="itinerary-content">
            <template v-if="Object.keys(dailyItineraries).length">
              <div v-if="selectedDate && dailyItineraries[selectedDate]" class="pt-0">
                <v-timeline density="comfortable">
                  <template v-for="activity in dailyItineraries[selectedDate]" :key="activity.time">
                    <v-timeline-item
                      :dot-color="getTimelineColor(activity)"
                      size="small"
                    >
                      <template v-slot:opposite>
                        <div class="text-caption">{{ activity.time }}</div>
                      </template>
                      <v-card>
                        <v-card-title class="text-h6">
                          {{ activity.locationName || activity.location_name || activity.location || "Unknown Location" }}
                        </v-card-title>
                        <v-card-text>
                          <div v-if="activity.address || activity.location_address" class="text-body-2 text-grey">
                            <v-icon small class="mr-1">mdi-map-marker</v-icon>
                            {{ activity.address || activity.location_address }}
                          </div>
                          <p class="description">{{ activity.description }}</p>
                          <div class="activity-details">
                            <span v-if="getDuration(activity)">
                              <v-icon small class="mr-1">mdi-clock-outline</v-icon>
                              Duration: {{ getDuration(activity) }}
                            </span>
                            <span v-if="getTravelTime(activity)" class="ml-4">
                              <v-icon small class="mr-1">mdi-car</v-icon>
                              Travel time: {{ getTravelTime(activity) }}
                            </span>
                          </div>
                          <div v-if="activity.notes" class="notes">
                            <v-icon small class="mr-1">mdi-information</v-icon>
                            {{ activity.notes }}
                          </div>
                        </v-card-text>
                      </v-card>
                    </v-timeline-item>
                  </template>
                </v-timeline>
              </div>
            </template>
            <div v-else class="text-center py-6">
              <v-icon size="48" color="info" class="mb-2">mdi-information</v-icon>
              <div class="text-h6">No Itinerary Data Available</div>
              <div class="text-body-1">Please generate an itinerary first.</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { computed, ref } from 'vue'

export default {
  name: 'ItineraryDisplay',
  props: {
    itineraryData: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const selectedDate = ref(null)

    console.log('------ ITINERARY DISPLAY DEBUG ------')
    console.log('Raw itineraryData:', props.itineraryData)
    console.log('itineraryData type:', typeof props.itineraryData)
    console.log('itineraryData keys:', props.itineraryData ? Object.keys(props.itineraryData) : 'null')
    
    if (props.itineraryData?.travelDetails) {
      console.log('travelDetails found:', props.itineraryData.travelDetails)
    } else if (props.itineraryData?.travel_details) {
      console.log('travel_details found:', props.itineraryData.travel_details)
    } else {
      console.log('No travel details found in props.itineraryData')
    }
    
    if (props.itineraryData?.itinerary) {
      console.log('Itinerary found:', props.itineraryData.itinerary)
      console.log('Itinerary keys:', Object.keys(props.itineraryData.itinerary))
    } else {
      console.log('No itinerary found in props.itineraryData')
    }

    const travelDetails = computed(() => {
      if (!props.itineraryData) {
        console.log('No itineraryData found')
        return {
          number_of_travelers: 0,
          budget: '-',
          start_date: '-',
          end_date: '-',
          daily_start_time: '-',
          daily_end_time: '-',
          destination: 'Travel Details'
        }
      }
      
      // Try different possible properties for travel details
      const details = props.itineraryData.travelDetails || 
                       props.itineraryData.travel_details || 
                       props.itineraryData || {}
      
      console.log('Using details:', details)
      
      return {
        number_of_travelers: details.numberOfTravelers || details.number_of_travelers || 0,
        budget: details.budget || '-',
        start_date: details.startDate || details.start_date || '-',
        end_date: details.endDate || details.end_date || '-',
        daily_start_time: details.dailyStartTime || details.start_time || details.daily_start_time || '-',
        daily_end_time: details.dailyEndTime || details.end_time || details.daily_end_time || '-',
        destination: details.destination || 'Travel Details'
      }
    })
    
    const dailyItineraries = computed(() => {
      console.log('Computing dailyItineraries...')
      
      // Try different possible properties for itinerary data
      const itineraryData = props.itineraryData?.itinerary || 
                            props.itineraryData?.dailyItineraries || 
                            props.itineraryData || {}
      
      console.log('Using itineraryData:', itineraryData)
      
      if (!itineraryData || Object.keys(itineraryData).length === 0) {
        console.log('No valid itinerary data found')
        return {}
      }
      
      // Filter out any invalid dates and sort them
      const validDates = Object.keys(itineraryData)
        .filter(date => {
          try {
            const isValid = new Date(date).toString() !== 'Invalid Date'
            console.log(`Date ${date} is ${isValid ? 'valid' : 'invalid'}`)
            return isValid
          } catch (e) {
            console.log(`Error parsing date ${date}:`, e)
            return false
          }
        })
        .sort((a, b) => new Date(a) - new Date(b))

      console.log('Valid dates:', validDates)

      // Create a new object with only valid dates
      const validItineraries = {}
      validDates.forEach(date => {
        // Make sure the value is an array
        let activities = itineraryData[date]
        if (!Array.isArray(activities)) {
          console.log(`Activities for ${date} is not an array:`, activities)
          activities = []
        }
        
        // Log the first activity to check its structure
        if (activities.length > 0) {
          console.log(`First activity for ${date}:`, activities[0])
          console.log(`First activity keys:`, Object.keys(activities[0]))
          
          // Log specific fields we're interested in
          const sampleActivity = activities[0]
          console.log('Fields in first activity:', {
            locationNameValue: sampleActivity.locationName,
            location_nameValue: sampleActivity.location_name,
            locationValue: sampleActivity.location,
            durationValue: sampleActivity.duration,
            estimated_durationValue: sampleActivity.estimated_duration,
            estimatedDurationValue: sampleActivity.estimatedDuration,
            travelTimeValue: sampleActivity.travelTime,
            travelTimeBetweenLocationsValue: sampleActivity.travelTimeBetweenLocations,
            travel_time_between_locationsValue: sampleActivity.travel_time_between_locations,
          })
        }
        
        validItineraries[date] = activities
        console.log(`Adding itinerary for ${date} with ${activities.length} activities`)
      })

      // Set initial selected date if not set
      if (!selectedDate.value && validDates.length > 0) {
        console.log('Setting initial selected date to', validDates[0])
        selectedDate.value = validDates[0]
      }

      console.log('Final dailyItineraries:', validItineraries)
      return validItineraries
    })

    const formatDate = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        if (date.toString() === 'Invalid Date') return ''
        return date.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch (error) {
        console.error('Error formatting date:', error)
        return ''
      }
    }

    const formatDateShort = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        if (date.toString() === 'Invalid Date') return ''
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric'
        })
      } catch (error) {
        console.error('Error formatting date:', error)
        return ''
      }
    }

    const getTimelineColor = (activity) => {
      if (!activity?.time) return 'primary'
      try {
        const hour = parseInt(activity.time.split(':')[0])
        if (hour < 12) return 'primary'
        if (hour < 16) return 'success'
        return 'warning'
      } catch (error) {
        console.error('Error getting timeline color:', error)
        return 'primary'
      }
    }

    const getDuration = (activity) => {
      return activity.estimatedDuration || 
             activity.estimated_duration || 
             activity.duration || 
             null
    }

    const getTravelTime = (activity) => {
      return activity.travelTimeBetweenLocations || 
             activity.travel_time_between_locations || 
             activity.travelTime || 
             activity.travel_time || 
             null
    }

    return {
      selectedDate,
      travelDetails,
      dailyItineraries,
      formatDate,
      formatDateShort,
      getTimelineColor,
      getDuration,
      getTravelTime
    }
  }
}
</script>

<style scoped>
.v-container {
  background-color: #f8f9fd;
  border-radius: 12px;
  padding: 24px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
}

.v-card {
  border: 1px solid rgba(0, 0, 0, 0.07) !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03) !important;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.v-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05) !important;
}

/* Travel Details styling */
.travel-details-row {
  margin: 0;
  padding: 16px;
  background-color: #ffffff;
  border-radius: 12px;
}

.travel-detail-col {
  padding: 8px;
}

.travel-detail-card {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  height: 100%;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
}

.travel-detail-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #6a80e0, #8c9eff);
}

.travel-detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  border-color: rgba(106, 128, 224, 0.2);
}

.detail-icon {
  margin-right: 12px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(106, 128, 224, 0.08);
  color: #6a80e0 !important;
}

.detail-content {
  flex: 1;
}

.detail-content .text-subtitle-2 {
  color: #6a7280;
  font-weight: 500;
  margin-bottom: 4px;
  font-size: 0.875rem;
}

.detail-content div:last-child {
  color: #374151;
  font-weight: 500;
  font-size: 1rem;
  line-height: 1.4;
}

/* Integration of dates with itineraries */
.itinerary-container {
  position: relative;
  overflow: visible !important;
}

.date-tabs-wrapper {
  position: relative;
  padding: 20px 16px 0;
  z-index: 5;
}

.date-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  margin-bottom: 10px;
}

.date-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
  height: 56px;
  padding: 8px 16px;
  border-radius: 12px;
  border: 1px solid rgba(106, 128, 224, 0.15);
  background-color: #ffffff;
  color: #6a7280;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.date-tab::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #6a80e0, #8c9eff);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.date-tab:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.1);
  border-color: rgba(106, 128, 224, 0.3);
}

.date-tab:hover::before {
  opacity: 1;
}

.date-tab.active {
  border-color: rgba(106, 128, 224, 0.5);
  background: linear-gradient(to bottom, #f0f4ff, #ffffff);
  font-weight: 600;
  color: #4a6bda;
  box-shadow: 0 4px 12px rgba(106, 128, 224, 0.15);
}

.date-tab.active::before {
  opacity: 1;
  height: 4px;
  background: linear-gradient(90deg, #5c6bc0, #7986cb);
}

.date-tab.active::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-top: 8px solid rgba(106, 128, 224, 0.5);
  z-index: 1;
}

.date-tab .day {
  font-size: 1.1rem;
  margin-bottom: 2px;
}

.date-tab .date {
  font-size: 0.85rem;
  opacity: 0.8;
}

.itinerary-content {
  background-color: #ffffff;
  border-radius: 0 0 12px 12px;
  padding: 24px 16px 16px;
  position: relative;
  z-index: 1;
  border-top: 1px solid rgba(106, 128, 224, 0.1);
  margin-top: 20px;
}

.itinerary-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 16px;
  background: linear-gradient(to bottom, rgba(0,0,0,0.02), rgba(0,0,0,0));
}

/* Timeline styling */
.v-timeline {
  padding: 16px 8px;
  background-color: #ffffff;
  border-radius: 0 0 12px 12px;
  margin-top: 0;
  position: relative;
}

.v-timeline::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 16px;
  background: linear-gradient(to bottom, rgba(0,0,0,0.02), rgba(0,0,0,0));
}

.v-card-text.pt-0 {
  padding-top: 0 !important;
}

.v-card-text.pb-0 {
  padding-bottom: 0 !important;
}

.v-timeline-item {
  margin-bottom: 24px;
  width: 100%;
}

.v-timeline-item .v-card {
  width: calc(100% - 40px);
  margin-left: 20px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
  overflow: hidden;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
  transition: all 0.25s ease;
}

.v-timeline-item .v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06) !important;
}

.v-timeline-item .v-card-title {
  font-size: 1.1rem;
  padding: 16px 20px;
  background: #f8f9fd;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  color: #374151;
  font-weight: 600;
}

.v-timeline-item .v-card-text {
  padding: 16px 20px;
  background-color: #ffffff;
}

.description {
  margin: 12px 0;
  line-height: 1.6;
  color: #4b5563;
  font-size: 1rem;
}

.activity-details {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  background-color: #f8f9fd;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: flex-start;
  gap: 12px;
  width: 100%;
}

.activity-details span {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: #ffffff;
  border: 1px solid rgba(106, 128, 224, 0.15);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
  font-size: 0.9rem;
  color: #4b5563;
  flex: 1;
  min-width: 140px;
  max-width: calc(50% - 12px);
}

.activity-details span:hover {
  background-color: #f0f4ff;
}

.activity-details .v-icon {
  margin-right: 6px;
  color: #6a80e0 !important;
}

.notes {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  background-color: #ebf3fe;
  border: 1px solid rgba(106, 128, 224, 0.15);
  color: #4a6bda;
  font-size: 0.95rem;
}

.text-caption {
  font-weight: 500;
  color: #6a7280;
  width: 50px;
  text-align: right;
  font-size: 0.85rem;
  opacity: 0.9;
}

/* Timeline colors */
.v-timeline-item .v-timeline-divider__dot {
  transition: transform 0.2s ease;
}

.v-timeline-item:hover .v-timeline-divider__dot {
  transform: scale(1.2);
}

/* Add color variations for different times of day */
.v-timeline-item .primary {
  background: linear-gradient(135deg, #6a80e0, #8c9eff);
}

.v-timeline-item .success {
  background: linear-gradient(135deg, #66bb6a, #81c784);
}

.v-timeline-item .warning {
  background: linear-gradient(135deg, #ffa726, #ffb74d);
}

/* Location address styling */
.text-body-2.text-grey {
  color: #9ca3af !important;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.text-body-2.text-grey .v-icon {
  color: #9ca3af;
}

/* Integration of dates with itineraries */
.v-card-title.text-h6 {
  background: linear-gradient(135deg, #6a80e0, #8c9eff);
  color: white;
  font-weight: 500;
  padding: 12px 20px;
  letter-spacing: 0.5px;
  border-radius: 12px 12px 0 0;
  margin-top: 0;
}

.v-btn-group + .v-card {
  margin-top: 0;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.mb-6 {
  margin-bottom: 20px !important;
}

@media (max-width: 960px) {
  .v-container {
    padding: 16px;
    border-radius: 0;
  }

  .travel-detail-col {
    margin-bottom: 8px;
  }
  
  .travel-detail-card {
    padding: 12px;
  }

  .v-timeline-item .v-card {
    width: calc(100% - 24px);
    margin-left: 12px;
  }
  
  .date-tab {
    min-width: 100px;
    padding: 6px 12px;
    height: 50px;
  }
  
  .date-tab .day {
    font-size: 1rem;
  }
  
  .date-tab .date {
    font-size: 0.8rem;
  }
  
  .itinerary-content {
    padding: 20px 12px 12px;
  }
}

@media (min-width: 1600px) {
  .v-container {
    max-width: 1300px;
  }
}
</style> 