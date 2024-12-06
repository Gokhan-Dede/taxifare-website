import streamlit as st
from geopy.geocoders import Nominatim
from datetime import datetime
import requests


# Streamlit UI
st.set_page_config(page_title="NYC Taxi Fare Predictor", layout="wide")

# Center the title, description, and estimated fare
st.markdown("""
    <style>
        .title {
            text-align: center;
        }
        .description {
            text-align: center;
            font-size: 18px;
            color: #555555;
        }
    </style>
    <h1 class="title">NYC Taxi Fare Predictor</h1>
    <p class="description">
        This app predicts the fare for a taxi ride in New York City.
        Enter the pickup and drop-off addresses, and the app will display the estimated fare.
    </p>
""", unsafe_allow_html=True)

# Function to geocode the address (convert address to latitude and longitude)
def geocode_address(address):
    geolocator = Nominatim(user_agent="TaxiFareApp")  # The user-agent is required
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        st.error(f"Address '{address}' not found.")
        return None, None


# Sidebar for User Inputs
st.header("Ride Details")


passenger_count = st.select_slider(
    "Passenger Count",
    options=[1, 2, 3, 4, 5, 6, 7, 8],
    value=1,  # Default value
    help="Select the number of passengers for your ride"
)

pickup_address = st.text_input("Pickup Address", "Central Park, New York, NY")
dropoff_address = st.text_input("Drop-off Address", "Times Square, New York, NY")



# Initialize session state for date and time if not already set
if "pickup_time" not in st.session_state:
    st.session_state["pickup_time"] = datetime.now().time()

if "pickup_date" not in st.session_state:
    st.session_state["pickup_date"] = datetime.today().date()

# Use session state values for date and time
pickup_date = st.date_input("Select Pickup Date", st.session_state["pickup_date"])
pickup_time = st.time_input("Select Pickup Time", st.session_state["pickup_time"])

# Update session state values
st.session_state["pickup_date"] = pickup_date
st.session_state["pickup_time"] = pickup_time

# Combine date and time into a single datetime object
pickup_datetime = datetime.combine(pickup_date, pickup_time)



# Button to Trigger Prediction
if st.button("Predict Fare"):
    with st.spinner("Geocoding addresses..."):
        # Geocode Addresses
        pickup_latitude, pickup_longitude = geocode_address(pickup_address)
        dropoff_latitude, dropoff_longitude = geocode_address(dropoff_address)

        # Call your API
        url = 'https://taxifare-api-795064670774.europe-west1.run.app/predict'

        # Prepare the parameters for the API call
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": pickup_longitude,
            "pickup_latitude": pickup_latitude,
            "dropoff_longitude": dropoff_longitude,
            "dropoff_latitude": dropoff_latitude,
            "passenger_count": passenger_count
}

        try:
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for bad status codes
            prediction = response.json()

            # Display the prediction
            fare = prediction.get("fare", "Prediction not available")
            st.metric("Estimated Fare", value=f"${fare:.2f}", label_visibility="visible")
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling the API: {e}")
