import time
from threading import Thread

import discord
from discord.ext.commands import Bot as DBot
from schedule import Scheduler


class Bot(DBot):
    def __init__(self, db, **options):
        super().__init__(**options)
        self.db = db
        self.jobs = []
        self.run_jobs = True
        self.schedule = Scheduler()

    async def close(self):
        print("Shutting down!")
        self.run_jobs = False
        await super().close()
        self.db.close_all()

    async def on_ready(self):
        print(f"Bot is ready! Logged in as {self.user}.")
        Thread(target=self.job_runner).start()

    def job_runner(self):
        print("Starting background timer runner.")
        while self.run_jobs:
            try:
                self.schedule.run_pending()
            except Exception as e:
                print(f"{type(e).__name__}: {e}")
            time.sleep(10)

    def register_job_daily(self, daytime, f):
        print(f"Registering job {f.__name__} to run every day at {daytime}")
        self.schedule.every().day.at(daytime).do(f)

    def register_job(self, timer, f):
        print(f"Registering job {f.__name__} to run every {timer} seconds")
        self.schedule.every(timer).seconds.do(f)

    def dbconf_get(self, guild_id, name, default=None):
        result = self.db.get(guild_id).execute("SELECT value FROM config WHERE name = ?", (name,)).fetchall()

        if len(result) < 1:
            return default

        return str(result[0][0])

    def dbconf_set(self, guild_id, name, value):
        saved = self.dbconf_get(guild_id, name)

        if saved is None:
            with self.db.get(guild_id) as db:
                db.execute("INSERT INTO config(name, value) VALUES(?, ?)", (name, value))
            return

        if str(saved) == str(value):
            return

        with self.db.get(guild_id) as db:
            db.execute("UPDATE config SET value = ? WHERE name = ?", (value, name))

    async def send_table(self, messageable: discord.abc.Messageable, keys, table, maxlen=2000):
        key_length = {}

        for row in table:
            for key in keys:
                if not key in key_length:
                    key_length[key] = len(str(key))

                key_length[key] = max(key_length[key], len(str(row[key])))

        header = "|"
        headerline = "|"

        for i in keys:
            header += f" {str(i).ljust(key_length[i])} |"
            headerline += '-' * (key_length[i] + 2) + '|'

        text = header + "\n" + headerline

        for row in table:
            newtext = "\n|"
            for key in keys:
                newtext += f" {str(row[key]).ljust(key_length[key])} |"

            # -6: Account for code block
            if len(text) + len(newtext) >= maxlen - 6:
                await messageable.send(f"```{text}```")
                text = ""

            text += newtext

        await messageable.send(f"```{text}```")
