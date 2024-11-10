# One-Day Tour Planning Assistant

Welcome to the **One-Day Tour Planning Assistant**! This intelligent chat-driven application is designed to craft personalized, optimized itineraries for one-day trips based on user preferences and external factors like weather and news. Powered by advanced AI and LLM agents, this app integrates multiple services to deliver a seamless planning experience.

## Key Features

- **Chat-Driven Interface**: Interact with an AI chatbot that asks relevant questions about your preferences, destination, and time frame.
- **LLM Agents**:
  - **User Interaction Agent**: Engages with users to understand preferences and requirements.
  - **Itinerary Generation Agent**: Curates an itinerary tailored to user input.
  - **Optimization Agent**: Fine-tunes the itinerary for an optimal experience.
  - **Map Generation Agent**: Provides a visual map of the planned itinerary.
  - **Weather Agent**: Incorporates real-time weather conditions into planning.
  - **News Agent**: Updates users on local news or events that might impact the trip.
  - **Memory Agent**: Stores user preferences for personalized future interactions.
- **Personalization**: The app remembers user preferences to deliver personalized suggestions on repeat visits.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) for the UI interface, making the app easy to use and interactive.
- **Backend**: Built on [FastAPI](https://fastapi.tiangolo.com/) for fast and efficient API responses.
- **Natural Language Processing**: Utilizes [Transformers](https://huggingface.co/transformers/) for language understanding.
- **Database**: [Neo4j](https://neo4j.com/) for managing location data and user interactions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prathamtarjule/Tour_Planner_Assistant.git
   cd Tour_Planner_Assistant
2. Install required libraries
   ```bash
   pip install -r requirements.txt
3. Start the backend API
   ```bash
   cd backend
   uvicorn main:app --reload
4. Start the frontend API
   ```
   cd frontend
   streamlit run app.py
