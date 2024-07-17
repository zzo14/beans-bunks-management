import unittest
from unittest.mock import patch, MagicMock
from collections import namedtuple
from app.utils import getCursor, closeCursorAndConnection
from .models.Poduct import Product, ProductCategory, Room, ProductVariation

class TestProduct(unittest.TestCase):

    @patch('app.product.models.Poduct.getCursor')
    def test_get_all_products(self, mock_get_cursor):
        # Mock cursor and connection objects
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_cursor.return_value = (mock_cursor, mock_connection)

        # Mock database result
        mock_cursor.fetchall.return_value = [
            (1, 'Product 1', 'Description 1', 10.0, 1, 'image1.jpg', 1, 1),
            (2, 'Product 2', 'Description 2', 15.0, 2, 'image2.jpg', 1, 1)
        ]
        mock_cursor.description = [('product_id',), ('name',), ('description',),
                                   ('price',), ('category_id',), ('image',),
                                   ('is_available',), ('is_inventory',)]

        # Call the static method under test
        products = Product.get_all_products()

        # Assertions
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].product_id, 1)
        self.assertEqual(products[1].name, 'Product 2')

        # Ensure cursor methods were called
        mock_get_cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM product")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('app.product.models.Poduct.getCursor')
    def test_get_products_by_category(self, mock_get_cursor):
        # Mock cursor and connection objects
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_get_cursor.return_value = (mock_cursor, mock_connection)

        # Mock database result
        mock_cursor.fetchall.return_value = [
            (1, 'Product 1', 'Description 1', 10.0, 1, 'image1.jpg', 1, 1),
            (2, 'Product 2', 'Description 2', 15.0, 1, 'image2.jpg', 1, 1)
        ]
        mock_cursor.description = [('product_id',), ('name',), ('description',),
                                   ('price',), ('category_id',), ('image',),
                                   ('is_available',), ('is_inventory',)]

        # Call the static method under test
        products = Product.get_products_by_category(1)

        # Assertions
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].product_id, 1)
        self.assertEqual(products[1].name, 'Product 2')

        # Ensure cursor methods were called
        mock_get_cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM product WHERE category_id = %s AND is_available = 1 AND is_inventory = 1", (1,))
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
