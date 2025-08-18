#!/usr/bin/env python3
import sqlite3

DB_PATH = "/workspace/assets/sql.lite"


def main() -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    def count(table: str) -> int:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0]

    print("counts:")
    for t in ["content", "seasons", "episodes", "content_servers", "episode_servers"]:
        print(f"  {t}:", count(t))

    print("\nsample content:")
    cur.execute("SELECT id, title, type, year FROM content ORDER BY id LIMIT 5")
    for row in cur.fetchall():
        print("  ", row)

    print("\nDRM servers (content level) sample:")
    cur.execute(
        """
        SELECT c.title, cs.name, cs.drm, cs.license
        FROM content c
        JOIN content_servers cs ON c.id=cs.content_id
        WHERE cs.license IS NOT NULL OR cs.drm=1
        LIMIT 5
        """
    )
    for row in cur.fetchall():
        print("  ", row)

    print("\nEpisode-level server sample:")
    cur.execute(
        """
        SELECT c.title, s.season_number, e.episode_number, es.name
        FROM content c
        JOIN seasons s ON c.id=s.content_id
        JOIN episodes e ON s.id=e.season_id
        JOIN episode_servers es ON e.id=es.episode_id
        WHERE c.type='tv_series'
        LIMIT 5
        """
    )
    for row in cur.fetchall():
        print("  ", row)

    con.close()


if __name__ == "__main__":
    main()

