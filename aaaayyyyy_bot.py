import logging
import discord

class AaaayyyyyBot(discord.Client):
    def __init__(self, logger:logging.Logger=None, ping_timeout:float=None, command_timeout:float=None, **options):
        self.ping_timeout = ping_timeout
        self.command_timeout = command_timeout
        self.targets = dict()
        self.logger = logger
        if logger is not None:
            logger.info('Log started')
        discord.Client.__init__(self, **options)
        return
    def calc_target_list_key(self, message)->tuple:
        '''Calculate the target list key to use for the given message'''
        if isinstance(message.channel, discord.TextChannel):
            return (message.guild.id, message.channel.id)
        if isinstance(message.channel, discord.GroupChannel):
            return ('group', message.channel.id)
        if isinstance(message.channel, discord.DMChannel):
            return ('dm', message.channel.id)
        return None
    async def ping(self, message):
        '''Trigger a ping with the given message'''
        #calc target list key
        key = self.calc_target_list_key(message)
        if self.logger is not None:
            self.logger.debug(f'Fetching target list for {key}')
        #calc target list
        targets = set()
        if key in self.targets:
            print(self.targets[key])
            print(set(map(lambda mem: mem.mention, message.channel.members)))
            targets = self.targets[key] & set(map(lambda mem: mem.mention, message.channel.members))
        #log action
        if logger is not None:
            logger.info('Pinging "'+ '", "'.join(targets) + f'" in channel "{message.channel}" in guild "{message.guild}"')
        #ping targets
        await message.channel.send(f'Aaaayyyyy! {" ".join(targets)}', delete_after=self.ping_timeout, reference=message, mention_author=False)
        return
    async def command(self, message):
        '''Add or remove targets mentioned in the given message'''
        #get key
        key = self.calc_target_list_key(message)
        if self.logger is not None:
            self.logger.debug(f'Modifying target list for {key}')
        if key not in self.targets:
            self.targets[key] = set()
            if self.logger is not None:
                self.logger.debug(f'Added new target list for {key}')
        #classify targets
        to_remove = set()
        to_add = set()
        for user in message.mentions:
            if user == self.user:
                continue
            if user.mention in self.targets[key]:
                to_remove.add(user)
            else:
                to_add.add(user)
        #add/remove targets
        self.targets[key] -= set(map(lambda user: user.mention, to_remove))
        self.targets[key] |= set(map(lambda user: user.mention, to_add))
        if len(self.targets[key]) < 1:
            del self.targets[key]
            if self.logger is not None:
                self.logger.debug(f'Removed empty target list from {key}')
        #log actions
        if self.logger is not None:
            if len(to_remove) > 0:
                self.logger.info(f'Removed "' + '", "'.join(map(lambda user: user.name, to_remove)) + f'" from target list for channel "{message.channel}" in guild "{message.guild}"')
            if len(to_add) > 0:
                self.logger.info(f'Added "' + '", "'.join(map(lambda user: user.name, to_add)) + f'" to target list for channel "{message.channel}" in guild "{message.guild}"')
        #reply to command
        reply = list()
        if len(to_remove) > 0:
            reply.append(f'Removed `{"`, `".join(map(lambda user: user.name, to_remove))}` from target list')
        if len(to_add) > 0:
            reply.append(f'Added `{"`, `".join(map(lambda user: user.name, to_add))}` to target list')
        await message.channel.send('\n'.join(reply), delete_after=self.command_timeout, reference=message, mention_author=False)
        return
    async def on_message(self, message):
        if message.author != self.user:
            if self.user in message.mentions:
                await self.command(message)
            elif 'a' in message.content or 'A' in message.content:
                await self.ping(message)
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
