from django.test import TestCase
from library.tmdb_service import get_popular_media, get_media_details, search_movies, search_tv_shows


class TMDBServiceTest(TestCase):

    def test_get_popular_media_movies(self):
        """Test fetching popular movies from TMDB"""
        results = get_popular_media(media_type='movie', page=1)
        self.assertIsInstance(results, list, "Expected a list of movies")
        if results:
            self.assertIn('id', results[0], "Each movie should have an 'id'")
            self.assertIn('title', results[0], "Each movie should have a 'title'")
            self.assertIn('poster_path', results[0], "Each movie should have a 'poster_path'")

    def test_get_popular_media_tv_shows(self):
        """Test fetching popular TV shows from TMDB"""
        results = get_popular_media(media_type='tv', page=1)
        self.assertIsInstance(results, list, "Expected a list of TV shows")
        if results:
            self.assertIn('id', results[0], "Each TV show should have an 'id'")
            self.assertIn('title', results[0], "Each TV show should have a 'title'")
            self.assertIn('poster_path', results[0], "Each TV show should have a 'poster_path'")

    def test_get_popular_media_invalid_type(self):
        """Test handling of invalid media type"""
        results = get_popular_media(media_type='invalid', page=1)
        self.assertEqual(results, [], "Invalid media type should return an empty list")

    def test_get_media_details_movie(self):
        """Test fetching details of a specific movie"""
        movie_id = 27205  # Example: Inception
        details = get_media_details(media_type='movie', media_id=movie_id)
        self.assertIsNotNone(details, "Movie details should not be None")
        self.assertEqual(details.id, movie_id, "Returned movie ID should match the requested ID")

    def test_get_media_details_tv(self):
        """Test fetching details of a specific TV show"""
        tv_id = 1396  # Example: Breaking Bad
        details = get_media_details(media_type='tv', media_id=tv_id)
        self.assertIsNotNone(details, "TV show details should not be None")
        self.assertEqual(details.id, tv_id, "Returned TV show ID should match the requested ID")

    def test_get_media_details_invalid_type(self):
        """Test handling of invalid media type for details"""
        details = get_media_details(media_type='invalid', media_id=12345)
        self.assertIsNone(details, "Invalid media type should return None")

    def test_get_media_details_invalid_id(self):
        """Test handling of invalid media ID"""
        details = get_media_details(media_type='movie', media_id=999999999)  # Invalid ID
        self.assertIsNone(details, "Invalid movie ID should return None")

    def test_movie_search(self):
        """Check if movie search returns results"""
        results = search_movies("Inception")
        self.assertTrue(results, "Movie search returned no results")

    def test_tv_search(self):
        """Check if TV show search returns results"""
        results = search_tv_shows("Breaking Bad")
        self.assertTrue(results, "TV search returned no results")
