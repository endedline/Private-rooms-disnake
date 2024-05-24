import disnake
from disnake.ext import commands
from disnake import TextInputStyle
import datetime
from disnake.interactions import MessageInteraction
import pymongo
from config import *
import json

cluster = pymongo.MongoClient(MONGO_URI)

db = cluster["Private_Room"]
coll = db["Rooms"]

class UserLockSelect(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return
        
        
        await self.channel_id.set_permissions(self.values[0], connect=False)
        try:
            await self.values[0].move_to(channel=self.channel_id)
        except:
            pass
        await interaction.response.defer()


class UserUnLockSelect(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return
        
        await self.channel_id.set_permissions(self.values[0], connect=None)
        try:
            await self.values[0].move_to(channel=self.channel_id)
        except:
            pass
        await interaction.response.defer()


class UserMute(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return
        
        await self.channel_id.set_permissions(self.values[0], speak=False)
        try:
            await self.values[0].move_to(channel=self.channel_id)
        except:
            pass
        await interaction.response.defer()


class UserUnMute(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return

        await self.channel_id.set_permissions(self.values[0], speak=None)
        try:
            await self.values[0].move_to(channel=self.channel_id)
        except:
            pass
        await interaction.response.defer()


class KickUser(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return
        
        if self.values[0].voice.channel == self.channel_id:
            try:
                await self.values[0].move_to(channel=None)
            except:
                pass
        await interaction.response.defer()


class PermUser(disnake.ui.UserSelect):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        super().__init__(placeholder='Выберите пользователя', min_values=0, max_values=1)

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
            return
        
        coll.update_one({"member": interaction.author.id}, {"$set": {"member": self.values[0].id}})
        await interaction.response.defer()


class MyModalName(disnake.ui.Modal):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.components = [
            disnake.ui.TextInput(
                label="Задайте название",
                placeholder="Няшимся",
                custom_id="channel_name",
                style=TextInputStyle.paragraph,
                max_length=1000
            )
        ]
        super().__init__(title="Задать имя канала", components=self.components, custom_id="Modal_channel_name")

    async def callback(self, inter: disnake.ModalInteraction):
        new_name = str(inter.text_values["channel_name"])
        if self.channel_id is not None:
            await self.channel_id.edit(name=new_name)
            await inter.response.send_message(f"Название канала успешно изменено на **{new_name}**", ephemeral=True)
        else:
            await inter.response.send_message("Канал не найден. Возможно, он не был создан", ephemeral=True)


class LimitModal(disnake.ui.Modal):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        self.components = [
            disnake.ui.TextInput(
                label="Задайте название",
                placeholder="0 - 99",
                custom_id="limit",
                style=TextInputStyle.paragraph,
                max_length=2
            )
        ]
        super().__init__(title="Задать лимит канала", components=self.components, custom_id="Modal_channel_name")

    async def callback(self, inter: disnake.ModalInteraction):
        new_limit = int(inter.text_values["limit"])
        if self.channel_id is not None:
            await self.channel_id.edit(user_limit=new_limit)
            await inter.response.send_message(f"Лимит канала успешно изменен на **{new_limit}**", ephemeral=True)
        else:
            await inter.response.send_message("Канал не найден. Возможно, он не был создан", ephemeral=True)


class btn(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.last_button_use = {}
        self.last_limit = {}
        
    async def interaction_check(self, interaction: MessageInteraction):
        user = coll.find_one({"member": interaction.author.id})
        
        view = disnake.ui.View()
        button = disnake.ui.Button(label="Перейти в комнату", style=disnake.ButtonStyle.url, url='https://discord.com/channels/819316098859532358/1211024007374180393')
        view.add_item(button)
        
        categoriya = interaction.guild.get_channel(1209557850385420340) #категория где будет создавать комната
        for chnls in categoriya.voice_channels:
            if interaction.author.voice and interaction.author.voice.channel == chnls:
                if not user:
                    embed = disnake.Embed(title="Приватные комнаты", color=0x36383f)
                    embed.description = f"Вы не являетесь владельцем комнаты!"
                    embed.set_thumbnail(url=interaction.author.display_avatar)
                    return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        if interaction.author.voice is None:
            embed = disnake.Embed(title="Приватные комнаты", color=0x36383f)
            embed.description = f"Вы не находитесь в войсе! Чтобы создать приватную команту перейдите в канал"
            embed.set_thumbnail(url=interaction.author.display_avatar)
            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        if not user:
            embed = disnake.Embed(title="Приватные комнаты", color=0x36383f)
            embed.description = f"Вы еще не создали приватную комнату! Чтобы создать приватную команту перейдите в канал"
            embed.set_thumbnail(url=interaction.author.display_avatar)
            return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        return True

    @disnake.ui.button(emoji="<:deleteuser2:1220869415122243804>", style=disnake.ButtonStyle.gray, custom_id="hide_unhide")
    async def hide_unhide(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])
        
        channel_permissions = channel_id.permissions_for(inter.guild.default_role)
        
        if channel_permissions.view_channel:
            await channel_id.set_permissions(inter.guild.default_role, view_channel=False)
        else:
            await channel_id.set_permissions(inter.guild.default_role, view_channel=True)

        await inter.response.defer()

    @disnake.ui.button(emoji="<:lock1:1220835622445514833>", style=disnake.ButtonStyle.gray, custom_id="lock")
    async def lock(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])

        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, у которого хотите забрать доступ в комнату",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)
        
        view = disnake.ui.View()
        view.add_item(UserLockSelect(channel_id))
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @disnake.ui.button(emoji="<:unlock:1221188570484572300>", style=disnake.ButtonStyle.gray, custom_id="unlock")
    async def unlock(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])

        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, которому хотите выдать доступ в комнату",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)
        
        view = disnake.ui.View()
        view.add_item(UserUnLockSelect(channel_id))
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @disnake.ui.button(emoji="<:pencil:1221188568634884166>", style=disnake.ButtonStyle.gray, custom_id="rename")
    async def rename(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})
        
        channel_id = inter.guild.get_channel(user["_id"])
        
        current_time = datetime.datetime.now()
        
        if inter.author.id in self.last_button_use:
            last_use_time = self.last_button_use[inter.author.id]
            time_difference = current_time - last_use_time
            if time_difference.total_seconds() < 60:
                оставшееся_время = datetime.timedelta(seconds=60 - time_difference.total_seconds())
                следующее_время = current_time + оставшееся_время
                nrxt = disnake.utils.format_dt(следующее_время, style='R')
                await inter.response.send_message(f"Следущее использование будет доступно {nrxt}", ephemeral=True)
                return

        self.last_button_use[inter.author.id] = current_time

        await inter.response.send_modal(MyModalName(channel_id))
        

    @disnake.ui.button(emoji="<:mute1:1220873145221775493>", style=disnake.ButtonStyle.gray, custom_id="mute")
    async def mute(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])
        
        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, которому хотите выдать мут",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)

        view = disnake.ui.View()
        view.add_item(UserMute(channel_id))
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @disnake.ui.button(emoji="<:mic5:1220873143820750848>", style=disnake.ButtonStyle.gray, custom_id="unmute")
    async def unmute(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])
        
        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, которому хотите снять мут",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)

        view = disnake.ui.View()
        view.add_item(UserUnMute(channel_id))
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @disnake.ui.button(emoji="<:delete:1221188552184823938>", style=disnake.ButtonStyle.gray, custom_id="locktoall")
    async def locktoall(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])

        channel_permissions = channel_id.permissions_for(inter.guild.default_role)
        if channel_permissions.connect:
            await channel_id.set_permissions(inter.guild.default_role, connect=False)
        else:
            await channel_id.set_permissions(inter.guild.default_role, connect=True)

        await inter.response.defer()

    @disnake.ui.button(emoji="<:deleteuser1:1220835628984303787>", style=disnake.ButtonStyle.gray, custom_id="kick")
    async def kick(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])
        
        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, которого хотите выгнать",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)
        
        view = disnake.ui.View()
        view.add_item(KickUser(channel_id))
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    @disnake.ui.button(emoji="<:group_3:1221188557117325555>", style=disnake.ButtonStyle.gray, custom_id="limit")
    async def limit(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})
        
        channel_id = inter.guild.get_channel(user["_id"])
        
        current_time = datetime.datetime.now()
        
        if inter.author.id in self.last_limit:
            last_use_time = self.last_limit[inter.author.id]
            time_difference = current_time - last_use_time
            if time_difference.total_seconds() < 60:
                оставшееся_время = datetime.timedelta(seconds=60 - time_difference.total_seconds())
                следующее_время = current_time + оставшееся_время
                nrxt = disnake.utils.format_dt(следующее_время, style='R')
                await inter.response.send_message(f"Следущее использование будет доступно {nrxt}", ephemeral=True)
                return

        self.last_limit[inter.author.id] = current_time

        await inter.response.send_modal(LimitModal(channel_id))

    @disnake.ui.button(emoji="<:vip:1221188572296646878>", style=disnake.ButtonStyle.gray, custom_id="crown")
    async def crown(self, button: disnake.Button, inter: disnake.CommandInteraction):
        user = coll.find_one({"member": inter.author.id})

        channel_id = inter.guild.get_channel(user["_id"])
        
        embed = disnake.Embed(
            title="Меню выбора",
            description="Выберите пользователя, которому хотите передать право владением кномнатой",
            color=0x36393f,
            timestamp=datetime.datetime.now()
        ).set_thumbnail(url=inter.author.display_avatar)

        view = disnake.ui.View()
        view.add_item(PermUser(channel_id))

        await inter.response.send_message(embed=embed, view=view, ephemeral=True)


class CreateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.new_channel = None
        self.views_added_private = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if after.channel and after.channel.id == 1211024007374180393: #канал для создание комнаты
            self.new_channel = await guild.create_voice_channel(member.display_name, category=after.channel.category)
            await self.new_channel.set_permissions(member, connect=True, view_channel=True)

            try:
                await member.move_to(self.new_channel)
                coll.insert_one({"_id": self.new_channel.id, "member": member.id})
            except:
                await self.new_channel.delete()

        try:
            def check(a, b, c):
                return len(self.new_channel.members) == 0

            await self.bot.wait_for("voice_state_update", check=check)
            await self.new_channel.delete()
            coll.delete_one({"_id": self.new_channel.id})
        except:
            pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def s(self, ctx):
        channel = self.bot.get_channel(1211023937388150784)
        embed = disnake.Embed(title=f"Настройка приватных комнат", #заменить емодзи
                              description=
                              "Жми следующие кнопки, чтобы настроить свою комнату\n"
                              "Использовать их можно только когда у тебя есть приватный канал\n\n"
                              "<:deleteuser_2:1221188555372757094> — `Скрыть комнату от всех`\n"
                              "<:lock_1:1221188561466822820> — `Забрать доступ в комнату`\n"
                              "<:unlock:1221188570484572300> — `Выдать доступ в комнату`\n"
                              "<:pencil:1221188568634884166> — `Изменить название канала`\n"
                              "<:mute_1:1221188565623509163> — `Выключить микрофон участнику`\n"
                              "<:asdasdxzc:1221188563140481057> — `Включить микрофон участнику`\n"
                              "<:delete:1221188552184823938> — `Закрыть комнату от всех`\n"
                              "<:zXZaS:1221188554059681912> — `Выгнать участника`\n"
                              "<:group_3:1221188557117325555> — `Установить лимит пользователей`\n"
                              "<:vip:1221188572296646878> — `Назначить пользователя владельцем комнаты\n`",
                              color=0x36393f)
        await channel.send(embed=embed, view=btn())
        

    @commands.Cog.listener()
    async def on_connect(self):
        if self.views_added_private:
            return
        self.bot.add_view(btn(), message_id=1221194762598617189) #id сообщение после первого конекта


def setup(bot):
    bot.add_cog(CreateCog(bot))
