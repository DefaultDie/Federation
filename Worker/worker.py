import os
import time
import datetime
import csv
import numpy
import nextcord
from nextcord.ext import application_checks, tasks

TOKEN = ''  # Your bot token here.


def check_msg_content(m):
    return m.content in ('y', 'n') and not m.author.bot


def predicate(m):
    return not m.author.bot


def copy_master_list():

    members_list = []
    with open(f'{os.getcwd()}/Master/master_list.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            members_list.append(row)

    return members_list


def get_server_roles(guild_id):

    server_roles = []
    with open(f'{os.getcwd()}/Workers/{guild_id}/{guild_id}.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            row = row[0][:-1]
            server_roles.append(row)

    return server_roles


def get_master_roles():

    master_roles = []
    with open(f'{os.getcwd()}/Master/master_roles.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            row = row[0][:-1]
            master_roles.append(row)

    return master_roles


def get_log_channel(guild_id):

    with open(f'{os.getcwd()}/Workers/{guild_id}/channel.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            row = row[0][:-1]
            return row


def check_role(guild, member, verify_self=False):
    roles_list = get_server_roles(member.guild.id)
    check_list = numpy.copy(copy_master_list())
    master_roles = get_master_roles()

    roles_to_add = []
    roles_to_remove = []

    x = numpy.where(check_list == member.name)
    role_id = check_list[x[0], 3:4]

    if verify_self:
        role_id = role_id[0]

    tier_four = guild.get_role(int(roles_list[3]))
    tier_three = guild.get_role(int(roles_list[2]))
    tier_two = guild.get_role(int(roles_list[1]))
    tier_one = guild.get_role(int(roles_list[0]))
    no_role = 0

    if any(member.name in sublist for sublist in check_list):
        if int(role_id) == int(master_roles[3]):
            roles_to_add.extend([tier_four, tier_three, tier_two, tier_one])
            return roles_to_add, roles_to_remove
        elif int(role_id) == int(master_roles[2]):
            roles_to_remove.append(tier_four)
            roles_to_add.extend([tier_three, tier_two, tier_one])
            return roles_to_add, roles_to_remove
        elif int(role_id) == int(master_roles[1]):
            roles_to_remove.extend([tier_four, tier_three])
            roles_to_add.extend([tier_two, tier_one])
            return roles_to_add, roles_to_remove
        elif int(role_id) == int(master_roles[0]):
            roles_to_remove.extend([tier_four, tier_three, tier_two])
            roles_to_add.append(tier_one)
            return roles_to_add, roles_to_remove
        else:
            print("Error")
    elif not any(member.name in sublist for sublist in check_list):
        roles_to_remove.extend([tier_four, tier_three, tier_two, tier_one])
        return no_role, roles_to_remove


def run_discord_bot():
    intents = nextcord.Intents.all()
    bot = nextcord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} is getting ready....')
        auto_mass_verify.start()

    @bot.event
    async def on_member_join(member):

        cwd = os.getcwd()
        worker_path = f'{cwd}/Workers/{member.guild.id}/Logs'
        worker_log = f'{worker_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(worker_path):
            os.makedirs(worker_path)

        channel = None
        if bot.get_channel(int(get_log_channel(member.guild.id))) is not None:
            channel = bot.get_channel(int(get_log_channel(member.guild.id)))

        with open(worker_log, 'a') as log:
            log.write(f'{member.name} joined the server at {tz_est} eastern time.\n')

        role = check_role(member.guild, member, True)
        if role[0] != 0:
            await member.add_roles(*role[0])
        elif role[0] == 0:
            await member.remove_roles(*role[1])

        roles_ids = get_server_roles(member.guild.id)
        user_roles = []
        for x in range(len(roles_ids)):
            user_roles.append(member.guild.get_role(int(roles_ids[x])))

        log_roles = []
        for role in member.roles:
            if role in user_roles:
                log_roles.append(role.name)

        with open(worker_log, 'a') as log:
            log.write(f'{member.name} received roles {log_roles} on joining the server.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(
                title=f'{member.name} received roles {log_roles} on joining the server.', color=0x000ff))

    @bot.event
    async def on_member_remove(member):

        cwd = os.getcwd()
        worker_path = f'{cwd}/Workers/{member.guild.id}/Logs'
        worker_log = f'{worker_path}/{member.guild.id}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(worker_path):
            os.makedirs(worker_path)

        channel = None
        if bot.get_channel(int(get_log_channel(member.guild.id))) is not None:
            channel = bot.get_channel(int(get_log_channel(member.guild.id)))

        with open(worker_log, 'a') as log:
            log.write(f'{member.name} left the server at {tz_est} eastern time.\n')

        roles_ids = get_server_roles(member.guild.id)
        user_roles = []
        for x in range(len(roles_ids)):
            user_roles.append(member.guild.get_role(int(roles_ids[x])))

        log_roles = []
        for role in member.roles:
            if role in user_roles:
                log_roles.append(role.name)

        with open(worker_log, 'a') as log:
            log.write(f'{member.name} had roles {log_roles} before leaving the server.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(
                title=f'{member.name} lost roles {log_roles} on leaving the server.', color=0x000ff))

    @bot.slash_command(description="Verify yourself for the federation bot.")
    async def self_verify(interaction: nextcord.Interaction):
        member = interaction.user

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Verifying user {member.name}...',
                                                    color=0x000ff), delete_after=15)

        cwd = os.getcwd()
        worker_path = f'{cwd}/Workers/{member.guild.id}/Logs'
        worker_log = f'{worker_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(worker_path):
            os.makedirs(worker_path)

        channel = None
        if bot.get_channel(int(get_log_channel(member.guild.id))) is not None:
            channel = bot.get_channel(int(get_log_channel(member.guild.id)))

        role = check_role(member.guild, member, True)
        if role[0] != 0:
            await member.remove_roles(*role[1])
            await member.add_roles(*role[0])

            added_roles_list = []
            removed_roles_list = []

            for x in range(len(role[0])):
                added_roles_list.append(role[0][x].name)

            for x in range(len(role[1])):
                removed_roles_list.append(role[1][x].name)

            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(title=f'{member.name} has been verified.', color=0x000ff))

            with open(worker_log, 'a') as log:
                log.write(f'{member.name} lost roles: {role[1]} on self verify at {tz_est} eastern time.\n')
                log.write(f'{member.name} received roles: {role[0]} on self verify at {tz_est} eastern time.\n')

            if channel is not None:
                time.sleep(1)
                await channel.send(embed=nextcord.Embed(
                    title=f'{member.name} lost roles {removed_roles_list} during self verification.', color=0x000ff))
                time.sleep(1)
                await channel.send(embed=nextcord.Embed(
                    title=f'{member.name} received roles {added_roles_list} during self verification.', color=0x000ff))

        elif role[0] == 0:
            await member.remove_roles(*role[1])

            with open(worker_log, 'a') as log:
                log.write(f'{member.name} received no roles on self verify at {tz_est} eastern time.\n')

            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(title=f'{member.name} no new roles to receive.', color=0x000ff))

    @bot.slash_command(description="Federation worker bot setup.")
    @application_checks.has_any_role("Federation Auditor")
    async def setup(interaction: nextcord.Interaction,
                    tier1: str, tier2: str, tier3: str, tier4: str, log_channel: str):

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="Beginning the setup process...",
                                                    color=0x000ff), delete_after=15)

        guild = interaction.guild
        cwd = os.getcwd()

        input_roles = [tier1, tier2, tier3, tier4]
        for x in range(4):
            if not input_roles[x].isdigit():
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(
                    title="You did not enter a valid integer. Please restart the setup process.", color=0x000ff))
                return

        if not log_channel.isdigit():
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title="You did not enter a valid integer. Please restart the setup process.", color=0x000ff))
            return

        if not os.path.exists(f'{cwd}/Workers/{guild.id}'):
            os.makedirs(f'{cwd}/Workers/{guild.id}')

        with open(f'{cwd}/Workers/{guild.id}/{guild.id}.csv', 'w', newline='') as csvfile:
            field_names = ['role_id', 'role_name']
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

        server_roles = []
        num_of_roles = 4
        for x in range(num_of_roles):

            added_role = False
            while added_role is False:
                role = interaction.guild.get_role(int(input_roles[x]))
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(
                    title=f'You entered the id for the role {role} for tier {x + 1}. Is this correct? (y/n)',
                    color=0x000ff), delete_after=15)

                check = await bot.wait_for('message', check=check_msg_content)

                if check.content == 'n':
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(title="Please input the correct role id:",
                                                                color=0x000ff), delete_after=15)

                    msg = await bot.wait_for('message', check=predicate)

                    if not msg.content.isdigit() or interaction.guild.get_role(int(msg.content)) is None:
                        time.sleep(1)
                        await interaction.send(embed=nextcord.Embed(title="You did not enter a valid rank id.",
                                                                    color=0x000ff), delete_after=15)
                        continue

                    input_roles[x] = interaction.guild.get_role(int(msg.content))

                elif check.content == 'y':
                    if guild.get_role(int(input_roles[x])) is None:
                        time.sleep(1)
                        await interaction.send(embed=nextcord.Embed(
                            title="You have saved an invalid role. Please restart the setup process.", color=0x000ff))
                        return

                    server_roles.append(input_roles[x])

                    with open(f'{cwd}/Workers/{guild.id}/{guild.id}.csv', 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=field_names)
                        writer.writerow({'role_id': str(role.id) + '\t', 'role_name': role.name})

                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(title="Role saved.", color=0x000ff), delete_after=15)

                    added_role = True

                else:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="Error saving role. Please restart the setup process",
                        color=0x000ff))

        channel = bot.get_channel(int(log_channel))
        correct_channel = False
        while not correct_channel:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title=f'The channel you wish for me to output logs in is {channel.name}'
                      f' Is this correct? (y/n). Enter X if you do not wish to use this feature. (x)',
                color=0x000ff))

            check = await bot.wait_for('message', check=check_msg_content)

            if check.content == 'n':
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Please input the correct channel id:",
                                                            color=0x000ff), delete_after=15)

                msg = await bot.wait_for('message', check=predicate)

                if not msg.content.isdigit() or bot.get_channel(int(msg.content)) is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(title="You did not enter a valid channel id.",
                                                                color=0x000ff), delete_after=15)
                    continue

                channel = bot.get_channel(int(msg.content))

            if check.content == 'y':
                if channel is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You have saved an invalid channel id. Please restart the setup process.",
                        color=0x000ff), delete_after=15)
                    return

                with open(f'{cwd}/Workers/{guild.id}/channel.csv', 'w', newline='') as csvfile:
                    field_names = ['channel_id', 'channel_name', 'server_name']
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    writer.writerow(
                        {'channel_id': str(channel.id) + '\t', 'channel_name': channel.name, 'server_name': guild.name})

                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Channel saved.", color=0x000ff), delete_after=15)

                correct_channel = True

            if check.content == 'x':
                correct_channel = True

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Setup has been completed.', color=0x000ff))

    @bot.slash_command(description="Changes the log channel.")
    @application_checks.has_any_role("Federation Auditor")
    async def move_log_channel(interaction: nextcord.Interaction, log_channel: str):

        cwd = os.getcwd()

        if interaction.guild.get_channel(int(log_channel)) is not None:
            channel = interaction.guild.get_channel(int(log_channel))
        elif interaction.guild.get_channel(int(log_channel)) is None or log_channel.isdigit() is False:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title="You did not enter a valid channel id. Please restart the move process.", color=0x000ff))
            return

        else:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title=f'Error occurred when moving log channel for server {interaction.guild.name}.',
                color=0x000ff))
            return

        correct_channel = False
        while not correct_channel:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title=f'The channel you wish for me to output logs in is {channel.name}.'
                      f' Is this correct? (y/n). Enter X if you do not wish to use this feature. (x)',
                color=0x000ff))

            check = await bot.wait_for('message', check=check_msg_content)

            if check.content == 'n':
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Please input the correct channel id:",
                                                            color=0x000ff), delete_after=15)

                msg = await bot.wait_for('message', check=predicate)

                if not msg.content.isdigit() or bot.get_channel(int(msg.content)) is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(title="You did not enter a valid channel id.",
                                                                color=0x000ff), delete_after=15)
                    continue

                channel = bot.get_channel(int(msg.content))

            if check.content == 'y':
                if channel is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You have saved an invalid channel id. Please restart the setup process.",
                        color=0x000ff), delete_after=15)
                    return

                with open(f'{cwd}/Workers/{interaction.guild.id}/channel.csv', 'w', newline='') as csvfile:
                    field_names = ['channel_id', 'channel_name', 'server_name']
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    writer.writerow(
                        {'channel_id': str(channel.id) + '\t', 'channel_name': channel.name,
                         'server_name': interaction.guild.name})

                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Channel saved.", color=0x000ff), delete_after=15)

                correct_channel = True

            if check.content == 'x':
                correct_channel = True

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Log channel has been set.', color=0x000ff))

    @bot.slash_command(description="Removes federation roles from everyone.", default_member_permissions=8)
    @application_checks.has_any_role("Federation Auditor")
    async def remove_roles(interaction: nextcord.Interaction):

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=".", color=0x000ff))

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="Removing all possible roles.",
                                                    color=0x000ff), delete_after=15)

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="This may take a few minutes...",
                                                    color=0x000ff), delete_after=15)

        cwd = os.getcwd()
        worker_path = f'{cwd}/Workers/{interaction.guild.id}/Logs'
        worker_log = f'{worker_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        channel = None
        if bot.get_channel(int(get_log_channel(interaction.guild.id))) is not None:
            channel = bot.get_channel(int(get_log_channel(interaction.guild.id)))

        with open(worker_log, 'a') as log:
            log.write(f'{interaction.user.name} began a mass role removal at {tz_est} eastern time.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} began a mass role removal.\n',
                                                    color=0x000ff))

        guild = interaction.user.guild
        roles_ids = get_server_roles(guild.id)
        roles_list = []
        for x in range(len(roles_ids)):
            roles_list.append(guild.get_role(int(roles_ids[x])))

        count = 1
        member_count = len(guild.humans)
        for member in guild.humans:
            await member.remove_roles(*roles_list)
            time.sleep(1)
            await interaction.edit_original_message(embed=nextcord.Embed(
                title=f'{count} / {member_count} member\'s had roles checked and/or removed',
                color=0x000ff))

            count += 1

        time.sleep(1)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Removing roles completed.", color=0x000ff))

        with open(worker_log, 'a') as log:
            log.write(f'{interaction.user.name} completed a mass role removal at {tz_est} eastern time.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} finished a mass role removal.\n',
                                                    color=0x000ff))

    @bot.slash_command(description="Federation verification process for all members.")
    @application_checks.has_any_role("Federation Auditor")
    async def mass_verify(interaction: nextcord.Interaction):
        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=".", color=0x000ff))

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="Starting verification.", color=0x000ff), delete_after=15)

        cwd = os.getcwd()
        worker_path = f'{cwd}/Workers/{interaction.guild.id}/Logs'
        worker_log = f'{worker_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(worker_path):
            os.makedirs(worker_path)

        channel = None
        if bot.get_channel(int(get_log_channel(interaction.guild.id))) is not None:
            channel = bot.get_channel(int(get_log_channel(interaction.guild.id)))

        with open(worker_log, 'a') as log:
            log.write(f'{interaction.user.name} began manual mass verify at {tz_est} eastern time.\n')

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="This may take a few minutes...",
                                                    color=0x000ff), delete_after=15)

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} began a manual mass verify.\n',
                                                    color=0x000ff))

        guild = interaction.user.guild
        count = 1
        member_count = len(guild.humans)
        for member in guild.humans:
            time.sleep(1)
            await interaction.edit_original_message(embed=nextcord.Embed(title=f'{count} / {member_count} verified',
                                                                         color=0x000ff))
            role = check_role(guild, member)
            if role[0] != 0:
                await member.remove_roles(*role[1])
                await member.add_roles(*role[0])

                with open(worker_log, 'a') as log:
                    log.write(f'{member.name} lost roles: {role[1]} at {tz_est} eastern time.\n')
                    log.write(f'{member.name} received roles: {role[0]} at {tz_est} eastern time.\n')

            elif role[0] == 0:
                await member.remove_roles(*role[1])

                with open(worker_log, 'a') as log:
                    log.write(f'{member.name} lost all roles at {tz_est} eastern time.\n')

            count += 1

        time.sleep(1)
        await interaction.edit_original_message(embed=nextcord.Embed(
            title="Mass verification completed!",
            color=0x000ff))

        with open(worker_log, 'a') as log:
            log.write(f'Manual mass verification ended at {tz_est} eastern time.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} completed a manual mass verify.\n',
                                                    color=0x000ff))

    @tasks.loop(time=datetime.time(hour=9, minute=1))
    async def auto_mass_verify():

        for guild in bot.guilds:

            cwd = os.getcwd()
            worker_path = f'{cwd}/Workers/{guild.id}/Logs'
            worker_log = f'{worker_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
            tz_est = datetime.datetime.now().strftime("%H:%M:%S")

            if not os.path.exists(worker_path):
                os.makedirs(worker_path)

            current_time = time.time()
            for file in worker_path:
                creation_time = os.path.getctime(file)
                if (current_time - creation_time) // (24 * 3600) >= 31:
                    try:
                        os.remove(file)
                    except FileNotFoundError:
                        print(f'Could not delete {file} during auto master list gen at {tz_est} eastern time.')
                        continue

            channel = None
            if bot.get_channel(int(get_log_channel(guild.id))) is not None:
                channel = bot.get_channel(int(get_log_channel(guild.id)))

            with open(worker_log, 'a') as log:
                log.write(f'Auto mass verify began at {tz_est} eastern time.\n')

            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title="Beginning today's auto verification process...",
                                                    color=0x000ff))

            count = 1
            member_count = len(guild.humans)
            for member in guild.humans:
                await channel.last_message.edit(embed=nextcord.Embed(title=f'{count} / {member_count}% completed',
                                                                     color=0x000ff))

                role = check_role(guild, member)
                if role[0] != 0:
                    await member.remove_roles(*role[1])
                    await member.add_roles(*role[0])

                    with open(worker_log, 'a') as log:
                        log.write(f'{member.name} lost roles: {role[1]} at {tz_est} eastern time.\n')
                        log.write(f'{member.name} received roles: {role[0]} at {tz_est} eastern time.\n')

                elif role[0] == 0:
                    await member.remove_roles(*role[1])

                    with open(worker_log, 'a') as log:
                        log.write(f'{member.name} lost all roles at {tz_est} eastern time.\n')

                count += 1

            with open(worker_log, 'a') as log:
                log.write(f'Auto mass verify completed at {tz_est} eastern time.\n')

            if channel is not None:
                time.sleep(1)
                await channel.send(embed=nextcord.Embed(title=f"Today's auto mass verification process is complete.",
                                                        color=0x000ff))

    @auto_mass_verify.before_loop
    async def before_loop():
        await bot.wait_until_ready()
        time.sleep(1)
        print(f'{bot.user} is ready....')

    bot.run(TOKEN)
