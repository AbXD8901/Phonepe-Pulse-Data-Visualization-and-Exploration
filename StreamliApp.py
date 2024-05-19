import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
import json

# Function to establish connection with MySQL database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="ur user name",
        password="ur pass",
        database="db name"
    )

# Function to fetch data from MySQL database
def fetch_data(query):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

# Load data from MySQL database
def load_map_data():
    # Define your SQL query to fetch PhonePe Pulse data
    query = "SELECT * FROM map"
    data = fetch_data(query)
    # Convert the fetched data into DataFrame
    df = pd.DataFrame(data, columns=['id', 'state', 'year', 'district', 'type', 'pincode', 'registeredUsers', 'appOpens', 'count', 'amount'])
    return df

# Load GeoJSON file
@st.cache_data
def load_geojson():
    with open('indian_states.geojson') as f:
        geojson_data = json.load(f)
    return geojson_data

# Function to handle each query
def handle_query(query, data, geojson_data):
    if query == "Which state had the highest number of registered users in 2024?":
        result = data[data['year'] == 2024].groupby('state')['registeredUsers'].sum().idxmax()
        return f"The state with the highest number of registered users in 2024 is {result}."
    elif query == "What was the total transaction amount in 2024?":
        total_amount = data[data['year'] == 2024]['amount'].sum()
        return f"The total transaction amount in 2024 was {total_amount}."
    elif query == "Which state saw the highest growth in transaction amount from 2018 to 2023?":
        growth = data.groupby(['state', 'year'])['amount'].sum().unstack().pct_change(axis=1)
        highest_growth_state = growth.idxmax().iloc[-1]
        return f"The state with the highest growth in transaction amount from 2018 to 2023 is {highest_growth_state}."
    elif query == "How did the number of registered users change over the years in each state?":
        fig = px.line(data, x='year', y='registeredUsers', color='state', title='Change in Registered Users Over the Years')
        return fig
    elif query == "What is the average transaction amount per state in 2024?":
        avg_amount = data[data['year'] == 2024].groupby('state')['amount'].mean()
        fig = px.bar(avg_amount, x=avg_amount.index, y=avg_amount.values, labels={'x': 'State', 'y': 'Average Transaction Amount'}, title='Average Transaction Amount per State in 2024')
        return fig
    elif query == "Which district had the highest number of transactions in 2024?":
        result = data[data['year'] == 2024].groupby('district')['count'].sum().idxmax()
        return f"The district with the highest number of transactions in 2024 is {result}."
    elif query == "What was the trend in app opens from 2018 to 2023?":
        fig = px.line(data, x='year', y='appOpens', title='Trend in App Opens from 2018 to 2023')
        return fig
    elif query == "Which state had the highest number of app opens in 2024?":
        result = data[data['year'] == 2024].groupby('state')['appOpens'].sum().idxmax()
        return f"The state with the highest number of app opens in 2024 is {result}."
    elif query == "How did the transaction count change over the years in each state?":
        fig = px.line(data, x='year', y='count', color='state', title='Change in Transaction Count Over the Years')
        return fig
    elif query == "What is the median transaction amount per state in 2024?":
        median_amount = data[data['year'] == 2024].groupby('state')['amount'].median()
        fig = px.bar(median_amount, x=median_amount.index, y=median_amount.values, labels={'x': 'State', 'y': 'Median Transaction Amount'}, title='Median Transaction Amount per State in 2024')
        return fig
    elif query == "Which state had the lowest number of registered users in 2024?":
        result = data[data['year'] == 2024].groupby('state')['registeredUsers'].sum().idxmin()
        return f"The state with the lowest number of registered users in 2024 is {result}."
    elif query == "Which district had the lowest number of transactions in 2024?":
        result = data[data['year'] == 2024].groupby('district')['count'].sum().idxmin()
        return f"The district with the lowest number of transactions in 2024 is {result}."
    elif query == "Which pincode area saw the lowest amount of transactions in 2024?":
        result = data[data['year'] == 2024].groupby('pincode')['amount'].sum().idxmin()
        return f"The pincode area with the lowest amount of transactions in 2024 is {result}."
    elif query == "What was the total number of transactions in 2024?":
        total_count = data[data['year'] == 2024]['count'].sum()
        return f"The total number of transactions in 2024 was {total_count}."
    else:
        return "This query is not available."

