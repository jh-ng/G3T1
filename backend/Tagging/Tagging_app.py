import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime, timedelta
import json
from supabase import create_client, Client

app = FastAPI(title="Location Tagging Microservice")

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Google Places API configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
PLACES_API_BASE_URL = "https://maps.googleapis.com/maps/api/place"
CACHE_EXPIRY_DAYS = 30  # How long to consider location data fresh

# Models
class LocationRequest(BaseModel):
    query: str

class LocationResponse(BaseModel):
    id: str
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    place_types: List[str]
    last_updated: datetime
    additional_metadata: Optional[Dict[str, Any]] = None

class LocationBulkResponse(BaseModel):
    locations: List[LocationResponse]

# Helper functions
async def get_google_place_details(place_id: str) -> Dict[str, Any]:
    """Fetch place details from Google Places API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PLACES_API_BASE_URL}/details/json",
            params={
                "place_id": place_id,
                "fields": "name,formatted_address,geometry,type,place_id",
                "key": GOOGLE_API_KEY
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Google Places API error")
            
        result = response.json()
        if result["status"] != "OK":
            raise HTTPException(status_code=400, detail=f"Google Places API error: {result['status']}")
            
        return result["result"]

async def search_google_places(query: str) -> List[Dict[str, Any]]:
    """Search for places using Google Places API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PLACES_API_BASE_URL}/textsearch/json",
            params={
                "query": query,
                "key": GOOGLE_API_KEY
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Google Places API error")
            
        result = response.json()
        if result["status"] != "OK":
            if result["status"] == "ZERO_RESULTS":
                return []
            raise HTTPException(status_code=400, detail=f"Google Places API error: {result['status']}")
            
        return result["results"]

def is_data_stale(last_updated: datetime) -> bool:
    """Check if the cached data is considered stale"""
    return datetime.now() - last_updated > timedelta(days=CACHE_EXPIRY_DAYS)

def parse_google_place(place_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Google Places API response into our database format"""
    return {
        "place_id": place_data["place_id"],
        "name": place_data["name"],
        "address": place_data.get("formatted_address", ""),
        "latitude": place_data["geometry"]["location"]["lat"],
        "longitude": place_data["geometry"]["location"]["lng"],
        "place_types": place_data.get("types", []),
        "last_updated": datetime.now().isoformat(),
        "additional_metadata": json.dumps({
            "raw_response": place_data
        })
    }

# API Endpoints
@app.get("/locations/search", response_model=LocationBulkResponse)
async def search_locations(query: str):
    """Search for locations by name/address with cache-first approach"""
    # Try to find in database first with case-insensitive search
    db_locations = supabase.table("tagged_locations").select("*").ilike("name", f"%{query}%").execute()
    
    # If we have results and they're not stale, return them
    if db_locations.data:
        fresh_locations = [loc for loc in db_locations.data if not is_data_stale(datetime.fromisoformat(loc["last_updated"]))]
        if fresh_locations:
            return {"locations": fresh_locations}
    
    # Otherwise, search Google Places API
    google_places = await search_google_places(query)
    
    # Store results in database and return them
    stored_locations = []
    for place in google_places:
        parsed_place = parse_google_place(place)
        
        # Check if place_id already exists and update if it does
        existing = supabase.table("tagged_locations").select("*").eq("place_id", parsed_place["place_id"]).execute()
        
        if existing.data:
            # Update existing record
            supabase.table("tagged_locations").update(parsed_place).eq("place_id", parsed_place["place_id"]).execute()
            stored_location = supabase.table("tagged_locations").select("*").eq("place_id", parsed_place["place_id"]).execute().data[0]
        else:
            # Insert new record
            result = supabase.table("tagged_locations").insert(parsed_place).execute()
            stored_location = result.data[0]
        
        stored_locations.append(stored_location)
    
    return {"locations": stored_locations}

@app.get("/locations/{place_id}", response_model=LocationResponse)
async def get_location(place_id: str):
    """Get details for a specific location by place_id"""
    # Try to find in database first
    db_location = supabase.table("tagged_locations").select("*").eq("place_id", place_id).execute()
    
    if db_location.data:
        location = db_location.data[0]
        
        # If data is fresh, return it
        if not is_data_stale(datetime.fromisoformat(location["last_updated"])):
            return location
    
    # Otherwise, get fresh data from Google Places API
    google_place = await get_google_place_details(place_id)
    parsed_place = parse_google_place(google_place)
    
    # Update or insert in database
    if db_location.data:
        supabase.table("tagged_locations").update(parsed_place).eq("place_id", place_id).execute()
        return supabase.table("tagged_locations").select("*").eq("place_id", place_id).execute().data[0]
    else:
        result = supabase.table("tagged_locations").insert(parsed_place).execute()
        return result.data[0]

@app.post("/locations/refresh/{place_id}", response_model=LocationResponse)
async def refresh_location(place_id: str):
    """Force refresh location data from Google Places API"""
    google_place = await get_google_place_details(place_id)
    parsed_place = parse_google_place(google_place)
    
    # Check if it exists first
    existing = supabase.table("tagged_locations").select("*").eq("place_id", place_id).execute()
    
    if existing.data:
        # Update existing record
        supabase.table("tagged_locations").update(parsed_place).eq("place_id", place_id).execute()
        return supabase.table("tagged_locations").select("*").eq("place_id", place_id).execute().data[0]
    else:
        # Insert new record
        result = supabase.table("tagged_locations").insert(parsed_place).execute()
        return result.data[0]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)