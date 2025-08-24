import sqlite3
import datetime
from typing import List, Dict, Optional
import os

DATABASE_FILE = "domain92_bot.db"

class DatabaseManager:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                total_links_created INTEGER DEFAULT 0,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create user_links table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                domain_name TEXT,
                server_name TEXT,
                server_ip TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str):
        """Add a new user or update existing user info"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, last_active)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
    
    def get_user_active_links_count(self, user_id: int) -> int:
        """Get the count of active links for a user"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM user_links 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_user_links(self, user_id: int, active_only: bool = True) -> List[Dict]:
        """Get all links for a user"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        query = '''
            SELECT domain_name, server_name, server_ip, created_at, is_active
            FROM user_links 
            WHERE user_id = ?
        '''
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        
        links = []
        for row in rows:
            links.append({
                'domain_name': row[0],
                'server_name': row[1],
                'server_ip': row[2],
                'created_at': row[3],
                'is_active': bool(row[4])
            })
        
        conn.close()
        return links
    
    def add_user_links(self, user_id: int, username: str, links: List[str], server_name: str, server_ip: str):
        """Add multiple links for a user"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Update user info
        self.add_user(user_id, username)
        
        # Add links
        for domain in links:
            cursor.execute('''
                INSERT INTO user_links (user_id, domain_name, server_name, server_ip)
                VALUES (?, ?, ?, ?)
            ''', (user_id, domain.strip(), server_name, server_ip))
        
        # Update total links count
        cursor.execute('''
            UPDATE users 
            SET total_links_created = total_links_created + ?
            WHERE user_id = ?
        ''', (len(links), user_id))
        
        conn.commit()
        conn.close()
    
    def deactivate_user_link(self, user_id: int, domain_name: str):
        """Deactivate a specific link for a user"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_links 
            SET is_active = 0 
            WHERE user_id = ? AND domain_name = ?
        ''', (user_id, domain_name))
        
        conn.commit()
        conn.close()
    
    def can_user_create_links(self, user_id: int, requested_count: int = 1) -> tuple:
        """Check if user can create more links (3 link limit)"""
        current_count = self.get_user_active_links_count(user_id)
        max_links = 3
        
        can_create = (current_count + requested_count) <= max_links
        remaining = max_links - current_count
        
        return can_create, remaining, current_count
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('''
            SELECT username, total_links_created, first_seen, last_active
            FROM users WHERE user_id = ?
        ''', (user_id,))
        
        user_info = cursor.fetchone()
        if not user_info:
            return None
        
        # Get active links count
        active_count = self.get_user_active_links_count(user_id)
        
        conn.close()
        
        return {
            'username': user_info[0],
            'total_links_created': user_info[1],
            'active_links': active_count,
            'remaining_slots': 3 - active_count,
            'first_seen': user_info[2],
            'last_active': user_info[3]
        }
    
    def cleanup_old_links(self, days_old: int = 30):
        """Cleanup old inactive links (optional maintenance)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM user_links 
            WHERE is_active = 0 AND 
                  created_at < datetime('now', '-{} days')
        '''.format(days_old))
        
        conn.commit()
        conn.close()

# Global database instance
db = DatabaseManager()