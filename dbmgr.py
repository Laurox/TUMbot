import os
import sqlite3


class DbMgr:
    def __init__(self, dbpath="db"):
        self.db_handles = {}
        self.dbpath = dbpath

    def get(self, guild):
        guild = str(guild)

        if guild not in self.db_handles:
            # Create a new connection
            self.db_handles[guild] = sqlite3.connect(f"{self.dbpath}/{guild}.db", check_same_thread=False)
            self.db_handles[guild].row_factory = sqlite3.Row

            # Update the database to the latest schema
            self.upgrade_db(self.db_handles[guild])

        return self.db_handles[guild]

    def upgrade_db(self, connection):
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]

        while os.path.isfile(f"db/schema_{user_version + 1}.sql"):
            with open(f"db/schema_{user_version + 1}.sql") as file:
                connection.executescript(file.read())
            user_version = connection.execute("PRAGMA user_version").fetchone()[0]

    def close(self, commit=True):
        while len(self.db_handles) > 0:
            conn = self.db_handles.pop(list(self.db_handles.keys())[0])

            if commit:
                conn.commit()

            conn.close()
