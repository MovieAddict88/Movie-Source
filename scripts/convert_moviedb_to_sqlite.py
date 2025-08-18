#!/usr/bin/env python3
import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


ASSETS_DIR = "/workspace/assets"
JSON_PATH = "/workspace/moviedb.json"
DB_PATH = os.path.join(ASSETS_DIR, "sql.lite")


def ensure_assets_directory(directory_path: str) -> None:
    os.makedirs(directory_path, exist_ok=True)


def connect_database(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS main_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS sub_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(main_category_id, name),
            FOREIGN KEY (main_category_id) REFERENCES main_categories(id) ON DELETE CASCADE
        );

        -- Content represents Live TV channels, Movies, and TV Series entries
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_category_id INTEGER NOT NULL,
            sub_category_id INTEGER,
            type TEXT NOT NULL CHECK(type IN ('live_tv','movie','tv_series')),
            title TEXT NOT NULL,
            country TEXT,
            description TEXT,
            poster TEXT,
            thumbnail TEXT,
            rating REAL,
            duration TEXT,
            year INTEGER,
            FOREIGN KEY (main_category_id) REFERENCES main_categories(id) ON DELETE RESTRICT,
            FOREIGN KEY (sub_category_id) REFERENCES sub_categories(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            season_number INTEGER NOT NULL,
            season_poster TEXT,
            UNIQUE(content_id, season_number),
            FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL,
            episode_number INTEGER NOT NULL,
            title TEXT,
            duration TEXT,
            description TEXT,
            thumbnail TEXT,
            UNIQUE(season_id, episode_number),
            FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS content_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            drm INTEGER NOT NULL DEFAULT 0,
            license TEXT,
            FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS episode_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            episode_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            drm INTEGER NOT NULL DEFAULT 0,
            license TEXT,
            FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_content_type ON content(type);
        CREATE INDEX IF NOT EXISTS idx_content_title ON content(title);
        CREATE INDEX IF NOT EXISTS idx_content_servers_content ON content_servers(content_id);
        CREATE INDEX IF NOT EXISTS idx_episode_servers_episode ON episode_servers(episode_id);
        CREATE INDEX IF NOT EXISTS idx_seasons_content ON seasons(content_id);
        CREATE INDEX IF NOT EXISTS idx_episodes_season ON episodes(season_id);
        """
    )

    connection.commit()


def get_or_create_main_category(cursor: sqlite3.Cursor, name: str) -> int:
    cursor.execute("SELECT id FROM main_categories WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute("INSERT INTO main_categories (name) VALUES (?)", (name,))
    return cursor.lastrowid


def get_or_create_sub_category(cursor: sqlite3.Cursor, main_category_id: int, name: Optional[str]) -> Optional[int]:
    if not name:
        return None
    cursor.execute(
        "SELECT id FROM sub_categories WHERE main_category_id = ? AND name = ?",
        (main_category_id, name),
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT OR IGNORE INTO sub_categories (main_category_id, name) VALUES (?, ?)",
        (main_category_id, name),
    )
    if cursor.lastrowid:
        return cursor.lastrowid
    cursor.execute(
        "SELECT id FROM sub_categories WHERE main_category_id = ? AND name = ?",
        (main_category_id, name),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def map_main_category_to_type(main_category_name: str) -> str:
    lower = main_category_name.strip().lower()
    if lower == "live tv":
        return "live_tv"
    if lower == "movies":
        return "movie"
    if lower == "tv series":
        return "tv_series"
    # Fallback to a generic bucket
    return "movie"


def insert_content(
    cursor: sqlite3.Cursor,
    main_category_id: int,
    sub_category_id: Optional[int],
    type_value: str,
    entry: Dict[str, Any],
) -> int:
    cursor.execute(
        """
        INSERT INTO content (
            main_category_id, sub_category_id, type, title, country, description,
            poster, thumbnail, rating, duration, year
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            main_category_id,
            sub_category_id,
            type_value,
            entry.get("Title"),
            entry.get("Country"),
            entry.get("Description"),
            entry.get("Poster"),
            entry.get("Thumbnail"),
            float(entry.get("Rating", 0.0)) if entry.get("Rating") is not None else None,
            entry.get("Duration"),
            int(entry.get("Year", 0)) if entry.get("Year") is not None else None,
        ),
    )
    return cursor.lastrowid


