import sqlite3
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Connect to SQLite database
def get_connection():
    return sqlite3.connect('imdb_SQL.db')

# Load dataset from SQLite
def load_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM imdb_movies", conn)
    conn.close()
    return df

st.title("IMDB Movies Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Raw Data", "Tables", "Visualizations", "Filters"])

imdb_movies = load_data()

if page == "Raw Data":
    st.header("Raw Data")
    st.write("### Uploaded Data Preview:")
    st.dataframe(imdb_movies)

elif page == "Tables":
    st.header("Tables")
    imdb_movies = imdb_movies[imdb_movies["Rating"] > 0.0]
    imdb_movies["Rating"] = imdb_movies["Rating"].astype(float)

    sorted_movies = imdb_movies.sort_values(by=["Genre", "Rating"], ascending=[True, False])
    top_rating = sorted_movies.drop_duplicates(subset="Genre", keep="first")[["Genre", "Title", "Rating"]]

    imdb_movies["Duration"] = imdb_movies["Duration"].astype(float).round(2)
    imdb_movies = imdb_movies[imdb_movies["Duration"] > 0.0]

    longest_movies = imdb_movies.loc[imdb_movies.groupby("Genre")["Duration"].idxmax()][["Genre", "Title", "Duration"]]
    shortest_movies = imdb_movies.loc[imdb_movies.groupby("Genre")["Duration"].idxmin()][["Genre", "Title", "Duration"]]

    sample = imdb_movies.nlargest(50, 'Rating')
    top10_genre = sample.nlargest(10, 'Votes')

    st.write("### Top 10 Movies by Rating and Votes")
    st.dataframe(top10_genre)

    st.write("### Top Rated Movie in Each Genre")
    st.dataframe(top_rating)

    st.write("### Longest Movie in Each Genre")
    st.dataframe(longest_movies)

    st.write("### Shortest Movie in Each Genre")
    st.dataframe(shortest_movies)

    overall_longest = imdb_movies.loc[imdb_movies["Duration"].idxmax()][["Genre", "Title", "Duration"]]
    overall_shortest = imdb_movies.loc[imdb_movies["Duration"].idxmin()][["Genre", "Title", "Duration"]]

    st.write("### Overall Shortest and Longest Movies")
    overall_table = pd.DataFrame([overall_shortest, overall_longest])
    st.dataframe(overall_table)

elif page == "Visualizations":
    st.header("Visualizations")

    st.subheader("Genre Distribution: Count of Movies per Genre")
    genre_counts = imdb_movies['Genre'].value_counts()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=genre_counts.index, y=genre_counts.values, palette='viridis')
    plt.xticks(rotation=45)
    plt.title("Count of Movies per Genre")
    st.pyplot(plt)

    st.subheader("Average Duration by Genre")
    avg_duration = imdb_movies.groupby('Genre')['Duration'].mean().sort_values()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=avg_duration.values, y=avg_duration.index, palette='coolwarm')
    plt.xlabel("Average Duration (minutes)")
    plt.title("Average Movie Duration by Genre")
    st.pyplot(plt)

    st.subheader("Average Voting Counts by Genre")
    filtered_data = imdb_movies[imdb_movies['Votes'] > 0]
    avg_votes = filtered_data.groupby('Genre')['Votes'].mean().sort_values()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=avg_votes.index, y=avg_votes.values, palette='magma')
    plt.ylabel("Average Votes")
    plt.xlabel("Genre")
    plt.xticks(rotation=45)
    plt.title("Average Voting Counts by Genre")
    st.pyplot(plt)

    st.subheader("Movie Rating Distribution")
    filtered_ratings = imdb_movies[imdb_movies['Rating'] > 0]
    plt.figure(figsize=(8, 5))
    sns.histplot(filtered_ratings['Rating'], kde=True, color='blue')
    plt.title("Distribution of Movie Ratings")
    st.pyplot(plt)

    st.subheader("Most Popular Genres by Total Votes")
    filtered_genre_votes = imdb_movies[imdb_movies['Votes'] > 0].groupby('Genre')['Votes'].sum()
    plt.figure(figsize=(8, 8))
    plt.pie(filtered_genre_votes, labels=filtered_genre_votes.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.axis('equal')
    plt.title("Most Popular Genres by Total Votes")
    st.pyplot(plt)

    st.subheader("Average Ratings by Genre - Heatmap")
    filtered_movies = imdb_movies[imdb_movies['Rating'] > 0]
    avg_ratings = filtered_movies.groupby('Genre')['Rating'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    heatmap_data = avg_ratings.pivot_table(values='Rating', index='Genre', aggfunc='mean')
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm')
    plt.title("Average Ratings by Genre")
    st.pyplot(plt)

    st.subheader("Correlation Analysis: Ratings vs Votes")
    filtered_movies = imdb_movies[(imdb_movies['Rating'] > 0) & (imdb_movies['Votes'] > 0)]
    plt.figure(figsize=(8, 5))
    sns.scatterplot(x='Rating', y='Votes', data=filtered_movies, alpha=0.6)
    plt.title("Correlation between Ratings and Votes")
    st.pyplot(plt)

elif page == "Filters":
    st.header("Filters Dashboard")
    st.sidebar.subheader("Apply Filters")

    duration_filter = st.sidebar.radio("Select Duration (Hours):", ["< 2 hrs", "2–3 hrs", "> 3 hrs"])
    if duration_filter == "< 2 hrs":
        imdb_movies = imdb_movies[imdb_movies['Duration'] < 120]
    elif duration_filter == "2–3 hrs":
        imdb_movies = imdb_movies[(imdb_movies['Duration'] >= 120) & (imdb_movies['Duration'] <= 180)]
    else:
        imdb_movies = imdb_movies[imdb_movies['Duration'] > 180]

    rating_threshold = st.sidebar.slider("Minimum IMDb Rating:", 0.0, 10.0, 8.0)
    imdb_movies = imdb_movies[imdb_movies['Rating'] >= rating_threshold]

   # Slider for Minimum Votes
    min_votes = st.sidebar.slider("Minimum Votes:", min_value=0, max_value=1000000, value=10000, step=1000)
    imdb_movies = imdb_movies[imdb_movies['Votes'] >= min_votes]

    selected_genre = st.sidebar.multiselect("Select Genres:", imdb_movies['Genre'].unique())
    if selected_genre:
        imdb_movies = imdb_movies[imdb_movies['Genre'].isin(selected_genre)]

    st.write("### Filtered Results")
    st.dataframe(imdb_movies)
