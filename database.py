import sqlite3
from typing import Dict, Any
from config import CURRENCY_COINS, CURRENCY_DIAMONDS
import discord

class Database:
    def __init__(self, db_name: str = "bot.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize database and create necessary tables"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Create table for storing balances
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_balance (
                    user_id INTEGER PRIMARY KEY,
                    coins INTEGER DEFAULT 0,
                    diamonds INTEGER DEFAULT 0
                )
            """)
            
            # Create table for personal roles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    role_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    owner_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create table for linking users and roles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    is_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, role_id, guild_id)
                )
            """)
            
            # Table for private rooms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS private_rooms (
                    room_id INTEGER PRIMARY KEY,    -- Text channel ID
                    voice_id INTEGER NOT NULL,      -- Voice channel ID
                    role_id INTEGER NOT NULL,       -- Access role ID
                    guild_id INTEGER NOT NULL,
                    owner_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for linking users and rooms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_members (
                    user_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    is_owner BOOLEAN DEFAULT 0,
                    is_coowner BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, room_id, guild_id)
                )
            """)
            
            # Table for tracking time in rooms
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS room_time (
                    user_id INTEGER NOT NULL,
                    room_id INTEGER NOT NULL,
                    total_time INTEGER DEFAULT 0,  -- Total time in seconds
                    last_join TIMESTAMP,          -- Last join time
                    PRIMARY KEY (user_id, room_id)
                )
            """)
            
            # Table for marriages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marriages (
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user1_id, user2_id)
                )
            """)
            
            # Table for tracking time in voice channels
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_activity (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    total_time INTEGER DEFAULT 0,
                    last_join TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            # Table for tracking messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_activity (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            
            conn.commit()

    def get_balance(self, user_id: int) -> Dict[str, int]:
        """Get user balance"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT coins, diamonds FROM user_balance WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result is None:
                # If user is not in DB, create a record
                cursor.execute(
                    "INSERT INTO user_balance (user_id, coins, diamonds) VALUES (?, 0, 0)",
                    (user_id,)
                )
                conn.commit()
                return {"coins": 0, "diamonds": 0}
            
            return {"coins": result[0], "diamonds": result[1]}

    def update_balance(self, user_id: int, coins: int = None, diamonds: int = None):
        """Update user balance"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            if coins is not None:
                cursor.execute(
                    "UPDATE user_balance SET coins = ? WHERE user_id = ?",
                    (coins, user_id)
                )
            
            if diamonds is not None:
                cursor.execute(
                    "UPDATE user_balance SET diamonds = ? WHERE user_id = ?",
                    (diamonds, user_id)
                )
            
            conn.commit() 

    def add_currency(self, user_id: int, currency_type: str, amount: int):
        """Add currency to user"""
        current_balance = self.get_balance(user_id)
        
        if currency_type.lower() == "coins":
            new_amount = current_balance["coins"] + amount
            self.update_balance(user_id, coins=new_amount)
        elif currency_type.lower() == "diamonds":
            new_amount = current_balance["diamonds"] + amount
            self.update_balance(user_id, diamonds=new_amount)
            
        return self.get_balance(user_id) 

    def add_role(self, role_id: int, guild_id: int, owner_id: int):
        """Add new role"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO roles (role_id, guild_id, owner_id) VALUES (?, ?, ?)",
                (role_id, guild_id, owner_id)
            )
            # Automatically add role to owner
            cursor.execute(
                "INSERT OR REPLACE INTO user_roles (user_id, role_id, guild_id) VALUES (?, ?, ?)",
                (owner_id, role_id, guild_id)
            )
            conn.commit()

    def add_user_role(self, user_id: int, role_id: int, guild_id: int):
        """Add role to user"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_roles (user_id, role_id, guild_id) VALUES (?, ?, ?)",
                (user_id, role_id, guild_id)
            )
            conn.commit()

    def toggle_role(self, user_id: int, role_id: int, guild_id: int, enabled: bool):
        """Enable/disable role"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_roles SET is_enabled = ? WHERE user_id = ? AND role_id = ? AND guild_id = ?",
                (enabled, user_id, role_id, guild_id)
            )
            conn.commit()

    def get_user_roles(self, user_id: int, guild_id: int) -> list:
        """Get list of user roles"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.role_id, ur.is_enabled, 
                       CASE WHEN r.owner_id = ? THEN 1 ELSE 0 END as is_owner
                FROM roles r
                JOIN user_roles ur ON r.role_id = ur.role_id
                WHERE ur.user_id = ? AND r.guild_id = ?
            """, (user_id, user_id, guild_id))
            return cursor.fetchall()

    def delete_role(self, role_id: int, guild_id: int):
        """Delete role"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roles WHERE role_id = ? AND guild_id = ?", (role_id, guild_id))
            cursor.execute("DELETE FROM user_roles WHERE role_id = ? AND guild_id = ?", (role_id, guild_id))
            conn.commit()

    def is_role_owner(self, user_id: int, role_id: int, guild_id: int) -> bool:
        """Check if user is role owner"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM roles WHERE role_id = ? AND guild_id = ? AND owner_id = ?",
                (role_id, guild_id, user_id)
            )
            return cursor.fetchone() is not None 

    def add_private_room(self, room_id: int, voice_id: int, role_id: int, 
                       guild_id: int, owner_id: int, name: str):
        """Add new private room"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO private_rooms 
                   (room_id, voice_id, role_id, guild_id, owner_id, name) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (room_id, voice_id, role_id, guild_id, owner_id, name)
            )
            # Add owner to members
            cursor.execute(
                """INSERT INTO room_members 
                   (user_id, room_id, guild_id, is_owner) 
                   VALUES (?, ?, ?, 1)""",
                (owner_id, room_id, guild_id)
            )
            conn.commit()

    def get_user_rooms(self, user_id: int, guild_id: int) -> list:
        """Get list of user rooms"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    pr.room_id,
                    pr.voice_id,
                    pr.role_id,
                    pr.name,
                    rm.is_owner,
                    rm.is_coowner
                FROM private_rooms pr
                JOIN room_members rm ON pr.room_id = rm.room_id
                WHERE rm.user_id = ? AND pr.guild_id = ?
            """, (user_id, guild_id))
            return cursor.fetchall()

    def add_room_member(self, user_id: int, room_id: int, guild_id: int, 
                       is_coowner: bool = False):
        """Add user to room"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO room_members 
                   (user_id, room_id, guild_id, is_coowner) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, room_id, guild_id, is_coowner)
            )
            conn.commit()

    def remove_room_member(self, user_id: int, room_id: int, guild_id: int):
        """Remove user from room"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM room_members WHERE user_id = ? AND room_id = ? AND guild_id = ?",
                (user_id, room_id, guild_id)
            )
            conn.commit()

    def delete_room(self, room_id: int, guild_id: int):
        """Delete room"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM private_rooms WHERE room_id = ? AND guild_id = ?",
                (room_id, guild_id)
            )
            cursor.execute(
                "DELETE FROM room_members WHERE room_id = ? AND guild_id = ?",
                (room_id, guild_id)
            )
            conn.commit() 

    def get_room_data(self, room_id: int) -> dict:
        """Get room information"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT room_id, voice_id, role_id, guild_id, owner_id, name
                FROM private_rooms 
                WHERE room_id = ?
            """, (room_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    "room_id": result[0],
                    "voice_id": result[1],
                    "role_id": result[2],
                    "guild_id": result[3],
                    "owner_id": result[4],
                    "name": result[5]
                }
            return None 

    def update_room_time(self, user_id: int, room_id: int, is_join: bool):
        """Update time in room"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if is_join:
                # User joined the room
                cursor.execute(
                    """INSERT OR REPLACE INTO room_time 
                       (user_id, room_id, last_join) 
                       VALUES (?, ?, CURRENT_TIMESTAMP)""",
                    (user_id, room_id)
                )
            else:
                # User left the room
                cursor.execute("""
                    UPDATE room_time 
                    SET total_time = total_time + 
                        (strftime('%s', 'now') - strftime('%s', last_join)),
                        last_join = NULL
                    WHERE user_id = ? AND room_id = ? AND last_join IS NOT NULL
                """, (user_id, room_id))
            conn.commit()

    def get_room_members(self, room_id: int) -> list:
        """Get list of room members with their time"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    rm.user_id,
                    rm.is_owner,
                    rm.is_coowner,
                    COALESCE(rt.total_time, 0) as total_time,
                    rt.last_join
                FROM room_members rm
                LEFT JOIN room_time rt ON rm.user_id = rt.user_id AND rm.room_id = rt.room_id
                WHERE rm.room_id = ?
                ORDER BY rm.is_owner DESC, rm.is_coowner DESC
            """, (room_id,))
            return cursor.fetchall() 

    def get_member_data(self, user_id: int, room_id: int) -> dict:
        """Get room member data"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_owner, is_coowner
                FROM room_members
                WHERE user_id = ? AND room_id = ?
            """, (user_id, room_id))
            result = cursor.fetchone()
            if result:
                return {
                    "is_owner": result[0],
                    "is_coowner": result[1]
                }
            return None

    def get_room_by_voice(self, voice_id: int) -> dict:
        """Get room data by voice channel ID"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT room_id, voice_id, role_id, guild_id, owner_id, name
                FROM private_rooms 
                WHERE voice_id = ?
            """, (voice_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "room_id": result[0],
                    "voice_id": result[1],
                    "role_id": result[2],
                    "guild_id": result[3],
                    "owner_id": result[4],
                    "name": result[5]
                }
            return None 

    def update_room_name(self, room_id: int, new_name: str):
        """Update room name"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE private_rooms SET name = ? WHERE room_id = ?",
                (new_name, room_id)
            )
            conn.commit() 

    def update_room_member(self, user_id: int, room_id: int, guild_id: int, is_coowner: bool):
        """Update co-owner status"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE room_members 
                   SET is_coowner = ?
                   WHERE user_id = ? AND room_id = ? AND guild_id = ?""",
                (is_coowner, user_id, room_id, guild_id)
            )
            conn.commit() 

    def add_marriage(self, user1_id: int, user2_id: int):
        """Register marriage between users"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Sort IDs to avoid duplicates
            min_id = min(user1_id, user2_id)
            max_id = max(user1_id, user2_id)
            cursor.execute(
                "INSERT OR REPLACE INTO marriages (user1_id, user2_id) VALUES (?, ?)",
                (min_id, max_id)
            )
            conn.commit()

    def remove_marriage(self, user1_id: int, user2_id: int):
        """Remove marriage"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            min_id = min(user1_id, user2_id)
            max_id = max(user1_id, user2_id)
            cursor.execute(
                "DELETE FROM marriages WHERE user1_id = ? AND user2_id = ?",
                (min_id, max_id)
            )
            conn.commit()

    def get_marriage(self, user_id: int) -> tuple:
        """Get user marriage information"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user1_id, user2_id, started_at 
                FROM marriages 
                WHERE user1_id = ? OR user2_id = ?
            """, (user_id, user_id))
            return cursor.fetchone() 

    def update_voice_activity(self, user_id: int, guild_id: int, is_join: bool):
        """Update time in voice channels"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if is_join:
                cursor.execute("""
                    INSERT OR REPLACE INTO voice_activity 
                    (user_id, guild_id, total_time, last_join)
                    VALUES (
                        ?, ?, 
                        COALESCE((SELECT total_time FROM voice_activity 
                                WHERE user_id = ? AND guild_id = ?), 0),
                        CURRENT_TIMESTAMP
                    )
                """, (user_id, guild_id, user_id, guild_id))
            else:
                cursor.execute("""
                    UPDATE voice_activity 
                    SET total_time = total_time + 
                        (strftime('%s', 'now') - strftime('%s', last_join)),
                        last_join = NULL
                    WHERE user_id = ? AND guild_id = ? AND last_join IS NOT NULL
                """, (user_id, guild_id))
            conn.commit()

    def increment_messages(self, user_id: int, guild_id: int):
        """Increment message counter"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO message_activity (user_id, guild_id, message_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET
                message_count = message_count + 1
            """, (user_id, guild_id))
            conn.commit()

    def get_user_stats(self, user_id: int, guild_id: int) -> dict:
        """Get user statistics"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Get voice time
            cursor.execute("""
                SELECT 
                    COALESCE(total_time, 0) as total_time,
                    last_join
                FROM voice_activity 
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            voice_data = cursor.fetchone() or (0, None)
            
            # If user is currently in voice, add current time
            current_time = voice_data[0]
            if voice_data[1]:
                current_time += int(
                    discord.utils.utcnow().timestamp() - 
                    discord.utils.parse_time(voice_data[1]).timestamp()
                )
            
            # Get message count
            cursor.execute("""
                SELECT COALESCE(message_count, 0)
                FROM message_activity 
                WHERE user_id = ? AND guild_id = ?
            """, (user_id, guild_id))
            messages = cursor.fetchone()
            
            return {
                "voice_time": current_time,
                "messages": messages[0] if messages else 0
            } 