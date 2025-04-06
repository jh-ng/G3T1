<template>
  <ItineraryDisplay :itineraryData="itineraryData" />
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ItineraryDisplay from '../components/ItineraryDisplay.vue'

// Dummy data for testing
const DUMMY_DATA = {
  "travel_details": {
    "number_of_travelers": 1,
    "budget": "MEDIUM",
    "start_date": "2025-04-07",
    "end_date": "2025-04-10",
    "daily_start_time": "09:00",
    "daily_end_time": "18:00",
    "user_preferences": {
      "travel_style": ["Active", "Solo"],
      "travel_sites": ["Nature Sites", "Cultural Sites"],
      "dietary_restrictions": ["Halal", "Vegetarian"]
    }
  },
  "2025-04-07": [
    {
      "time": "09:00",
      "location_name": "Gardens by the Bay",
      "description": "Explore the iconic Supertrees and wander through the Cloud Forest and Flower Dome. Experience the OCBC Skyway for stunning views (optional, additional cost).",
      "travel_time_between_locations": "N/A",
      "estimated_duration": "4 hours",
      "notes": "Wear comfortable shoes for walking. Consider purchasing tickets online in advance to avoid queues."
    },
    {
      "time": "13:00",
      "location_name": "蔬升 Ascend Vegetarian (Esplanade Xchange)",
      "description": "Enjoy a Halal & Vegetarian/Vegan lunch",
      "travel_time_between_locations": "30 minutes (from Gardens by the Bay)",
      "estimated_duration": "1 hour",
      "notes": "Halal, Vegetarian & Vegan options. Check opening hours."
    },
    {
      "time": "14:00",
      "location_name": "National Museum of Singapore",
      "description": "Immerse yourself in Singapore's history and culture through interactive exhibits.",
      "travel_time_between_locations": "15 minutes (from Esplanade Xchange)",
      "estimated_duration": "3 hours",
      "notes": "Check for special exhibitions. Can be crowded during peak hours."
    },
    {
      "time": "17:00",
      "location_name": "Merlion Park",
      "description": "Take photos with the iconic Merlion statue and enjoy the waterfront views.",
      "travel_time_between_locations": "15 minutes (from National Museum of Singapore)",
      "estimated_duration": "1 hour",
      "notes": "Great spot for sunset photos."
    }
  ],
  "2025-04-08": [
    {
      "time": "09:00",
      "location_name": "Singapore Botanic Gardens",
      "description": "Explore the UNESCO World Heritage Site, including the National Orchid Garden (additional cost) and the Healing Garden.",
      "travel_time_between_locations": "N/A",
      "estimated_duration": "4 hours",
      "notes": "Wear comfortable shoes. Bring water and sunscreen."
    },
    {
      "time": "13:00",
      "location_name": "Saute & Mee | Anchorvale Village | Seng Kang | Vegetarian Vegan | Local Delights",
      "description": "Enjoy a Halal & Vegetarian/Vegan lunch",
      "travel_time_between_locations": "45 minutes (from Botanic Gardens, assuming travel to Seng Kang)",
      "estimated_duration": "1 hour",
      "notes": "Halal, Vegetarian & Vegan options. Confirm location is suitable given the time of day and other planned activities."
    },
    {
      "time": "14:00",
      "location_name": "Haw Par Villa",
      "description": "Explore the quirky and thought-provoking theme park based on Chinese mythology.",
      "travel_time_between_locations": "60 minutes (from Anchorvale Village)",
      "estimated_duration": "3 hours",
      "notes": "Free admission. Prepare for outdoor walking and potentially hot weather. Can be intense for some visitors."
    },
    {
      "time": "17:00",
      "location_name": "West Coast Park",
      "description": "Wind down the day at West Coast Park with an amazing Sunset at the Grand Lawn.",
      "travel_time_between_locations": "15 minutes (from Haw Par Villa)",
      "estimated_duration": "1 hour",
      "notes": "Perfect for a relaxing evening stroll."
    }
  ],
  "2025-04-09": [
    {
      "time": "09:00",
      "location_name": "Pulau Ubin",
      "description": "Take a bumboat to Pulau Ubin and explore the last 'kampong' (village) in Singapore. Rent a bicycle and cycle through the island's trails.",
      "travel_time_between_locations": "N/A (includes travel to Changi Point Ferry Terminal and boat ride)",
      "estimated_duration": "5 hours",
      "notes": "Bring sunscreen, insect repellent, and water. Bumboat fare is cash only. Wear appropriate clothing and footwear for cycling and hiking."
    },
    {
      "time": "14:00",
      "location_name": "Lazarus Island",
      "description": "After you are done, visit Lazarus Island near St John's Island for scenic beauty.",
      "travel_time_between_locations": "30 minutes",
      "estimated_duration": "4 hours",
      "notes": "Ferry services available till 6 PM from St John's Island. Plan ahead of time."
    },
    {
      "time": "18:00",
      "location_name": "Return to Hotel",
      "description": "Return to your hotel to rest and relax.",
      "travel_time_between_locations": "30 minutes",
      "estimated_duration": "N/A",
      "notes": "Get on last ferry to reach your destination."
    }
  ],
  "2025-04-10": [
    {
      "time": "09:00",
      "location_name": "Sultan Mosque",
      "description": "Visit the majestic Sultan Mosque in Kampong Glam and learn about its history and significance.",
      "travel_time_between_locations": "N/A",
      "estimated_duration": "2 hours",
      "notes": "Dress modestly (shoulders and knees covered). Remove shoes before entering the prayer hall."
    },
    {
      "time": "11:00",
      "location_name": "Malay Heritage Centre",
      "description": "Explore Malay culture and heritage through exhibits and artifacts.",
      "travel_time_between_locations": "5 minutes (walk from Sultan Mosque)",
      "estimated_duration": "2 hours",
      "notes": "Check for special exhibitions and events."
    },
    {
      "time": "13:00",
      "location_name": "Kampong Glam Area (Food options)",
      "description": "Enjoy a Halal lunch at one of the many restaurants in Kampong Glam.",
      "travel_time_between_locations": "N/A",
      "estimated_duration": "1 hour",
      "notes": "Numerous Halal food options available in the area. Explore the side streets for hidden gems."
    },
    {
      "time": "14:00",
      "location_name": "Departure",
      "description": "Head to the airport for your departure.",
      "travel_time_between_locations": "Variable, depending on airport and transportation",
      "estimated_duration": "N/A",
      "notes": "Allow ample time for travel to the airport and check-in procedures."
    }
  ]
}

