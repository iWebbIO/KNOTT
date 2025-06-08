import aiosqlite
import asyncio
from typing import Optional, List, Tuple
import botsettings

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or botsettings.database_name
        
    async def init_database(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_message_time INTEGER DEFAULT 0,
                    total_messages INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, guild_id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    xp_multiplier REAL DEFAULT 1.0,
                    level_up_channel INTEGER,
                    announcement_enabled BOOLEAN DEFAULT TRUE,
                    custom_prefix TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rank_roles (
                    guild_id INTEGER,
                    level INTEGER,
                    role_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, level)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    requirement_type TEXT NOT NULL,
                    requirement_value INTEGER NOT NULL,
                    reward_xp INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_id INTEGER,
                    guild_id INTEGER,
                    achievement_id INTEGER,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id, achievement_id),
                    FOREIGN KEY (achievement_id) REFERENCES achievements (id)
                )
            """)
            
            await db.commit()
    
    async def get_user_data(self, user_id: int, guild_id: int = None) -> Optional[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id:
                cursor = await db.execute(
                    "SELECT xp, level, total_messages FROM users WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild_id)
                )
            else:
                cursor = await db.execute(
                    "SELECT SUM(xp) as total_xp, MAX(level) as max_level, SUM(total_messages) as total_messages FROM users WHERE user_id = ?",
                    (user_id,)
                )
            return await cursor.fetchone()
    
    async def update_user_xp(self, user_id: int, guild_id: int, xp_gain: int, current_time: int) -> Tuple[int, int, bool]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT xp, level, total_messages FROM users WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            )
            result = await cursor.fetchone()
            
            if result:
                current_xp, current_level, total_messages = result
                new_xp = current_xp + xp_gain
                new_level = current_level
                leveled_up = False
                
                xp_needed = current_level * botsettings.level_up_base
                if new_xp >= xp_needed:
                    new_xp = new_xp - xp_needed
                    new_level += 1
                    leveled_up = True
                
                await db.execute(
                    "UPDATE users SET xp = ?, level = ?, last_message_time = ?, total_messages = ? WHERE user_id = ? AND guild_id = ?",
                    (new_xp, new_level, current_time, total_messages + 1, user_id, guild_id)
                )
            else:
                new_xp = xp_gain
                new_level = 1
                leveled_up = False
                
                await db.execute(
                    "INSERT INTO users (user_id, guild_id, xp, level, last_message_time, total_messages) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, guild_id, new_xp, new_level, current_time, 1)
                )
            
            await db.commit()
            return new_xp, new_level, leveled_up
    
    async def get_leaderboard(self, guild_id: int = None, limit: int = 20) -> List[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id:
                cursor = await db.execute(
                    "SELECT user_id, level, xp, total_messages FROM users WHERE guild_id = ? ORDER BY level DESC, xp DESC LIMIT ?",
                    (guild_id, limit)
                )
            else:
                cursor = await db.execute(
                    "SELECT user_id, SUM(xp) as total_xp, MAX(level) as max_level, SUM(total_messages) as total_messages FROM users GROUP BY user_id ORDER BY max_level DESC, total_xp DESC LIMIT ?",
                    (limit,)
                )
            return await cursor.fetchall()
    
    async def get_user_rank(self, user_id: int, guild_id: int = None) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            if guild_id:
                cursor = await db.execute(
                    "SELECT COUNT(*) + 1 FROM users WHERE guild_id = ? AND (level > (SELECT level FROM users WHERE user_id = ? AND guild_id = ?) OR (level = (SELECT level FROM users WHERE user_id = ? AND guild_id = ?) AND xp > (SELECT xp FROM users WHERE user_id = ? AND guild_id = ?)))",
                    (guild_id, user_id, guild_id, user_id, guild_id, user_id, guild_id)
                )
            else:
                cursor = await db.execute(
                    "SELECT COUNT(*) + 1 FROM (SELECT user_id, MAX(level) as max_level, SUM(xp) as total_xp FROM users GROUP BY user_id) WHERE max_level > (SELECT MAX(level) FROM users WHERE user_id = ?) OR (max_level = (SELECT MAX(level) FROM users WHERE user_id = ?) AND total_xp > (SELECT SUM(xp) FROM users WHERE user_id = ?))",
                    (user_id, user_id, user_id)
                )
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def get_guild_settings(self, guild_id: int) -> Optional[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT xp_multiplier, level_up_channel, announcement_enabled, custom_prefix FROM guild_settings WHERE guild_id = ?",
                (guild_id,)
            )
            return await cursor.fetchone()
    
    async def update_guild_settings(self, guild_id: int, **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT guild_id FROM guild_settings WHERE guild_id = ?", (guild_id,))
            exists = await cursor.fetchone()
            
            if exists:
                set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
                values = list(kwargs.values()) + [guild_id]
                await db.execute(f"UPDATE guild_settings SET {set_clause} WHERE guild_id = ?", values)
            else:
                columns = ["guild_id"] + list(kwargs.keys())
                placeholders = ", ".join(["?"] * len(columns))
                values = [guild_id] + list(kwargs.values())
                await db.execute(f"INSERT INTO guild_settings ({', '.join(columns)}) VALUES ({placeholders})", values)
            
            await db.commit()
    
    async def get_user_achievements(self, user_id: int, guild_id: int = None) -> List[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT a.name, a.description, ua.earned_at 
                FROM user_achievements ua
                JOIN achievements a ON ua.achievement_id = a.id
                WHERE ua.user_id = ? AND ua.guild_id = ?
                ORDER BY ua.earned_at DESC
            """, (user_id, guild_id))
            return await cursor.fetchall()
    
    async def get_all_achievements(self) -> List[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT name, description, requirement_type, requirement_value FROM achievements ORDER BY requirement_value"
            )
            return await cursor.fetchall()
    
    async def get_total_achievements(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM achievements")
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def check_and_award_achievements(self, user_id: int, guild_id: int, level: int, total_messages: int):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT a.id, a.name, a.requirement_type, a.requirement_value, a.reward_xp
                FROM achievements a
                WHERE a.id NOT IN (
                    SELECT achievement_id FROM user_achievements 
                    WHERE user_id = ? AND guild_id = ?
                )
            """, (user_id, guild_id))
            
            available_achievements = await cursor.fetchall()
            earned_achievements = []
            
            for achievement in available_achievements:
                achievement_id, name, req_type, req_value, reward_xp = achievement
                
                if req_type == "level" and level >= req_value:
                    earned_achievements.append((achievement_id, name, reward_xp))
                elif req_type == "messages" and total_messages >= req_value:
                    earned_achievements.append((achievement_id, name, reward_xp))
            
            for achievement_id, name, reward_xp in earned_achievements:
                await db.execute(
                    "INSERT INTO user_achievements (user_id, guild_id, achievement_id) VALUES (?, ?, ?)",
                    (user_id, guild_id, achievement_id)
                )
                
                if reward_xp > 0:
                    await db.execute(
                        "UPDATE users SET xp = xp + ? WHERE user_id = ? AND guild_id = ?",
                        (reward_xp, user_id, guild_id)
                    )
            
            await db.commit()
            return earned_achievements
    
    async def initialize_default_achievements(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM achievements")
            count = await cursor.fetchone()
            
            if count[0] == 0:
                default_achievements = [
                    ("First Steps", "Send your first message", "messages", 1, 10),
                    ("Chatterbox", "Send 100 messages", "messages", 100, 50),
                    ("Conversationalist", "Send 500 messages", "messages", 500, 100),
                    ("Social Butterfly", "Send 1000 messages", "messages", 1000, 200),
                    ("Community Leader", "Send 5000 messages", "messages", 5000, 500),
                    ("Legend", "Send 10000 messages", "messages", 10000, 1000),
                    
                    ("Getting Started", "Reach level 5", "level", 5, 25),
                    ("Rising Star", "Reach level 10", "level", 10, 50),
                    ("Experienced", "Reach level 25", "level", 25, 100),
                    ("Veteran", "Reach level 50", "level", 50, 250),
                    ("Elite", "Reach level 100", "level", 100, 500),
                    ("Master", "Reach level 200", "level", 200, 1000),
                    ("Grandmaster", "Reach level 300", "level", 300, 2000),
                    ("Legendary", "Reach level 375", "level", 375, 5000),
                ]
                
                for achievement in default_achievements:
                    await db.execute(
                        "INSERT INTO achievements (name, description, requirement_type, requirement_value, reward_xp) VALUES (?, ?, ?, ?, ?)",
                        achievement
                    )
                
                await db.commit()
    
    async def add_rank_role(self, guild_id: int, level: int, role_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO rank_roles (guild_id, level, role_id) VALUES (?, ?, ?)",
                (guild_id, level, role_id)
            )
            await db.commit()
    
    async def remove_rank_role(self, guild_id: int, level: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM rank_roles WHERE guild_id = ? AND level = ?",
                (guild_id, level)
            )
            await db.commit()
    
    async def get_rank_roles(self, guild_id: int) -> List[Tuple]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT level, role_id FROM rank_roles WHERE guild_id = ? ORDER BY level",
                (guild_id,)
            )
            return await cursor.fetchall()
    
    async def get_rank_roles_for_level(self, guild_id: int, level: int) -> List[int]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT role_id FROM rank_roles WHERE guild_id = ? AND level <= ? ORDER BY level",
                (guild_id, level)
            )
            results = await cursor.fetchall()
            return [role_id for (role_id,) in results]
