from django.test import TestCase
from unittest.mock import Mock, patch
from library.tmdb_service import get_media_by_category, search_media, get_total_pages, get_media_details, MEDIA_TYPES, CATEGORIES


class TMDBClientTest(TestCase):
    def setUp(self):
        # Prepare a dummy handler and results
        self.dummy_item = Mock()
        self.dummy_item.id = 1
        self.dummy_item.title = 'Test Movie'
        self.dummy_item.poster_path = '/test.jpg'

        self.dummy_results = Mock()
        self.dummy_results.results = [self.dummy_item]
        self.dummy_results.total_pages = 5

        self.dummy_handler = Mock()
        self.dummy_handler.popular.return_value = self.dummy_results
        self.dummy_handler.search.return_value = self.dummy_results
        self.dummy_handler.details.return_value = self.dummy_item

        # Patch mappings for 'movie' media type
        self.media_patcher = patch.dict(
            MEDIA_TYPES,
            {'movie': self.dummy_handler},
            clear=False
        )
        self.cat_patcher = patch.dict(
            CATEGORIES,
            {'movie': ['popular']},
            clear=False
        )
        self.media_patcher.start()
        self.cat_patcher.start()

    def tearDown(self):
        self.media_patcher.stop()
        self.cat_patcher.stop()

    def test_get_media_by_category_success(self):
        results = get_media_by_category('movie', 'popular', page=2)
        self.dummy_handler.popular.assert_called_with(page=2)
        expected = [{'id': 1, 'title': 'Test Movie', 'poster_path': '/test.jpg'}]
        self.assertEqual(results, expected)

    def test_get_media_by_category_error(self):
        self.dummy_handler.popular.side_effect = Exception('fail')
        results = get_media_by_category('movie', 'popular', page=1)
        self.assertEqual(results, [])

    def test_search_media_success(self):
        results = search_media('query', 'movie', page=3)
        self.dummy_handler.search.assert_called_with('query', page=3)
        expected = [{'id': 1, 'title': 'Test Movie', 'poster_path': '/test.jpg'}]
        self.assertEqual(results, expected)

    def test_search_media_error(self):
        self.dummy_handler.search.side_effect = Exception('oops')
        results = search_media('q', 'movie', page=1)
        self.assertEqual(results, [])

    def test_get_media_details_success_and_error(self):
        # Success
        item = get_media_details('movie', 42)
        self.dummy_handler.details.assert_called_with(42)
        self.assertEqual(item, self.dummy_item)
        # Error
        self.dummy_handler.details.side_effect = Exception('err')
        self.assertIsNone(get_media_details('movie', 99))

    def test_get_total_pages(self):
        # From category
        pages = get_total_pages(media_type='movie', category='popular')
        self.assertEqual(pages, 5)
        # From query
        pages = get_total_pages(media_type='movie', query='test')
        self.assertEqual(pages, 5)
        # Error path
        self.dummy_handler.popular.side_effect = Exception('fail')
        self.assertEqual(
            get_total_pages('movie', category='popular'),
            1)
