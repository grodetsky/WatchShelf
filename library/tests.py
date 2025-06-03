from django.test import TestCase
from library.tmdb_service import search_movies, get_movie_details, search_tv_shows, get_tv_details


class TMDBClientTest(TestCase):
    def test_movie_search(self):
        """Check if movie search returns results"""
        results = search_movies("Inception")
        self.assertTrue(results, "Movie search returned no results")

    def test_movie_details(self):
        """Check if movie details can be fetched"""
        movie_id = 27205  # Inception
        details = get_movie_details(movie_id)
        self.assertEqual(details.id, movie_id, "Movie ID does not match")

    def test_tv_search(self):
        """Check if TV show search returns results"""
        results = search_tv_shows("Breaking Bad")
        self.assertTrue(results, "TV search returned no results")

    def test_tv_details(self):
        """Check if TV show details can be fetched"""
        tv_id = 1396  # Breaking Bad
        details = get_tv_details(tv_id)
        self.assertEqual(details.id, tv_id, "TV show ID does not match")