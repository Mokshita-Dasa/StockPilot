
from db import get_connection


def main():
    connection = None

    try:
        connection = get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")

        result = cursor.fetchone()

        print("MySQL connection successful!")
        print("Database:", result[0])
        print("MySQL version:", result[1])

        cursor.close()

    except Exception as error:
        print("Connection failed:", error)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
