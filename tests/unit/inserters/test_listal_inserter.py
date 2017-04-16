import os
from unittest import TestCase
from unittest.mock import patch

from RatS.inserters.listal_inserter import ListalInserter

TESTDATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'assets'))


class ListalInserterTest(TestCase):
    def setUp(self):
        self.movie = dict()
        self.movie['title'] = 'Fight Club'
        self.movie['year'] = 1999
        self.movie['imdb'] = dict()
        self.movie['imdb']['id'] = 'tt0137523'
        self.movie['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        self.movie['imdb']['my_rating'] = 9
        self.movie['tmdb'] = dict()
        self.movie['tmdb']['id'] = '550'
        self.movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/550'
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'listal.html'), encoding='utf8') as search_result:
            self.search_result = search_result.read()
        with open(os.path.join(TESTDATA_PATH, 'search_result', 'listal_tile.html'), encoding='utf8') as result_tile:
            self.search_result_tile_list = [result_tile.read()]
        with open(os.path.join(TESTDATA_PATH, 'movie_detail_page', 'listal.html'), encoding='utf8') as movie_detail_page:
            self.movie_detail_page = movie_detail_page.read()

    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_init(self, browser_mock, base_init_mock):
        ListalInserter()

        self.assertTrue(base_init_mock.called)

    @patch('RatS.inserters.listal_inserter.ListalInserter._post_movie_rating')
    @patch('RatS.inserters.listal_inserter.print_progress')
    @patch('RatS.inserters.listal_inserter.ListalInserter._is_requested_movie')
    @patch('RatS.inserters.listal_inserter.ListalInserter._get_movie_tiles')
    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_insert(self, browser_mock, base_init_mock, site_mock, overview_page_mock,  # pylint: disable=too-many-arguments
                    eq_check_mock, progress_print_mock, post_rating_mock):
        overview_page_mock.return_value = self.search_result_tile_list
        eq_check_mock.return_value = True
        site_mock.browser = browser_mock
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []

        inserter.insert([self.movie], 'imdb')

        self.assertTrue(base_init_mock.called)
        self.assertTrue(progress_print_mock.called)

    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_imdb_fail(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []

        result = inserter._compare_external_links(self.movie_detail_page, self.movie, 'imdb.com', 'imdb')  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_external_link_compare_imdb_success(self, browser_mock, base_init_mock, site_mock):
        site_mock.browser = browser_mock
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []

        movie2 = dict()
        movie2['title'] = 'The Simpsons'
        movie2['year'] = 2007
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0462538'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0462538'
        movie2['imdb']['my_rating'] = 10

        result = inserter._compare_external_links(self.movie_detail_page, movie2, 'imdb.com', 'imdb')  # pylint: disable=protected-access

        self.assertFalse(result)

    @patch('RatS.inserters.listal_inserter.ListalInserter._compare_external_links')
    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_success_by_imdb(self, browser_mock, base_init_mock, site_mock, compare_mock):
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_result
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []
        compare_mock.return_value = True

        result = inserter._find_movie(self.movie)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.listal_inserter.ListalInserter._is_requested_movie')
    @patch('RatS.inserters.listal_inserter.ListalInserter._compare_external_links')
    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_success_by_year(self, browser_mock, base_init_mock, site_mock, compare_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_result
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []
        compare_mock.return_value = True
        equality_mock.return_value = True

        movie2 = dict()
        movie2['title'] = 'Fight Club'
        movie2['year'] = 1999

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertTrue(result)

    @patch('RatS.inserters.listal_inserter.ListalInserter._is_requested_movie')
    @patch('RatS.inserters.listal_inserter.ListalInserter._get_movie_tiles')
    @patch('RatS.inserters.listal_inserter.ListalInserter._compare_external_links')
    @patch('RatS.inserters.listal_inserter.Listal')
    @patch('RatS.inserters.base_inserter.Inserter.__init__')
    @patch('RatS.sites.base_site.Firefox')
    def test_find_movie_fail(self, browser_mock, base_init_mock, site_mock, compare_mock, tiles_mock, equality_mock):  # pylint: disable=too-many-arguments
        site_mock.browser = browser_mock
        browser_mock.page_source = self.search_result
        inserter = ListalInserter()
        inserter.site = site_mock
        inserter.site.site_name = 'listal'
        inserter.failed_movies = []
        compare_mock.return_value = False
        tiles_mock.return_value = self.search_result_tile_list
        equality_mock.return_value = False

        movie2 = dict()
        movie2['title'] = 'The Matrix'
        movie2['year'] = 1995
        movie2['imdb'] = dict()
        movie2['imdb']['id'] = 'tt0137523'
        movie2['imdb']['url'] = 'http://www.imdb.com/title/tt0137523'
        movie2['imdb']['my_rating'] = 9

        result = inserter._find_movie(movie2)  # pylint: disable=protected-access

        self.assertFalse(result)