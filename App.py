import pickle
import streamlit as st
import requests
import time  # <-- 1. IMPORT TIME MODULE


# 2. ADD STREAMLIT'S CACHE DECORATOR
# This is the most important change. It tells Streamlit to save the result
# of this function. If the same movie_id is requested again, it will use
# the saved poster path instead of calling the API.
@st.cache_data
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=71c3595e63dfa0a2d5b220bc9311653a".format(movie_id)
    try:
        data = requests.get(url)
        data.raise_for_status()  # This will raise an exception for HTTP errors (like 404 Not Found)
        data = data.json()

        # 3. SAFELY GET THE POSTER PATH
        # Use .get() which returns None if 'poster_path' doesn't exist, preventing a crash.
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            # Return a placeholder or None if no poster is found
            return "https://via.placeholder.com/500x750.png?text=No+Poster+Available"

    except requests.exceptions.RequestException as e:
        # Handle cases where the API call itself fails (network error, etc.)
        st.error(f"Error fetching data for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=API+Error"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

        # 4. ADD A SMALL DELAY
        # Be a good citizen to the API by spacing out your requests slightly.
        time.sleep(0.1)

    return recommended_movie_names, recommended_movie_posters


st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie to get a recommendation",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # 5. A MORE EFFICIENT WAY TO DISPLAY COLUMNS
    # This is cleaner than creating each column variable manually.
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])