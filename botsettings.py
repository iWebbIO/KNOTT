import os
from dotenv import load_dotenv

load_dotenv()

name = os.getenv('BOT_NAME', 'KnoTT')
token = os.getenv('BOT_TOKEN', 'your_bot_token_here')
owner_id = int(os.getenv('OWNER_ID', '697509268085145630'))

database_name = os.getenv('DATABASE_NAME', 'Users.db')

command_prefix = os.getenv('COMMAND_PREFIX', 'k')
xp_per_message = int(os.getenv('XP_PER_MESSAGE', '1'))
xp_cooldown = int(os.getenv('XP_COOLDOWN', '60'))
level_up_base = int(os.getenv('LEVEL_UP_BASE', '50'))

enable_global_leaderboard = os.getenv('ENABLE_GLOBAL_LEADERBOARD', 'True').lower() == 'true'
enable_server_leaderboard = os.getenv('ENABLE_SERVER_LEADERBOARD', 'True').lower() == 'true'
enable_rank_roles = os.getenv('ENABLE_RANK_ROLES', 'False').lower() == 'true'
