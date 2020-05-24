from discord import Client, Embed
from random import choice
from database_control import *
from os.path import exists
from re import search

# DO NOT TOUCH FUCKING TOKEN AND IDS!!!
# ----------------------------------------------------------------------------------------------------------------------
TOKEN = '<Discord_token>'
GUILD_ID = <GUILD_ID>
ACTIVE_ROLE_ID = <ACTIVE_ROLE_ID>
# ----------------------------------------------------------------------------------------------------------------------
#
# Setting
#
ADMINISTRATORS = [<Admin_list>
                  ]
#
# (All values must be in a small case!!!)
#
# General
PREFIX = '!'
BOT_NAME = 'lupa'
# Commands
COMMAND_COIN = 'coin'
COMMAND_TOP = 'top'  # only_for_admins
COMMAND_USER_INFO = 'act'  # some_functions_only_for_admins
COMMAND_ADD_COINS = 'add'  # only_for_admins
COMMAND_HELP = 'help'
# Other
EMBED_COLOR = 1428807
DEFAULT_TOP_LEN = 10
MAX_TOP_LEN = 30
ROLE_PRICE = 100
# ----------------------------------------------------------------------------------------------------------------------


class Lupa(Client):
    # Events------------------------------------------------------------------------------------------------------------
    async def on_ready(self):
        if not exists('user_data.db'):
            create_database()
            add_user_to_database([user for user in self.get_guild(GUILD_ID).members if not user.bot])
        else:
            check_database(self.get_guild(GUILD_ID).members)
        print('Logged on as', self.user)

    @staticmethod
    async def on_member_join(member):
        user = get_user_from_database(member.id)
        if user is None:
            add_user_to_database(member)
        elif member.display_name != user.name:
            change_name(user.id, member.display_name)

    @staticmethod
    async def on_member_update(before, after):
        if before.display_name != after.display_name:
            change_name(before.id, after.display_name)

    async def on_message(self, message):
        if message.author == self.user:
            return
        text = message.content.lower()
        if text.startswith(PREFIX + BOT_NAME):
            if COMMAND_COIN in text:
                await message.channel.send(embed=self.coin)
            elif COMMAND_TOP in text:
                if message.author.id in ADMINISTRATORS:
                    await message.channel.send(self.top(text))
            elif COMMAND_USER_INFO in text:
                await message.channel.send(embed=self.user_info(message))
            elif COMMAND_ADD_COINS in text:
                if message.author.id in ADMINISTRATORS:
                    embed = await self.add_coins(message.content)
                    await message.channel.send(embed=embed)
            elif COMMAND_HELP in text:
                await message.channel.send(embed=self.commands)

    # Generation_of_responses-------------------------------------------------------------------------------------------
    @property
    def coin(self):
        return Embed(title='**Результат:**', description=choice(('||**решка**||', '||**орел**||')), color=EMBED_COLOR)

    @staticmethod
    def top(message):
        def insert_len(text: str):
            number = search(r'\d+', text)
            if number is not None:
                number = int(number.group())
                return number if number <= MAX_TOP_LEN else MAX_TOP_LEN
            return DEFAULT_TOP_LEN
        top_len = insert_len(message)
        users = get_top_users(top_len)
        top = f'**Информация об активности:**\n**Топ {top_len} активов:**\n```'
        for num, user in zip(range(1, top_len + 1), users):
            top += f'\n{num:•>2}) {user.name:·<20}{user.coins:·>6}'
        return top + '```'

    @staticmethod
    def user_info(message):
        if message.author.id in ADMINISTRATORS:
            user_id = search(r'@[!]?\d+', message.content)
            if user_id is not None:
                user_id = int(user_id.group().replace('@', '').replace('!', ''))
                if user_id != message.author.id:
                    user = get_user_from_database(user_id)
                    if user is not None:
                        return Embed(title='**`Информация об активности:`**',
                                     description=f'||Очков активности у @{user.name}: {user.coins}||',
                                     color=EMBED_COLOR)
        user = get_user_from_database(message.author.id)
        return Embed(title='**`Информация об активности:`**',
                     description=f'||Очков активности у вас (@{user.name}): {user.coins}||',
                     color=EMBED_COLOR)

    async def add_coins(self, text):
        user_id = search(r'@[!]?\d+', text)
        if user_id is not None:
            user_id = int(user_id.group().replace('@', '').replace('!', ''))
            user = get_user_from_database(user_id)
            if user is not None:
                value = search(r'[-]?\d+', text.replace(str(user_id), ''))
                if value is not None:
                    value = int(value.group())
                    if user.coins + value < ROLE_PRICE:
                        change_coins(user.id, value)
                        user = get_user_from_database(user.id)
                        return Embed(title='**`Очки активности успешно изменены!`**',
                                     description=f'||Очков активности у @{user.name}: {user.coins}||',
                                     color=EMBED_COLOR)
                    else:
                        change_coins(user.id, -user.coins)
                        guid = self.get_guild(GUILD_ID)
                        await guid.get_member(user.id).add_roles(guid.get_role(ACTIVE_ROLE_ID))
                        return Embed(title='**`Новый активист!!!`**',
                                     description=f'@{user.name} собрал {ROLE_PRICE} или более очков активности,' +
                                                 f' роль назначена!!!',
                                     color=EMBED_COLOR)
                return Embed(title='**`Ошибка!`**',
                             description=f'Колличество очков указано некорректно!',
                             color=EMBED_COLOR)
        return Embed(title='**`Ошибка!`**',
                     description=f'Пользователь указан некорректно!',
                     color=EMBED_COLOR)

    @property
    def commands(self):
        embed = Embed(title='**`Информация о боте:`**',
                      description='Привет, меня зовут Лупа!\n~~Но друзья зовут меня получать зарплату.~~\nЯ товарищ' +
                                  ' всем известного бота Пупа!',
                      color=EMBED_COLOR)
        embed.set_author(name='Lupa Bot', url='https://vk.com/duuuda')
        embed.set_thumbnail(url=self.user.avatar_url)
        embed.add_field(name='__**`Команда №1`**__',
                        value=f'**{PREFIX}{BOT_NAME.title()} {COMMAND_COIN}** - Команда для принятия важнейших, в' +
                              f' вашей жизни, решений',
                        inline=False)
        embed.add_field(name='__**`Команда №2`**__ (this command is only available to administrators)',
                        value=f'**{PREFIX}{BOT_NAME.title()} {COMMAND_TOP} <num>** - Получить топ активистов\n(<num>' +
                              f' - длинна списка, не обязательный параметр, по умолчанию: {DEFAULT_TOP_LEN};' +
                              f' максимум: {MAX_TOP_LEN})',
                        inline=False)
        embed.add_field(name='__**`Команда №3`**__' +
                             ' (some functions in this command are only available to administrators)',
                        value=f'**{PREFIX}{BOT_NAME.title()} {COMMAND_USER_INFO} @<user_name>** - Узнать колличество'
                              f' очков активности\n(<user_name> - Имя пользователя чьё колличество очков требуется'
                              f' узнать (Запрос чужой активности доступен лишь администраторам!!!))',
                        inline=False)
        embed.add_field(name='__**`Команда №4`**__',
                        value=f'**{PREFIX}{BOT_NAME.title()} {COMMAND_HELP}** - Вызывает данное информационное'
                              f' сообщение',
                        inline=False)
        embed.set_footer(text='P.S. В случае возникновения вопросов касаемо работы бота пожалуйста обращайтесь к' +
                              ' создателю (для этого перейдите по ссылке кликнув по надписи "Lupa Bot" в начале' +
                              ' данного сообщения)\n' +
                              'P.P.S. Вы можете использовать любой регистр в командах и даже писать слитно, но не'
                              ' забывайте о префиксе!')
        return embed


if __name__ == '__main__':
    bot = Lupa()
    bot.run(TOKEN)
