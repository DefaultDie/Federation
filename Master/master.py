import os
import time
import datetime
import csv
import nextcord
from nextcord.ext import application_checks, commands, tasks

TOKEN = ''  # Your token here.


def check_msg_content(m):
    return m.content in ('y', 'Y', 'n', 'N') and not m.author.bot


def check_msg_content_x(m):
    return m.content in ('y', 'Y', 'n', 'N', 'x', 'X') and not m.author.bot


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


def get_master_roles():

    master_roles = []
    with open(f'{os.getcwd()}/Master/master_roles.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            row = row[0][:-1]
            master_roles.append(row)

    return master_roles


def get_log_channel():

    try:
        with open(f'{os.getcwd()}/Master/master_channel.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                row = row[0][:-1]
                return row
    except FileNotFoundError:
        return 0


def check_role(member):

    master_roles = get_master_roles()
    if member.get_role(int(master_roles[3])) is not None:
        return member.get_role(int(master_roles[3]))
    elif member.get_role(int(master_roles[2])) is not None:
        return member.get_role(int(master_roles[2]))
    elif member.get_role(int(master_roles[1])) is not None:
        return member.get_role(int(master_roles[1]))
    elif member.get_role(int(master_roles[0])) is not None:
        return member.get_role(int(master_roles[0]))
    else:
        return 0


def run_discord_bot():
    intents = nextcord.Intents.all()
    bot = commands.Bot(intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is getting ready....")
        auto_master_list.start()

    @bot.slash_command(description="Verify yourself for the federation bot.")
    @commands.cooldown(1, 30)
    async def self_verify(interaction: nextcord.Interaction):

        member = interaction.user
        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Verifying {member.name}....',
                                                    color=0x000ff), delete_after=15)

        cwd = os.getcwd()
        master_path = f'{cwd}/Master/Logs'
        master_log = f'{master_path}/Logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        field_names = ['username', str('user_id'), 'role', 'role_id']
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(master_path):
            os.makedirs(master_path)

        channel = None
        if bot.get_channel(int(get_log_channel())) is not None:
            channel = bot.get_channel(int(get_log_channel()))

        role = check_role(member)
        master_list = copy_master_list()
        if any(member.name in sublist for sublist in master_list):
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(title=f'{member.name} has already been verified.',
                                                        color=0x000ff))

            with open(master_log, 'a') as log:
                log.write(f'{member.name} tried to re-verify at {tz_est} eastern time.\n')

            if channel is not None:
                time.sleep(1)
                await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} tried to re-verify.',
                                                        color=0x000ff))

        else:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(title=f'{member.name} has been verified.', color=0x000ff))

            with open(f'{cwd}/Master/master_list.csv', 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writerow({'username': member.name, 'user_id': str(member.id) + '\t',
                                 'role': role, 'role_id': str(role.id) + '\t'})

            with open(master_log, 'a') as log:
                log.write(f'{member.name} was verified with role {role} at {tz_est} eastern time.\n')

            if channel is not None:
                time.sleep(1)
                await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} was verified with role {role}.',
                                                        color=0x000ff))

    @bot.slash_command(description="Federation boss bot setup.")
    @application_checks.has_any_role("Federation Auditor")
    async def setup(interaction: nextcord.Interaction,
                    tier1: str, tier2: str, tier3: str, tier4: str, log_channel: str):

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="Beginning the setup process...",
                                                    color=0x000ff), delete_after=15)

        input_roles = [tier1, tier2, tier3, tier4]
        for x in range(len(input_roles)):
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

        cwd = os.getcwd()
        if not os.path.exists(f'{cwd}/Master'):
            os.makedirs(f'{cwd}/Master')

        if not os.path.exists(f'{cwd}/Workers'):
            os.makedirs(f'{cwd}/Workers')

        with open(f'{cwd}/Master/master_roles.csv', 'w', newline='') as csvfile:
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
                    title=f"You entered the id for the role {role} for tier {x+1}. Is this correct? (y/n)",
                    color=0x000ff), delete_after=15)

                check = await bot.wait_for('message', check=check_msg_content)

                if check.content == 'n' or check.content == 'N':
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="Please input the correct role id:", color=0x000ff), delete_after=15)

                    msg = await bot.wait_for('message', check=predicate)

                    if not msg.content.isdigit() or interaction.guild.get_role(int(msg.content)) is None:
                        time.sleep(1)
                        await interaction.send(embed=nextcord.Embed(
                            title="You did not enter a valid rank id.", color=0x000ff), delete_after=15)
                        continue

                    input_roles[x] = interaction.guild.get_role(int(msg.content))

                elif check.content == 'y' or check.content == 'Y':
                    if interaction.guild.get_role(int(input_roles[x])) is None:
                        time.sleep(1)
                        await interaction.send(embed=nextcord.Embed(
                            title="You have saved an invalid role. Please restart the setup process.",
                            color=0x000ff), delete_after=15)
                        return

                    server_roles.append(role)

                    with open(f'{cwd}/Master/master_roles.csv', 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=field_names)
                        writer.writerow({'role_id': str(role.id) + '\t', 'role_name': role.name})

                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(title="Role saved.", color=0x000ff), delete_after=15)

                    added_role = True
                else:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="Error saving role. Please restart the setup process.", color=0x000ff))

        channel = bot.get_channel(int(log_channel))
        correct_channel = False
        while not correct_channel:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title=f'The channel you wish for me to output logs in is {channel.name}.'
                      f' Is this correct? (y/n). Enter X if you do not wish to use this feature. (x)',
                color=0x000ff), delete_after=15)

            check = await bot.wait_for('message', check=check_msg_content_x)

            if check.content == 'n' or check.content == 'N':
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(
                    title="Please input the correct channel id:", color=0x000ff), delete_after=15)

                msg = await bot.wait_for('message', check=predicate)

                if not msg.content.isdigit() or bot.get_channel(int(msg.content)) is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You did not enter a valid channel id.", color=0x000ff), delete_after=15)
                    continue

                channel = bot.get_channel(int(msg.content))

            if check.content == 'y' or check.content == 'Y':
                if channel is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You have saved an invalid channel id. Please restart the setup process.",
                        color=0x000ff), delete_after=15)
                    return

                with open(f'{cwd}/Master/master_channel.csv', 'w', newline='') as csvfile:
                    field_names = ['channel_id', 'channel_name']
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    writer.writerow({'channel_id': str(channel.id) + '\t', 'channel_name': channel.name})

                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Channel saved.", color=0x000ff), delete_after=15)

                correct_channel = True

            if check.content == 'x' or check.content == 'X':
                correct_channel = True

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Setup has been completed.', color=0x000ff))

    @bot.slash_command(description="Changes the log channel.")
    @application_checks.has_any_role("Federation Auditor")
    async def move_log_channel(interaction: nextcord.Interaction, log_channel: str):

        if not log_channel.isdigit():
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title="You did not enter a valid integer. Please restart the setup process.",
                color=0x000ff))
            return

        channel = None
        if interaction.guild.get_channel(int(log_channel)) is not None:
            channel = interaction.guild.get_channel(int(log_channel))

        correct_channel = False
        while not correct_channel:
            time.sleep(1)
            await interaction.send(embed=nextcord.Embed(
                title=f'The channel you wish for me to output logs in is {channel.name}.'
                      f' Is this correct? (y/n). Enter X if you do not wish to use this feature. (x)',
                color=0x000ff))

            check = await bot.wait_for('message', check=check_msg_content_x)

            if check.content == 'n' or check.content == 'N':
                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(title="Please input the correct channel id:",
                                                            color=0x000ff), delete_after=15)

                msg = await bot.wait_for('message', check=predicate)

                if not msg.content.isdigit() or bot.get_channel(int(msg.content)) is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You did not enter a valid channel id.", color=0x000ff), delete_after=15)
                    continue

                channel = bot.get_channel(int(msg.content))

            if check.content == 'y' or check.content == 'Y':
                time.sleep(1)
                if channel is None:
                    time.sleep(1)
                    await interaction.send(embed=nextcord.Embed(
                        title="You have saved an invalid channel id. Please restart the setup process.",
                        color=0x000ff), delete_after=15)
                    return

                with open(f'{os.getcwd()}/Master/channel.csv', 'w', newline='') as csvfile:
                    field_names = ['channel_id', 'channel_name', 'server_name']
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writeheader()
                    writer.writerow(
                        {'channel_id': str(channel.id) + '\t', 'channel_name': channel.name,
                         'server_name': interaction.guild.name})

                time.sleep(1)
                await interaction.send(embed=nextcord.Embed(
                    title="Channel saved.", color=0x000ff), delete_after=15)

                correct_channel = True

            if check.content == 'x' or check.content == 'X':
                correct_channel = True

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title=f'Log channel has been set.', color=0x000ff))

    @bot.slash_command(description="Creates the master list.")
    @application_checks.has_any_role("Federation Auditor")
    async def create_master_list(interaction: nextcord.Interaction):

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(
            title="Generating master list.", color=0x000ff))

        cwd = os.getcwd()
        master_path = f'{cwd}/Master/Logs'
        master_log = f'{master_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(master_path):
            os.makedirs(master_path)

        channel = None
        if bot.get_channel(int(get_log_channel())) is not None:
            channel = bot.get_channel(int(get_log_channel()))

        with open(f'{cwd}/Master/master_list.csv', 'w', newline='') as csvfile:
            field_names = ['username', str('user_id'), 'role', 'role_id']
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

        time.sleep(1)
        await interaction.send(embed=nextcord.Embed(title="This may take a moment...", color=0x000ff), delete_after=15)

        guild = interaction.guild
        count = 1
        member_count = len(guild.humans)
        for member in guild.members:
            role = check_role(member)
            if role == 0:
                continue
            else:
                with open(f'{cwd}/Master/master_list.csv', 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writerow({'username': member.name, 'user_id': str(member.id) + '\t',
                                     'role': role, 'role_id': str(role.id) + '\t'})

            if count % 500 == 0:
                time.sleep(1)
                await interaction.edit_original_message(
                    embed=nextcord.Embed(title=f'{count} / {member_count} member\'s added to the list', color=0x000ff))
            count += 1

        time.sleep(1)
        await interaction.edit_original_message(embed=nextcord.Embed(title="Master list completed!", color=0x000ff))

        with open(master_log, 'a') as log:
            log.write(f'{interaction.user.name} manually generated master list at {tz_est} eastern time.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'{interaction.user.name} manually generated master list.',
                                                    color=0x000ff))

    @tasks.loop(time=datetime.time(hour=8, minute=1))
    async def auto_master_list():
        cwd = os.getcwd()
        master_path = f'{cwd}/Master/Logs'
        master_log = f'{master_path}/logs_{datetime.date.today().strftime("%d_%m_%Y")}.txt'
        tz_est = datetime.datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(master_path):
            os.makedirs(master_path)

        current_time = time.time()
        for file in os.listdir(master_path):
            creation_time = os.path.getctime(f'{master_path}/{file}')
            if (current_time - creation_time) // (24 * 3600) >= 31:
                try:
                    os.remove(f'{master_path}/{file}')
                except FileNotFoundError:
                    print(f'Could not delete {file} during auto master list gen at {tz_est} eastern time.')
                    continue

        channel = None
        if bot.get_channel(int(get_log_channel())) is not None:
            channel = bot.get_channel(int(get_log_channel()))

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title="Creating today's master list...", color=0x000ff))

        with open(f'{cwd}/Master/master_list.csv', 'w', newline='') as csvfile:
            field_names = ['username', str('user_id'), 'role', 'role_id']
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()

        guild = bot.guilds[0]
        for member in guild.members:
            role = check_role(member)
            if role != 0:
                with open(f'{cwd}/Master/master_list.csv', 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=field_names)
                    writer.writerow({'username': member.name, 'user_id': str(member.id) + '\t',
                                     'role': role, 'role_id': str(role.id) + '\t'})

        with open(master_log, 'a') as log:
            log.write(f'Completed auto generated master list occurred at {tz_est} eastern time.\n')

        if channel is not None:
            time.sleep(1)
            await channel.send(embed=nextcord.Embed(title=f'Completed auto generated master list occurred.',
                                                    color=0x000ff))

    @auto_master_list.before_loop
    async def before_loop():
        await bot.wait_until_ready()
        time.sleep(1)
        print(f"{bot.user} is ready....")

    bot.run(TOKEN)
