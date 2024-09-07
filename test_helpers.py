import unittest
from unittest.mock import patch, MagicMock
from helpers import insert_article_to_mongodb

class TestHelpers(unittest.TestCase):

    @patch('helpers.pymongo.MongoClient')
    def test_insert_article_to_mongodb(self, mock_client):
        # Prepare mock objects
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db

        # Prepare sample data
        sample_data = [
            {'url': 'http://example.com/1', 'title': 'Article 1', 'content': 'Content 1'},
            {'url': 'http://example.com/2', 'title': 'Article 2', 'content': 'Content 2'},
        ]

        # Call the function
        insert_article_to_mongodb(sample_data, 'test_collection', 'test_db')

        # Assert that the function called MongoDB correctly
        mock_client.assert_called_once_with(host="mongodb://localhost:27017/")
        mock_db.__getitem__.assert_called_once_with('test_collection')

        # Assert that update_one was called for each item in the sample data
        self.assertEqual(mock_collection.update_one.call_count, 2)

        # Check the arguments for each call to update_one
        for item in sample_data:
            mock_collection.update_one.assert_any_call(
                {'url': item['url']},
                {'$set': item},
                upsert=True
            )

if __name__ == '__main__':
    unittest.main()