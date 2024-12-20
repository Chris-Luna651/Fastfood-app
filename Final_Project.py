""" Name: Chris Luna
CS230: Section 5
Data: Fast Food Restaurants

Description: This program will be evaluating the Fast Food industry in the U.S.
I will implement queries to help see more depth into the data. I implemented two bar charts, a map,and a pie chart. I hope that with these functions, I am able to explain some information around fast food restaurants in the U.S

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# [PY3] Function with error handling in reading the data
def read_data():
    try:
        df = pd.read_csv('Datafiniti_Fast_Food_Restaurants.csv',header=0).set_index('index')
        return df
    except FileNotFoundError:
        st.error("The dataset file was not found. Please check the file path.")
        return None


# [DA1] Clean the data (remove duplicates, handle missing values)
def clean_data(df):
    # Remove duplicates
    df = df.drop_duplicates()

    # Drop rows with missing critical values (latitude or longitude)
    df = df.dropna(subset=['latitude', 'longitude'])

    # Fill missing optional values with placeholders (e.g., 'Unknown' for province)
    df['province'] = df['province'].fillna('Unknown')
    return df

# Displaying the data in Streamlit
df = read_data()  # Make sure to load the data first

# [PY1] Function with two parameters, one with a default value (called twice)
#[DA4]Filter data by one condition
def filter_data(df, country=None, province=None): # Define a function to filter data based on country and province
    if country and country != "All": # Check if a country is provided and it's not "All"
        df = df[df['country'] == country] # Filter rows where the 'country' column matches the specified country
    if province and province != "All":# Check if a province is provided and it's not "All"
        df = df[df['province'] == province]# Filter rows where the 'province' column matches the specified province
    return df

#[PY2] A function that returns more than one value
def calculate_statistics(df):
    mean_value = df['latitude'].mean()
    median_value = df['latitude'].median()
    return mean_value, median_value


# Function for Query 1: City with the Largest Number of Fast-Food Restaurants
#[VIZ1] Bar Chart
def query_1_city_with_most_restaurants(df):
    st.subheader("Query 1: City with the Largest Number of Fast-Food Restaurants")

    # filtering by country or province
    #[ST1] Select box
    countries = df['country'].unique()
    selected_country = st.selectbox("Filter by Country", options=["All"] + list(countries))

    provinces = df['province'].unique()
    selected_province = st.selectbox("Filter by Province", options=["All"] + list(provinces))

    # Apply the filter based on selected country and province
    #
    filtered_df = filter_data(df, country=selected_country, province=selected_province)

    # Query Logic
    # [DA2] Sort data by the number of restaurants in each city
    #[DA3] Find top values
    city_counts = filtered_df.groupby('city').size().sort_values(ascending=False)
    if not city_counts.empty:
        top_city = city_counts.idxmax()
        top_count = city_counts.max()
        st.write(f"The city with the most fast-food restaurants is **{top_city}** with **{top_count}** restaurants.")

        # Bar chart visualization
        # [VIZ1] Bar chart visualization (with labels, title, colors, etc.)
        fig, ax = plt.subplots(figsize=(10, 6))
        city_counts.head(10).plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title("Top 10 Cities with the Largest Number of Fast-Food Restaurants")
        ax.set_xlabel("City")
        ax.set_ylabel("Number of Restaurants")
        st.pyplot(fig)
    else:
        st.write("No data available for the selected filters.")

# Query 2: Number of Fast-Food Restaurants by State for a Specific Restaurant Name
#[VIZ1] Bar Chart
def query_2_restaurants_by_state(df):
    st.subheader("Query 2: Number of Fast-Food Restaurants by State for a Specific Restaurant Name")

    # filtering by country or province
    # [ST3] Streamlit widgets (dropdowns for country and province, text input for restaurant name)
    countries = df['country'].unique()
    selected_country = st.selectbox("Filter by Country", options=["All"] + list(countries), key="country_selectbox")

    #provinces = df['province'].unique()
    #selected_province = st.selectbox("Filter by Province", options=["All"] + list(provinces), key="province_selectbox")

    # Apply the filter based on selected country and province
    filtered_df = filter_data(df, country=selected_country)# province=selected_province

    # User Input: Restaurant Name
    restaurant_name = st.text_input("Enter the name of the fast-food restaurant (e.g., McDonald's):")

    if restaurant_name:# Check if the user provided a restaurant name
        # Filter Data for the Input Restaurant
        df_restaurant = filtered_df[filtered_df['name'].str.contains(restaurant_name, case=False, na=False)]# Case-insensitive match for the restaurant name


        if not df_restaurant.empty:
            # [ST3] User Input:State Filter
            states = df_restaurant['province'].dropna().unique()# Get unique, non-null state values from the filtered data
            selected_state = st.selectbox("Filter by State", options=["All"] + sorted(states) if states.size > 0 else ["All"], key="state_selectbox") # Unique key for the dropdown widget in Streamlit

            if selected_state != "All":
                df_restaurant = df_restaurant[df_restaurant['province'] == selected_state]

            # Query Logic
            # [DA2] Count the number of restaurants by state
            state_counts = df_restaurant['province'].value_counts()
            st.write(f"Number of **{restaurant_name}** restaurants by state:")

            # Bar Chart Visualization
            # [VIZ1] Bar chart visualization (with labels, title, and colors)
            fig, ax = plt.subplots(figsize=(10, 6))
            state_counts.plot(kind='bar', color='orange', ax=ax) # it tells Pandas to use a specific Axes object (here, ax) to draw the plot.
            ax.set_title(f"Number of {restaurant_name} Restaurants by State", fontsize=14)
            ax.set_xlabel("State", fontsize=12)
            ax.set_ylabel("Number of Restaurants", fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)#Adjusts the transparency of the grid lines (1.0 is opaque, 0.0 is fully transparent).
            plt.xticks(rotation=45, ha='right')# Rotate the x-axis labels by 45 degrees for better readability,'ha' set to 'right' to align the labels to the right of their tick positions
            st.pyplot(fig)
        else:
            st.write(f"No restaurants found for **{restaurant_name}**.")
    else:
        st.write("Please enter a restaurant name to begin the analysis.")

# Query 3: Distribution of Fast-Food Chains by Province (Map Visualization)
#[MAP] Heated map
def query_3_distribution_by_province_map(df):
    st.subheader("Query 3: Geographical Distribution of Fast-Food Locations by Province")

    # filtering by country or province
    # [ST3] Streamlit widgets (dropdowns for country and province)
    countries = df['country'].unique()
    selected_country = st.selectbox("Filter by Country", options=["All"] + list(countries), key="country_map_selectbox")

    provinces = df['province'].unique()
    selected_province = st.selectbox("Select a Province or View All", options=["All"] + sorted(provinces), key="province_map_selectbox")

    # Apply the filter based on selected country and province
    filtered_df = filter_data(df, country=selected_country, province=selected_province)

    # Filter by Selected Province
    if selected_province != "All":
        filtered_df = filtered_df[filtered_df['province'] == selected_province]

    # Check if the DataFrame has valid latitude and longitude data
    # [MAP] Map visualization (location markers for each fast-food restaurant)
    if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns and not filtered_df[['latitude', 'longitude']].dropna().empty:
        # Display Map
        st.write("Geographical distribution of fast-food locations:")
        st.map(filtered_df[['latitude', 'longitude']])
    else:
        st.write("No geographical data available for the selected province or dataset.")

# Query 4: percent of each fastfood restaurant in the U.S
#[VIZ4] Pie chart
def query_4_restaurant_location_distribution(df):
    # Step 1: Preprocess the Data
    # Count the total number of restaurants and group by restaurant name
    restaurant_counts = df['name'].value_counts()
    total_restaurants = restaurant_counts.sum()  # Total number of restaurant locations

    #[DA9] Add/drop columns
    df['Total Amt of Restaurants in the U.S'] = total_restaurants
    # Display the updated DataFrame (for verification)
    #st.write(df.head())

    # Calculate the percentage for each restaurant
    percentages = (restaurant_counts / total_restaurants) * 100

    # Step 2: Visualization Setup
    # Pie chart data
    labels = restaurant_counts.index  # Restaurant names
    sizes = percentages.values        # Percentages
    colors = plt.cm.tab20.colors      # Diverse colors from colormap

    # Combine small slices into an "Others" category for clarity
    top_n = 10  # Display top 10 restaurants
    top_restaurants = restaurant_counts.head(top_n)
    others_count = restaurant_counts[top_n:].sum()

    # Update the pie chart slices for the "Others" category
    labels = list(top_restaurants.index) + ['Others']# Create labels for top restaurants and "Others"
    sizes = list((top_restaurants / total_restaurants) * 100) + [(others_count / total_restaurants) * 100]# Combine sizes for pie chart
    colors = list(colors[:top_n]) + [(0.85, 0.85, 0.85)]  # Convert tuple to list and add gray color(RGB(0.85, 0.85, 0.85)) is for "Others"

    # Step 3: Create the Pie Chart
    fig, ax = plt.subplots(figsize=(10, 7))# Create a figure and axes for the pie chart
    wedges, texts, autotexts = ax.pie(  # Plot the pie chart
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',#Displays the percentage value inside the slices, formatted to 1 decimal place
        startangle=90,#Rotates the pie chart so the first slice starts at the top (90 degrees from the default starting angle)
        textprops={'fontsize': 10} # Font size for the text
    )
    ax.set_title("Distribution of Restaurants in the U.S. by Percentage", fontsize=14)

    # Step 4: Add Legend
    # Format the legend with restaurant names and percentages
    legend_labels = [f"{name}: {percent:.1f}%" for name, percent in zip(labels, sizes)] # Create legend labels,  Combines the labels and sizes lists into pairs, where each label corresponds to its size.
    ax.legend(
        wedges,#The pie slices (or "wedges") in the chart.
        legend_labels,
        title="Restaurant Percentages",
        bbox_to_anchor=(1.05, 1),#Places the legend outside the plot area, slightly to the right. (1.05, 1) specifies the legend’s location relative to the chart.
        loc='upper left', #Positions the legend’s anchor point at the upper-left corner of the legend box.
        fontsize=10
    )

    # Display the pie chart in Streamlit
    st.pyplot(fig)


# Main function
def main():
    # Read the data
    df = read_data()

    if df is not None:
        # Sidebar for navigation
        st.sidebar.title("App Navigation")
        #[ST3] Select Box
        menu = st.sidebar.selectbox("Menu", ["Home", "Query 1", "Query 2", "Query 3", "Query 4"])

        # Display based on selected menu item
        if menu == "Home":
            st.title("Fast Food Restaurants across the USA")
            st.write("Name:Christopher Luna")
            st.write("Welcome to the Fast Food Restaurants analysis app. Use the navigation in the sidebar to explore queries.")
            # Display the image (Food.jpg should be in the same directory as the script or provide full path)
            st.image("Food.jpg", use_container_width=True)
            st.write("In this demonstration, you will learn more about fast-food restaurants in the U.S. Hopefully by the end of this, you will learn something new around the fast food industry.")
        elif menu == "Query 1":
            st.title("Which City has the largest amount of fast food restaurants?")
            query_1_city_with_most_restaurants(df)
            st.write("In this query, you can see which city has the largest amount of fast food restaurants based on what state is picked. For example when you pick the state to be MI, the city with the most amount of restaurants is Grand Rapids with 26 total restaurants.")
        elif menu == "Query 2":
            st.title("Which state has the most number of Taco bell's'?")
            query_2_restaurants_by_state(df)
            st.write("In this query, it allows user to input a restaurant which it will then show all top 10 states with the most amount of that specific restaurant. for example, when a user inputs 'Checkers', the query will show a bar chart where FL is the state with the most number of Checkers and GA being the second state.")
        elif menu == "Query 3":
            query_3_distribution_by_province_map(df)
            st.write("In this query you can see a map visualization where you can see all the restaurants on a map. if the user wants they can pick a specific state in which the map will be zoomed in closely at that state. ")
        elif menu == "Query 4":
            st.title("What is the top fast food chain in the U.S?")
            query_4_restaurant_location_distribution(df)
            st.write("In this query, it is a pie chart in which it shows the top 10 restaurants that the U.S have in percentage. In terms of the total number of fast food restaurants, it shows the amount of a specific restaurant is in the U.S")
        # Run the app

if __name__ == "__main__":
    main()

