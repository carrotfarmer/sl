from flask import Flask, g, request
from flask_cors import CORS
import psycopg

from dotenv import load_dotenv
import os

load_dotenv()
PG_URI = os.getenv("PG_URI") 

app = Flask(__name__)
CORS(app)

if (PG_URI is None):
    raise ValueError("PG_URI is not set in the environment variables")

# add database to the app context
def get_db():
    if "db" not in g:
        g.db = psycopg.connect(str(PG_URI))
    return g.db

# remove database from the app context
@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# create database table
with psycopg.connect(PG_URI) as conn:
    with conn.cursor() as cur:
        # sql query to create a table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );
        """
        cur.execute(create_table_query)
        conn.commit()

# create a new item
@app.route('/items', methods=["POST"])
def create_item():
    db = get_db()
    name = request.args.get("name") 
    if not name:
        return {"error": "Name is required"}, 400

    try:
        with db.cursor() as cur:
            # SQL query to insert a new item
            insert_query = """
            INSERT INTO items (name) VALUES (%s) RETURNING id, name;
            """
            cur.execute(insert_query, (name,))
            result = cur.fetchone()  # Fetch the result

            # Check if the result is None
            if result is None:
                return {"error": "Failed to insert item"}, 500

            id, name = result
            db.commit()
            return {"id": id, "name": name}, 201
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500

# delete an item
@app.route('/items/<int:id>', methods=["DELETE"])
def delete_item(id):
    db = get_db()
    try:
        with db.cursor() as cur:
            # SQL query to delete an item
            delete_query = """
            DELETE FROM items WHERE id = %s RETURNING id, name;
            """
            cur.execute(delete_query, (id,))
            result = cur.fetchone()  # Fetch the result

            # Check if the result is None
            if result is None:
                return {"error": "Item not found"}, 404

            id, name = result
            db.commit()
            return {"id": id, "name": name}, 200
    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500

# get all items
@app.route('/items', methods=["GET"])
def get_items():
    db = get_db()
    try:
        with db.cursor() as cur:
            # SQL query to get all items
            select_query = """
            SELECT id, name FROM items;
            """
            cur.execute(select_query)
            items = cur.fetchall()  # Fetch all the results

            # Check if the result is None
            if items is None:
                return {"error": "No items found"}, 404

            items = [{"id": id, "name": name} for id, name in items]
            return {"items": items}, 200
    except Exception as e:
        return {"error": str(e)}, 500
