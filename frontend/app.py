import streamlit as st
import requests
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static
import pandas as pd

# Configure the app
st.set_page_config(page_title="Tour Planner", layout="wide")

# Constants
API_URL = "http://localhost:8000"

def initialize_session_state():
    """Initialize session state variables."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_itinerary' not in st.session_state:
        st.session_state.current_itinerary = None

def login_page():
    """Display login page."""
    st.title("Tour Planner - Login")
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            # In a real app, verify credentials against a database
            st.session_state.user_id = username
            st.rerun()
            
    with col2:
        st.markdown("### Demo Credentials")
        st.markdown("Username: demo")
        st.markdown("Password: demo123")

def display_chat_interface():
    """Display the chat interface."""
    st.title("Tour Planner Assistant")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Process user input
        try:
            response = requests.post(
                f"{API_URL}/process-input",
                json={"user_id": st.session_state.user_id, "message": prompt}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "itinerary" in data["data"]:
                    st.session_state.current_itinerary = data["data"]["itinerary"]
                    display_itinerary(data["data"]["itinerary"])
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": data["data"].get("response", "I've processed your request.")
                })
                
                st.rerun()
            else:
                st.error("Failed to process your request. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def display_itinerary(itinerary):
    """Display the current itinerary."""
    st.subheader("Your Itinerary")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Schedule", "Map", "Weather"])
    
    with tab1:
        # Display schedule
        for item in itinerary["schedule"]:
            with st.expander(f"{item['time']} - {item['activity']}"):
                st.write(f"🏛️ Location: {item['location']}")
                st.write(f"⏱️ Duration: {item['duration']} minutes")
                st.write(f"🚗 Travel: {item['travel_method']} ({item['travel_time']} min)")
                st.write(f"💰 Cost: ${item['cost']}")
        
        # Display totals
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cost", f"${itinerary['total_cost']}")
        with col2:
            st.metric("Total Distance", f"{itinerary['total_distance']} km")
    
    with tab2:
        # Display map
        display_map(itinerary)
    
    with tab3:
        # Display weather
        display_weather(itinerary.get("city"), itinerary.get("date"))

def display_map(itinerary):
    """Display a folium map with the itinerary locations."""
    # Create a base map centered on the first location
    m = folium.Map(location=[0, 0], zoom_start=13)  # Default location
    
    # Add markers for each location
    locations = []
    for item in itinerary["schedule"]:
        # In a real app, you would geocode the locations
        # This is a placeholder using dummy coordinates
        location = [0, 0]  # Replace with actual coordinates
        locations.append(location)
        
        folium.Marker(
            location,
            popup=item["activity"],
            tooltip=item["location"]
        ).add_to(m)
    
    # Draw path between locations
    if locations:
        folium.PolyLine(
            locations,
            weight=2,
            color='blue',
            opacity=0.8
        ).add_to(m)
    
    # Display the map
    folium_static(m)

def display_weather(city, date):
    """Display weather information."""
    if city and date:
        try:
            response = requests.get(f"{API_URL}/weather", params={"city": city, "date": date})
            if response.status_code == 200:
                weather_data = response.json()["data"]
                st.write(f"Weather forecast for {city} on {date}:")
                st.write(f"Temperature: {weather_data['temperature']}°C")
                st.write(f"Conditions: {weather_data['conditions']}")
                st.write(f"Recommendation: {weather_data['recommendation']}")
            else:
                st.warning("Unable to fetch weather data.")
        except Exception as e:
            st.error(f"Error fetching weather data: {str(e)}")

def main():
    initialize_session_state()
    
    # Show login page if user is not logged in
    if not st.session_state.user_id:
        login_page()
    else:
        # Show main interface
        display_chat_interface()

if __name__ == "__main__":
    main()
