"""
Name:       Parker Vangellow
CS230:      Section 4
Data:       Nuclear Explosions 1945-1998
URL:        https://nuclearexplosionspv.streamlit.app/
(Note on URL): I spent a lot of time trying to solve an error telling me there was no module named matplotlib.
I tried adding a requirements.txt to my GitHub Repository but that did not seem to help.
I would really appreciate help with this, so I can publish it. Thank you

Description: This website deals with the nuclear explosion data from 1945-1998.
The opening page has a picture of a nuclear explosion, a fun explosion like screen effect, and the data used for the graphs and charts.
The sidebar opens up with the left arrow and displays a few options for the user to pick.
The first option will take them to two graphs: one that shows all explosion data, and one that lets them pick which country they want to filter it by.
The second option shows them a pie chart of which countries do the most nuclear explosions.
The third shows them a map of all explosions.
The fourth goes through the data to calculate the minimum and max values of the yield of the explosions, and returns the yield, the name of the weapon, and the country that produced it.
Overall this website finds good uses for most of the fields within the data.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
from PIL import Image
import time

# Keeps sidebar closed initially
st.set_page_config(initial_sidebar_state="collapsed")

path = "C:\\Users\\pgjv7\\OneDrive - Bentley University\\Desktop\\CS-230\\parkervangellowfinal.py"

df = pd.read_csv("nuclear_explosions.csv")


# Function to center and underline title, as well as define parameters for explosion effect
st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            text-decoration: underline;
            font-size: 2.5em !important;
        }
        .explosion {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: white;
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 5em;
            animation: fadeOut 2s forwards;
        }
        @keyframes fadeOut {
            0% { opacity: 1; }
            100% { opacity: 0; display: none; }
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="centered-title">Nuclear Explosions</h1>', unsafe_allow_html=True)

# Image
#[PY3] - Try and except for error if user doesn't have the .jpg downloaded
#[ST3] - nuclear bomb image for streamlit widget
try:
    img1 = Image.open("nucbombpic.jpg")
    st.image(img1, width=800)
except FileNotFoundError:
    st.warning("Warning: Nuclear explosion image not found. Proceeding without it.")

# Explosion
#[ST1] - streamlit button tool with explosion effect
if st.button('💥 Simulate Explosion 💥'):
    explosion_placeholder = st.empty()
    explosion_placeholder.markdown(
        '<div class="explosion">💥</div>',
        unsafe_allow_html=True
    )
    time.sleep(2)
    explosion_placeholder.empty()

print(df.info)

#App navigation advice
st.write("Use the arrow on the left side of the screen to access the sidebar to navigate the website!")

#Data filtering and adjustments
#[DA1] - cleaning data with .dropna
#[DA2] - sorting data by descending yield value
df.rename(columns={"Location.Cordinates.Latitude": "lat", "Location.Cordinates.Longitude": "lon"}, inplace=True)
df = df.sort_values(by="Data.Yeild.Upper", ascending=False)
df.dropna(inplace=True)
st.write(df)

#[ST4] - sidebar navigation tool
selected_option = st.sidebar.radio("Please what data you want to view",
                                   ["", "Explosions Over Time", "Explosions by Country", "Map of All Explosions", "Yields" ])

#Define function for different graphs based on country choice
#Left a choice for ALL
#[PY1] - function with default value used twice, once with default value, once without
def exps_time(country="ALL", test_type="ALL"):
    # Filter data based on country selection
    if country != "ALL":
        filtered_df = df[df["WEAPON SOURCE COUNTRY"] == country]
    else:
        filtered_df = df

    # Convert date columns to single date
    #[DA7] - combined data from multiple columns to make one data field of a whole date
    filtered_df['Date'] = pd.to_datetime(filtered_df[['Date.Year', 'Date.Month', 'Date.Day']]
                                         .rename(
        columns={'Date.Year': 'year', 'Date.Month': 'month', 'Date.Day': 'day'}))

    # Group by year and count explosions
    explosions_by_year = filtered_df.groupby(filtered_df['Date'].dt.year).size().reset_index(name='Count')

    # Create the line plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(explosions_by_year['Date'], explosions_by_year['Count'],
            marker='o', linestyle='-', color='red')

    # Customize the plot
    title = f'Nuclear Explosions Over Time ({country})' if country != "ALL" else 'Nuclear Explosions Over Time (All Countries)'
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Explosions', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Display the plot in Streamlit
    st.pyplot(fig)

    # Add some explanatory text
    st.write(
        f"This line graph shows the number of nuclear explosions conducted each year by {country if country != 'ALL' else 'all countries'} from 1945 onwards.")

#[VIZ1] - line graph based on explosions in countries individually
#[VIZ2] - line graph based on explosions in all countries
if selected_option == "Explosions Over Time":
    st.title('Explosions over time')
    #[ST2] selectbox widget
    #[DA4] - filtered by one condition: country
    country_box = st.selectbox("Select a country", ["ALL", "USA", "USSR", "FRANCE", "UK", "CHINA"])

    # Call the function with the selected country
    #[PY1] - function with default value used twice, once with default value, once without
    exps_time(country_box)
    exps_time()
#[VIZ3] - pie chart of explosions by country
elif selected_option == "Explosions by Country":
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Create the pie chart
    df["WEAPON SOURCE COUNTRY"].value_counts().plot(kind="pie", autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')

    st.pyplot(fig)

#[VIZ4] - map visualization of all nuclear explosions
elif selected_option == "Map of All Explosions":
    st.title("Map of All Explosions")

    ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/IncessantBlabber_Radioactive_symbol.png/640px-IncessantBlabber_Radioactive_symbol.png"

    #[PY5] - dictionary with code for different aspects of the icon
    icon_data = {
        "url": ICON_URL,
        "width": 10,
        "height": 10,
        "anchorY": 1
    }

    # Add icons to your dataframe
    df["icon_data"] = None
    for i in df.index:
        df.at[i, "icon_data"] = icon_data


    # Create a layer with your custom icon
    icon_layer = pdk.Layer(type="IconLayer",
                           data=df,
                           get_icon="icon_data",
                           get_position='[lon,lat]',
                           get_size=10,
                           pickable=True)

    # Create a view of the map
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=1,
        pitch=0
    )

    tool_tip = {"html": "Weapon Name:<br/> <b>{Data.Name}</b>",
                "style": {"backgroundColor": "red",
                          "color": "white"}
                }

    icon_map = pdk.Deck(
        map_style='mapbox://styles/mapbox/navigation-day-v1',
        layers=[icon_layer],
        initial_view_state=view_state,
        tooltip=tool_tip
    )

    st.pydeck_chart(icon_map)

if selected_option == "Yields":
    #[PY2] - function returns 6 values
    def Yields(df):

        first_row = df.iloc[0]

        # Initialize with first row's data
        min_yield = first_row['Data.Yeild.Lower']
        max_yield = first_row['Data.Yeild.Upper']
        min_weapon = max_weapon = first_row['Data.Name']
        min_country = max_country = first_row['WEAPON SOURCE COUNTRY']

        #[DA8]-df.iterrows(), iterate through rows of a dataframe
        for index, row in df.iterrows():
            current_lower = row['Data.Yeild.Lower']
            current_upper = row['Data.Yeild.Upper']

            # Skip invalid yields
            if current_upper <= 0:
                continue

            # Check for new min (using lower bound)
            if current_lower < min_yield:
                min_yield = current_lower
                min_weapon = row['Data.Name']
                min_country = row['WEAPON SOURCE COUNTRY']

            # Check for new max (using upper bound)
            if current_upper > max_yield:
                max_yield = current_upper
                max_weapon = row['Data.Name']
                max_country = row['WEAPON SOURCE COUNTRY']

        return min_yield, min_weapon, min_country, max_yield, max_weapon, max_country



    min_y, min_w, min_c, max_y, max_w, max_c = Yields(df)
    #[DA3] - found smallest and largest yields
    if min_y is not None:
        st.write(f"The smallest nuclear test was **{min_w}** with a yield of **{min_y:.1f} kilotons**, conducted by **{min_c}**.")
        st.write("")
        st.write(f"The largest nuclear test was **{max_w}** with a yield of **{max_y:.1f} kilotons**, conducted by **{max_c}**.")
        st.write("A kiloton is a unit of explosive energy, not a unit of mass. It's defined as the amount of energy released by 1,000 tons of TNT when detonated.")
