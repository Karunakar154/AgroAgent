import sqlite3
import json
import os


# ==================================================
# DATABASE LOCATION
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "agroagent.db"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_PATH
    )


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # ==================================================
    # FARMERS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (

            farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT UNIQUE,

            email TEXT UNIQUE,

            password_hash TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # ==================================================
    # MIGRATE OLD FARMERS TABLE
    # ==================================================

    cursor.execute("""
        PRAGMA table_info(farmers)
    """)

    farmer_columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    if "password_hash" not in farmer_columns:

        cursor.execute("""
            ALTER TABLE farmers
            ADD COLUMN password_hash TEXT
        """)


    # ==================================================
    # FARMS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farms (

            farm_id INTEGER PRIMARY KEY AUTOINCREMENT,

            farmer_id INTEGER NOT NULL,

            farm_name TEXT,

            latitude REAL,

            longitude REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (farmer_id)
                REFERENCES farmers(farmer_id)

        )
    """)


    # ==================================================
    # CONVERSATIONS
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            session_id TEXT PRIMARY KEY,

            farmer_id INTEGER,

            farm_id INTEGER,

            user_query TEXT,

            farmer_context TEXT,

            tool_results TEXT,

            FOREIGN KEY (farmer_id)
                REFERENCES farmers(farmer_id),

            FOREIGN KEY (farm_id)
                REFERENCES farms(farm_id)

        )
    """)


    # ==================================================
    # MIGRATE OLD CONVERSATIONS TABLE
    # ==================================================

    cursor.execute("""
        PRAGMA table_info(conversations)
    """)

    conversation_columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    if "farmer_id" not in conversation_columns:

        cursor.execute("""
            ALTER TABLE conversations
            ADD COLUMN farmer_id INTEGER
        """)


    if "farm_id" not in conversation_columns:

        cursor.execute("""
            ALTER TABLE conversations
            ADD COLUMN farm_id INTEGER
        """)


    # ==================================================
    # MESSAGES
    # ==================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            role TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (session_id)
                REFERENCES conversations(session_id)

        )
    """)


    connection.commit()

    connection.close()


# ==================================================
# CREATE FARMER
# ==================================================

def create_farmer(
    name,
    phone=None,
    email=None,
    password_hash=None
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO farmers
        (
            name,
            phone,
            email,
            password_hash
        )

        VALUES (?, ?, ?, ?)
    """, (

        name,
        phone,
        email,
        password_hash

    ))


    farmer_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return farmer_id


# ==================================================
# GET FARMER
# ==================================================

def get_farmer(
    farmer_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            farmer_id,
            name,
            phone,
            email,
            created_at

        FROM farmers

        WHERE farmer_id = ?
    """, (
        farmer_id,
    ))


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return {

        "farmer_id":
        row[0],

        "name":
        row[1],

        "phone":
        row[2],

        "email":
        row[3],

        "created_at":
        row[4]

    }


# ==================================================
# GET FARMER BY EMAIL
# ==================================================

def get_farmer_by_email(
    email
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            farmer_id,
            name,
            phone,
            email,
            password_hash,
            created_at

        FROM farmers

        WHERE email = ?
    """, (
        email,
    ))


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return {

        "farmer_id":
        row[0],

        "name":
        row[1],

        "phone":
        row[2],

        "email":
        row[3],

        "password_hash":
        row[4],

        "created_at":
        row[5]

    }


# ==================================================
# CREATE FARM
# ==================================================

def create_farm(
    farmer_id,
    farm_name,
    latitude=None,
    longitude=None
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO farms
        (
            farmer_id,
            farm_name,
            latitude,
            longitude
        )

        VALUES (?, ?, ?, ?)
    """, (

        farmer_id,

        farm_name,

        latitude,

        longitude

    ))


    farm_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return farm_id


# ==================================================
# GET FARM
# ==================================================

def get_farm(
    farm_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            farm_id,
            farmer_id,
            farm_name,
            latitude,
            longitude,
            created_at

        FROM farms

        WHERE farm_id = ?
    """, (
        farm_id,
    ))


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return {

        "farm_id":
        row[0],

        "farmer_id":
        row[1],

        "farm_name":
        row[2],

        "latitude":
        row[3],

        "longitude":
        row[4],

        "created_at":
        row[5]

    }


