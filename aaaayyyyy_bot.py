import logging
import discord

class AaaayyyyyBot(discord.Client):
    def __init__(self, target_list_path:str='./targets.csv',
                 ping_timeout:float=None, command_timeout:float=None, **options):
        self.logger = logging.getLogger('aaaayyyyy_bot')
        self.ping_timeout = ping_timeout
        self.logger.info(f'Ping timeout set to: {ping_timeout}')
        self.command_timeout = command_timeout
        self.logger.info(f'Command timeout set to: {command_timeout}')
        self.target_list_path = target_list_path
        self.logger.info(f'Target list path set to: "{target_list_path}"')
        self.targets = self.load_target_list(target_list_path)
        #setup intents
        if 'intents' not in options:
            options['intents'] = discord.Intents.default()
        options['intents'].messages = True
        options['intents'].members = True
        options['intents'].guilds = True
        discord.Client.__init__(self, **options)
        return
    def load_target_list(self, path:str)->dict:
        '''Load a target list from the given file path'''
        self.logger.info(f'Loading target list from "{path}"...')
        target_list = dict()
        try:
            with open(path, mode='rt') as file:
                while True:
                    line = file.readline()
                    if line == '':
                        break
                    key = line.partition(';')[0].split(',')
                    key[1] = int(key[1])
                    try:
                        key[0] = int(key[0])
                    except ValueError:
                        pass
                    key = tuple(key)
                    user_ids = set(map(lambda user_id: int(user_id), line.partition(';')[2].split(',')))
                    target_list[key] = user_ids
                    self.logger.debug(f'Loaded {len(user_ids)} target(s) to list {key!r} from "{path}": {user_ids}')
            self.logger.info(f'Loaded {len(target_list)} target list(s) from "{path}"')
        except FileNotFoundError:
            self.logger.warning(f'No file at "{path}" to load target list from')
        return target_list
    def save_target_list(self, path:str, target_list:dict):
        '''Save the given target list to the given file path'''
        self.logger.info(f'Saving target list to "{path}"...')
        with open(path, mode='wt') as file:
            for key in target_list:
                file.write(f'{key[0]},{key[1]};' + ','.join(map(lambda target: f'{target}', target_list[key])) + '\n')
                self.logger.debug(f'Saved {len(target_list[key])} target(s) for list {key} to "{path}": {target_list[key]}')
        self.logger.info(f'Saved {len(target_list)} target list(s) to "{path}"')
        return
    def get_target_list_key(self, arg)->tuple:
        '''Calculate the target list key to use for the given channel,
or set of existing keys if given a guild or member'''
        if isinstance(arg, discord.TextChannel):
            return (arg.guild.id, arg.id)
        if isinstance(arg, discord.GroupChannel):
            return ('group', arg.id)
        if isinstance(arg, discord.DMChannel):
            return ('dm', arg.id)
        if isinstance(arg, discord.Guild):
            return set(filter(lambda key: key[0] == arg.id, self.targets))
        if isinstance(arg, discord.Member):
            return set(filter(lambda key: key[0] == arg.guild.id and arg.mention in self.targets[key], self.targets))
        return None
    async def ping(self, message):
        '''Trigger a ping with the given message'''
        #calc target list key
        key = self.get_target_list_key(message.channel)
        self.logger.debug(f'Fetching target list for {key}')
        #calc target list
        targets = set()
        if key in self.targets:
            targets = self.targets[key] & set(map(lambda member: member.id, message.channel.members))
        #ping targets
        try:
            await message.channel.send('Aaaayyyyy! ' + ' '.join(map(lambda user_id: self.get_user(user_id).mention, targets)),
                                       delete_after=self.ping_timeout, reference=message, mention_author=False)
        except discord.Forbidden:
            self.logger.warning(f'Insufficient permissions to ping in channel "{message.channel}" in guild "{message.guild}"')
            return
        except discord.HTTPException:
            self.logger.warning(f'Failed to ping in channel "{message.channel}" in guild "{message.guild}"')
            return
        self.logger.info('Pinged "' + '", "'.join(map(lambda user: f'{user.name}#{user.discriminator}',
                                                       map(lambda user_id: self.get_user(user_id), targets)))
                    + f'" in channel "{message.channel}" in guild "{message.guild}"')
        return
    async def command(self, message):
        '''Add or remove targets mentioned in the given message'''
        #get key
        key = self.get_target_list_key(message.channel)
        self.logger.debug(f'Modifying target list for {key}')
        if key not in self.targets:
            self.targets[key] = set()
            self.logger.debug(f'Added new target list for {key}')
        #classify targets
        to_remove = set()
        to_add = set()
        for user in message.mentions:
            if user == self.user:
                continue
            if user.id in self.targets[key]:
                to_remove.add(user)
            else:
                to_add.add(user)
        #add/remove targets
        self.targets[key] -= set(map(lambda user: user.id, to_remove))
        self.targets[key] |= set(map(lambda user: user.id, to_add))
        if len(self.targets[key]) < 1:
            del self.targets[key]
            self.logger.debug(f'Removed empty target list from {key}')
        #log actions
        if len(to_remove) > 0:
            self.logger.info(f'Removed "' + '", "'.join(map(lambda user: f'{user.name}#{user.discriminator}', to_remove))
                             + f'" from target list for channel "{message.channel}" in guild "{message.guild}"')
        if len(to_add) > 0:
            self.logger.info(f'Added "' + '", "'.join(map(lambda user: f'{user.name}#{user.discriminator}', to_add))
                             + f'" to target list for channel "{message.channel}" in guild "{message.guild}"')
        self.save_target_list(self.target_list_path, self.targets)
        #reply to command
        reply = list()
        if len(to_remove) > 0:
            reply.append('Removed `' + '`, `'.join(map(lambda user: f'{user.name}#{user.discriminator}', to_remove))
                         + '` from target list')
        if len(to_add) > 0:
            reply.append('Added `' + '`, `'.join(map(lambda user: f'{user.name}#{user.discriminator}', to_add))
                         + '` to target list')
        try:
            await message.channel.send('\n'.join(reply), delete_after=self.command_timeout,
                                       reference=message, mention_author=False)
        except discord.Forbidden:
            self.logger.warning(f'Insufficient permissions to respond to command in channel "{message.channel}" in guild "{message.guild}"')
        except discord.HTTPException:
            self.logger.warning(f'Failed to respond to command in channel "{message.channel}" in guild "{message.guild}"')
        return
    async def on_message(self, message):
        if message.author == self.user:
            return
        if self.user in message.mentions:
            await self.command(message)
        elif 'a' in message.content or 'A' in message.content:
            await self.ping(message)
        return
    async def on_guild_channel_delete(self, channel):
        key = self.get_target_list_key(channel)
        if key in self.targets:
            del self.targets[key]
            self.logger.info(f'Cleared targets for channel "{channel.name}" in guild "{channel.guild.name}"')
        return
    async def on_guild_remove(self, guild):
        keys = self.get_target_list_key(guild)
        if len(keys) > 0:
            for key in keys:
                del self.targets[key]
            self.logger.info('Cleared targets for channels "'
                             + '", "'.join(map(lambda key: guild.get_channel(key[1]).name, keys))
                             + f'" in guild "{guild.name}"')
        return
    async def on_private_channel_delete(self, channel):
        key = self.get_target_list_key(channel)
        if key in self.targets:
            del self.targets[key]
            self.logger.info(f'Cleared targets for channel "{channel.name}"')
        return
    async def on_member_remove(self, member):
        keys = self.get_target_list_key(member)
        if len(keys) > 0:
            for key in keys:
                self.targets[key].remove(member.mention)
            self.logger.info(f'Removed target "{member.name}#{member.discriminator}" from channels "'
                             + '", "'.join(map(lambda key: member.guild.get_channel(key[1]).name, keys))
                             + f'" in guild "{member.guild.name}"')
        return
    async def on_group_remove(self, channel, user):
        key = self.get_target_list_key(channel)
        if key in self.targets and user.mention in self.targets[key]:
            self.targets[key].remove(user.mention)
            self.logger.info(f'Removed target "{user.name}#{user.discriminator}" from group channel "{channel.name}"')
        return
            
if __name__ == '__main__':
    import sys
    import dotenv
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
    try:
        try:
            token = dotenv.dotenv_values('./.env')['BOT_TOKEN']
        except KeyError:
            logger.critical('No bot token found')
            sys.exit('No bot token found')
        bot = AaaayyyyyBot()
        bot.run(token)
    except Exception as x:
        logger.exception(x)
        sys.exit(x)
