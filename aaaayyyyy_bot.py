import logging
import discord

class AaaayyyyyBot(discord.Client):
    def __init__(self, logger:logging.Logger, **options):
        self.logger = logger
        if logger is not None:
            logger.info('Log started')
        discord.Client.__init__(self, **options)
        return
    
if __name__ == '__main__':
    import sys
    import dotenv
    import os
    #setup logging
    formatter = logging.Formatter('[{asctime}]<{name}>{levelname}: {message}', style='{')
    file_handler = logging.FileHandler('aaaayyyyy_bot.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger = logging.getLogger('aaaayyyyy_bot')
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)
    #load token
    dotenv.load_dotenv()
    token = os.getenv('BOT_TOKEN')
    bot = AaaayyyyyBot(logger)
    bot.run(token)