# ==================================================
# GET FARMER FARMS
# ==================================================

def get_farmer_farms(
    farmer_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            farm_id,
            farm_name,
            latitude,
            longitude,
            created_at

        FROM farms

        WHERE farmer_id = ?

        ORDER BY farm_id ASC
    """, (
        farmer_id,
    ))


    rows = cursor.fetchall()

    connection.close()


    return [

        {

            "farm_id":
            row[0],

            "farm_name":
            row[1],

            "latitude":
            row[2],

            "longitude":
            row[3],

            "created_at":
            row[4]

        }

        for row in rows

    ]


# ==================================================
# SAVE MEMORY
# ==================================================

def save_memory(
    session_id,
    user_query,
    farmer_context,
    tool_results,
    farmer_id=None,
    farm_id=None
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT OR REPLACE INTO conversations
        (
            session_id,
            farmer_id,
            farm_id,
            user_query,
            farmer_context,
            tool_results
        )

        VALUES (?, ?, ?, ?, ?, ?)
    """, (

        session_id,

        farmer_id,

        farm_id,

        user_query,

        json.dumps(
            farmer_context
        ),

        json.dumps(
            tool_results
        )

    ))


    connection.commit()

    connection.close()


# ==================================================
# GET MEMORY
# ==================================================

def get_memory(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            user_query,
            farmer_context,
            tool_results,
            farmer_id,
            farm_id

        FROM conversations

        WHERE session_id = ?
    """, (
        session_id,
    ))


    row = cursor.fetchone()

    connection.close()


    if row is None:

        return None


    return {

        "user_query":
        row[0],

        "farmer_context":
        json.loads(
            row[1]
        ),

        "tool_results":
        json.loads(
            row[2]
        ),

        "farmer_id":
        row[3],

        "farm_id":
        row[4]

    }


# ==================================================
# SAVE MESSAGE
# ==================================================

def save_message(
    session_id,
    role,
    message
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        INSERT INTO messages
        (
            session_id,
            role,
            message
        )

        VALUES (?, ?, ?)
    """, (

        session_id,

        role,

        message

    ))


    connection.commit()

    connection.close()


# ==================================================
# GET MESSAGES
# ==================================================

def get_messages(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            role,
            message,
            created_at

        FROM messages

        WHERE session_id = ?

        ORDER BY id ASC
    """, (
        session_id,
    ))


    rows = cursor.fetchall()

    connection.close()


    return [

        {

            "role":
            row[0],

            "message":
            row[1],

            "created_at":
            row[2]

        }

        for row in rows

    ]


# ==================================================
# GET FARMER CONVERSATIONS
# ==================================================

def get_farmer_conversations(
    farmer_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT
            session_id,
            farm_id,
            user_query,
            farmer_context,
            tool_results

        FROM conversations

        WHERE farmer_id = ?

        ORDER BY rowid DESC
    """, (
        farmer_id,
    ))


    rows = cursor.fetchall()

    connection.close()


    return [

        {

            "session_id":
            row[0],

            "farm_id":
            row[1],

            "user_query":
            row[2],

            "farmer_context":
            json.loads(
                row[3]
            ),

            "tool_results":
            json.loads(
                row[4]
            )

        }

        for row in rows

    ]


# ==================================================
# DELETE MEMORY
# ==================================================

def delete_memory(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        DELETE FROM messages

        WHERE session_id = ?
    """, (
        session_id,
    ))


    cursor.execute("""
        DELETE FROM conversations

        WHERE session_id = ?
    """, (
        session_id,
    ))


    connection.commit()

    connection.close()


# ==================================================
# INITIALIZE DATABASE
# ==================================================

initialize_database()