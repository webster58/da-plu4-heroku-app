import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/tracks")
async def root():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    cursor = app.db_connection.cursor()
    tracks = cursor.execute("SELECT name FROM tracks").fetchall()
    return {
        "tracks": tracks,
    }


@app.get("/tracks/{track_id}")
async def single_track(track_id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT name, composer FROM tracks WHERE trackid = ?", (track_id, )).fetchone()

    return data


@app.get("/tracks_with_artist")
async def tracks_with_artist():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
     SELECT tracks.name AS track_name, artists.name AS album_artist FROM tracks
     JOIN albums ON tracks.albumid = albums.albumid
     JOIN artists ON albums.artistid = artists.artistid;
     ''').fetchall()
    return data


@app.get("/tracks_with_artists_order")
async def tracks_with_artists_order():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
     SELECT tracks.name AS track_name, artists.name AS album_artist FROM tracks
     JOIN albums ON tracks.albumid = albums.albumid
     JOIN artists ON albums.artistid = artists.artistid
     ORDER BY artists.name;
     ''').fetchall()
    return data


@app.get("/artists")
async def artists():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    artists = app.db_connection.execute("SELECT name FROM artists").fetchall()
    return artists


class Artist(BaseModel):
    name: str


@app.post("/artists/add")
async def artists_add(artist: Artist):
    cursor = app.db_connection.execute(
        "INSERT INTO artists (name) VALUES (?)", (artist.name, )
    )
    app.db_connection.commit()
    new_artist_id = cursor.lastrowid
    app.db_connection.row_factory = sqlite3.Row
    artist = app.db_connection.execute(
        """SELECT artistid AS artist_id, name AS artist_name
         FROM artists WHERE artistid = ?""",
        (new_artist_id, )).fetchone()

    return artist


@app.put("/artists/edit/{artist_id}")
async def artists_add(artist_id: int, artist: Artist):
    cursor = app.db_connection.execute(
        "UPDATE artists SET name = ? WHERE artistid = ?", (artist.name, artist_id)
    )
    app.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    artist = app.db_connection.execute(
        """SELECT artistid AS artist_id, name AS artist_name
         FROM artists WHERE artistid = ?""",
        (artist_id, )).fetchone()

    return artist


@app.delete("/artists/delete/{artist_id}")
async def artist_delete(artist_id: int):
    cursor = app.db_connection.execute(
        "DELETE FROM artists WHERE artistid = ?", (artist_id, )
    )
    app.db_connection.commit()
    return {"deleted": cursor.rowcount}


@app.get("/artists_count")
async def artists_count():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    artists = app.db_connection.execute("SELECT name FROM artists ORDER BY name DESC").fetchall()
    count = app.db_connection.execute('SELECT COUNT(*) FROM artists').fetchone()

    return {
        "artists": artists,
        "artists_counter": count
    }
