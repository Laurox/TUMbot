import discord
from discord.ext.commands import Bot as DBot
from schedule import Scheduler


class Bot(DBot):
    def __init__(self, db, conf, **options):
        super().__init__(**options)
        self.db = db
        self.conf = conf
        self.schedule = Scheduler()

    async def close(self):
        print("Shutting down!")
        await super().close()
        self.db.close_all()

    def register_job_daily(self, daytime, f):
        print(f"Registering job {f.__name__} to run every day at {daytime}")
        self.schedule.every().day.at(daytime).do(f)

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
