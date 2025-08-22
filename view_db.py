#!/usr/bin/env python3
"""Simple script to view database contents"""

import sqlite3
from datetime import datetime

DATABASE_FILE = "domain92_bot.db"

def view_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        print("=== DOMAIN92 BOT DATABASE ===\n")
        
        # View users table
        print("📋 USERS:")
        cursor.execute("SELECT user_id, username, total_links_created, first_seen, last_active FROM users ORDER BY last_active DESC")
        users = cursor.fetchall()
        
        if users:
            for user in users:
                print(f"  • {user[1]} (ID: {user[0]})")
                print(f"    Links: {user[2]} total | First seen: {user[3][:10]} | Last: {user[4][:10]}")
        else:
            print("  No users yet")
        
        print("\n🔗 ACTIVE LINKS:")
        cursor.execute("""
            SELECT ul.user_id, u.username, ul.domain_name, ul.server_name, ul.server_ip, ul.created_at
            FROM user_links ul
            JOIN users u ON ul.user_id = u.user_id
            WHERE ul.is_active = 1
            ORDER BY ul.created_at DESC
        """)
        
        links = cursor.fetchall()
        
        if links:
            for link in links:
                print(f"  • {link[2]} → {link[4]} ({link[3]})")
                print(f"    User: {link[1]} | Created: {link[5][:10]}")
        else:
            print("  No active links yet")
        
        print("\n📊 SUMMARY:")
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_links WHERE is_active = 1")
        active_links = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_links")
        total_links = cursor.fetchone()[0]
        
        print(f"  • Total users: {total_users}")
        print(f"  • Active links: {active_links}")
        print(f"  • Total links created: {total_links}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_database()