# Function for the second page
def second_page():
    st.title("Important Queries for Analysis")

    # List of important questions
    questions = [
        "Which state had the highest number of registered users in 2024?",
        "What was the total transaction amount in 2024?",
        "Which state saw the highest growth in transaction amount from 2018 to 2023?",
        "How did the number of registered users change over the years in each state?",
        "What is the average transaction amount per state in 2024?",
        "Which district had the highest number of transactions in 2024?",
        "What was the trend in app opens from 2018 to 2023?",
        "Which state had the highest number of app opens in 2024?",
        "How did the transaction count change over the years in each state?",
        "What is the median transaction amount per state in 2024?",
        "Which state had the lowest number of registered users in 2024?",
        "Which district had the lowest number of transactions in 2024?",
        "Which pincode area saw the lowest amount of transactions in 2024?",
        "What was the total number of transactions in 2024?"
    ]

    selected_question = st.selectbox("Select a Question", questions)
    
    if st.button("Enlighten!"):
        data = load_map_data()
        geojson_data = load_geojson()
        answer = handle_query(selected_question, data, geojson_data)
        if isinstance(answer, str):
            st.write(answer)
        else:
            st.plotly_chart(answer)

# Main function for the app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main Page", "Important Queries"])

    if page == "Main Page":
        st.title("PhonePe Pulse Data Visualization")

        # Load map data initially
        data = load_map_data()

        # Convert state names to uppercase
        data['state'] = data['state'].str.upper()

        # Load GeoJSON data
        geojson_data = load_geojson()

        # Sidebar Filters
        st.sidebar.header("Filters")

        # State filter
        selected_state = st.sidebar.selectbox("Select State", data['state'].unique())

        # Category filter
        transaction_or_user = st.sidebar.selectbox("Select Category", ['transaction', 'registeredUsers'])

        # Button to visualize the map
        if st.sidebar.button("Visualize !"):
            filtered_data = data[(data['state'] == selected_state) & (data['year'] == 2024)]

            # Set the color column based on the filter selection
            color_column = 'amount' if transaction_or_user == 'transaction' else 'registeredUsers'

            # Display the map
            st.subheader(f"{transaction_or_user.capitalize()} Data for {selected_state} in 2024")
            fig = px.choropleth_mapbox(
                filtered_data,
                geojson=geojson_data,
                locations='state',
                featureidkey="properties.STATE",
                color=color_column,
                color_continuous_scale="Viridis",
                mapbox_style="carto-positron",
                zoom=5,
                center={"lat": 20.5937, "lon": 78.9629},
                opacity=0.5,
                labels={color_column: 'Value'}
            )
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig)

            # Display the bar chart for the selected state over the years
            yearly_data = data[(data['state'] == selected_state) & (data['year'].between(2018, 2023))]
            # Display the bar chart for data over the years
            st.subheader(f"{transaction_or_user.capitalize()} Data for {selected_state} (2018-2023)")
            yearly_data = data[(data['state'] == selected_state) & (data['year'] <= 2023)]
            yearly_summary = yearly_data.groupby('year')[color_column].sum().reset_index()
            bar_fig = px.bar(yearly_summary, x='year', y=color_column, title=f"{transaction_or_user.capitalize()} Data Over the Years for {selected_state}", text=color_column)
            bar_fig.update_traces(marker_color='blue', texttemplate='%{text:.2s}', textposition='outside')
            bar_fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', xaxis_title='Year', yaxis_title=transaction_or_user.capitalize())
            st.plotly_chart(bar_fig)

    elif page == "Important Queries":
        second_page()

if __name__ == "__main__":
    main()
