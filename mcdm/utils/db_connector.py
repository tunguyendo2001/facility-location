import mysql.connector
from config import Config
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Create and return a MySQL database connection
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET
        )
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise


def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] == 1
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