export default {
  name: 'ItineraryPage',
  components: {
    ItineraryDisplay
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const itineraryData = ref(null)

    onMounted(() => {
      try {
        console.log('ItineraryPage mounted, checking for data...')
        
        // Get data from sessionStorage
        const storedData = sessionStorage.getItem('itineraryData')
        console.log('Raw stored data:', storedData ? storedData.substring(0, 100) + '...' : 'null')
        
        if (storedData) {
          try {
            const parsedData = JSON.parse(storedData)
            console.log('Parsed itinerary data structure:', {
              hasItinerary: !!parsedData.itinerary,
              hasTravelDetails: !!parsedData.travelDetails || !!parsedData.travel_details,
              keys: Object.keys(parsedData)
            })
            
            // Transform data format if needed
            let processedData = parsedData
            
            // If we have raw dates at the top level, restructure to expected format
            const dateLikeKeys = Object.keys(parsedData).filter(key => 
              key.match(/^\d{4}-\d{2}-\d{2}$/) || 
              key.match(/^\d{4}\/\d{2}\/\d{2}$/)
            )
            
            if (dateLikeKeys.length > 0) {
              console.log('Found date-like keys at top level, restructuring data...')
              
              // Extract travel details
              const travelDetails = parsedData.travel_details || parsedData.travelDetails || {}
              
              // Create restructured object
              processedData = {
                travelDetails: travelDetails,
                itinerary: {}
              }
              
              // Add each date to the itinerary
              dateLikeKeys.forEach(date => {
                processedData.itinerary[date] = parsedData[date]
              })
              
              // Log sample activity to check field names
              if (dateLikeKeys.length > 0 && Array.isArray(parsedData[dateLikeKeys[0]]) && parsedData[dateLikeKeys[0]].length > 0) {
                const sampleActivity = parsedData[dateLikeKeys[0]][0]
                console.log('Sample activity field names:', Object.keys(sampleActivity))
                console.log('Sample activity data:', {
                  location: sampleActivity.location,
                  locationName: sampleActivity.locationName,
                  location_name: sampleActivity.location_name,
                  duration: sampleActivity.duration,
                  estimatedDuration: sampleActivity.estimatedDuration,
                  estimated_duration: sampleActivity.estimated_duration,
                  travelTime: sampleActivity.travelTime,
                  travelTimeBetweenLocations: sampleActivity.travelTimeBetweenLocations,
                  travel_time_between_locations: sampleActivity.travel_time_between_locations
                })
              }
              
              console.log('Restructured data:', processedData)
            }
            
            // If no valid data, use dummy data for testing
            if (!processedData || (!processedData.itinerary && !dateLikeKeys.length)) {
              console.warn('No valid itinerary data found, using dummy data')
              
              // Create proper structure from dummy data
              const dummyWithStructure = {
                travelDetails: DUMMY_DATA.travel_details,
                itinerary: {}
              }
              
              // Add each date to the itinerary
              Object.keys(DUMMY_DATA)
                .filter(key => 
                  key.match(/^\d{4}-\d{2}-\d{2}$/) || 
                  key.match(/^\d{4}\/\d{2}\/\d{2}$/)
                )
                .forEach(date => {
                  dummyWithStructure.itinerary[date] = DUMMY_DATA[date]
                })
              
              processedData = dummyWithStructure
              console.log('Using dummy data:', processedData)
            }

            // Set the itinerary data
            itineraryData.value = processedData
            console.log('Final data passed to ItineraryDisplay:', itineraryData.value)
            
          } catch (parseError) {
            console.error('Error parsing stored data:', parseError)
            console.warn('Using dummy data due to parse error')
            
            // Create proper structure from dummy data
            const dummyWithStructure = {
              travelDetails: DUMMY_DATA.travel_details,
              itinerary: {}
            }
            
            // Add each date to the itinerary
            Object.keys(DUMMY_DATA)
              .filter(key => 
                key.match(/^\d{4}-\d{2}-\d{2}$/) || 
                key.match(/^\d{4}\/\d{2}\/\d{2}$/)
              )
              .forEach(date => {
                dummyWithStructure.itinerary[date] = DUMMY_DATA[date]
              })
            
            itineraryData.value = dummyWithStructure
            console.log('Using dummy data after parse error:', itineraryData.value)
          }
        } else {
          // If no stored data, use dummy data
          console.log('No stored itinerary data found, using dummy data')
          
          // Create proper structure from dummy data
          const dummyWithStructure = {
            travelDetails: DUMMY_DATA.travel_details,
            itinerary: {}
          }
          
          // Add each date to the itinerary
          Object.keys(DUMMY_DATA)
            .filter(key => 
              key.match(/^\d{4}-\d{2}-\d{2}$/) || 
              key.match(/^\d{4}\/\d{2}\/\d{2}$/)
            )
            .forEach(date => {
              dummyWithStructure.itinerary[date] = DUMMY_DATA[date]
            })
          
          itineraryData.value = dummyWithStructure
          console.log('Using dummy data in absence of stored data:', itineraryData.value)
        }
      } catch (error) {
        console.error('Error handling data:', error)
        
        // Fallback to dummy data
        console.warn('Falling back to dummy data due to error')
        
        // Create proper structure from dummy data
        const dummyWithStructure = {
          travelDetails: DUMMY_DATA.travel_details,
          itinerary: {}
        }
        
        // Add each date to the itinerary
        Object.keys(DUMMY_DATA)
          .filter(key => 
            key.match(/^\d{4}-\d{2}-\d{2}$/) || 
            key.match(/^\d{4}\/\d{2}\/\d{2}$/)
          )
          .forEach(date => {
            dummyWithStructure.itinerary[date] = DUMMY_DATA[date]
          })
        
        itineraryData.value = dummyWithStructure
      }
    })

    return {
      itineraryData
    }
  }
}
</script> 