def insert_servers_for_content(cursor: sqlite3.Cursor, content_id: int, servers: List[Dict[str, Any]]) -> None:
    for server in servers or []:
        name = server.get("name") or "Unknown"
        url = server.get("url") or ""
        drm_value = 1 if server.get("drm") else 0
        license_value = server.get("license")
        if not url:
            continue
        cursor.execute(
            """
            INSERT INTO content_servers (content_id, name, url, drm, license)
            VALUES (?, ?, ?, ?, ?)
            """,
            (content_id, name, url, drm_value, license_value),
        )


def insert_season(cursor: sqlite3.Cursor, content_id: int, season: Dict[str, Any]) -> int:
    cursor.execute(
        """
        INSERT OR IGNORE INTO seasons (content_id, season_number, season_poster)
        VALUES (?, ?, ?)
        """,
        (
            content_id,
            int(season.get("Season", 0)),
            season.get("SeasonPoster"),
        ),
    )
    # Retrieve season id (either newly inserted or existing)
    cursor.execute(
        "SELECT id FROM seasons WHERE content_id = ? AND season_number = ?",
        (content_id, int(season.get("Season", 0))),
    )
    row = cursor.fetchone()
    return row[0]


def insert_episode(cursor: sqlite3.Cursor, season_id: int, episode: Dict[str, Any]) -> int:
    cursor.execute(
        """
        INSERT OR IGNORE INTO episodes (season_id, episode_number, title, duration, description, thumbnail)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            season_id,
            int(episode.get("Episode", 0)),
            episode.get("Title"),
            episode.get("Duration"),
            episode.get("Description"),
            episode.get("Thumbnail"),
        ),
    )
    cursor.execute(
        "SELECT id FROM episodes WHERE season_id = ? AND episode_number = ?",
        (season_id, int(episode.get("Episode", 0))),
    )
    row = cursor.fetchone()
    return row[0]


def insert_servers_for_episode(cursor: sqlite3.Cursor, episode_id: int, servers: List[Dict[str, Any]]) -> None:
    for server in servers or []:
        name = server.get("name") or "Unknown"
        url = server.get("url") or ""
        drm_value = 1 if server.get("drm") else 0
        license_value = server.get("license")
        if not url:
            continue
        cursor.execute(
            """
            INSERT INTO episode_servers (episode_id, name, url, drm, license)
            VALUES (?, ?, ?, ?, ?)
            """,
            (episode_id, name, url, drm_value, license_value),
        )


def load_json(json_path: str) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process(json_data: Dict[str, Any], connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    categories: List[Dict[str, Any]] = json_data.get("Categories", [])

    for category in categories:
        main_category_name = category.get("MainCategory", "").strip()
        if not main_category_name:
            # Skip malformed category blocks
            continue

        main_category_id = get_or_create_main_category(cursor, main_category_name)
        # Pre-register declared subcategories
        for subcat_name in category.get("SubCategories", []) or []:
            get_or_create_sub_category(cursor, main_category_id, subcat_name)

        type_value = map_main_category_to_type(main_category_name)

        for entry in category.get("Entries", []) or []:
            sub_category_name = entry.get("SubCategory")
            sub_category_id = get_or_create_sub_category(cursor, main_category_id, sub_category_name)

            content_id = insert_content(
                cursor,
                main_category_id=main_category_id,
                sub_category_id=sub_category_id,
                type_value=type_value,
                entry=entry,
            )

            # Live TV and Movies have servers attached to entry level
            entry_servers = entry.get("Servers")
            if entry_servers:
                insert_servers_for_content(cursor, content_id, entry_servers)

            # TV Series: process seasons and episodes
            if type_value == "tv_series":
                for season in entry.get("Seasons", []) or []:
                    season_id = insert_season(cursor, content_id, season)
                    for episode in season.get("Episodes", []) or []:
                        episode_id = insert_episode(cursor, season_id, episode)
                        insert_servers_for_episode(cursor, episode_id, episode.get("Servers") or [])

    connection.commit()


def main() -> None:
    ensure_assets_directory(ASSETS_DIR)
    # Remove existing DB to avoid duplicate data on re-run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    connection = connect_database(DB_PATH)
    try:
        create_schema(connection)
        data = load_json(JSON_PATH)
        process(data, connection)
        # Vacuum to compact DB and ensure smaller footprint for assets
        connection.execute("VACUUM;")
        connection.commit()
        print(f"SQLite database created at: {DB_PATH}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()

