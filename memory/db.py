import sqlite3
import os
import json
import datetime
from pathlib import Path
from contextlib import contextmanager

class DatabaseMemory:
    """SQLite database for conversation history, user preferences, tasks, and system notes."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_dir = Path(os.path.expanduser("~")) / ".jarvis_ai"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "jarvis_memory.db"
        self.db_path = str(db_path)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table 1: Conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            # Table 2: Long-Term User Memory (Preferences, Facts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key_name TEXT UNIQUE NOT NULL,
                    value_content TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table 3: Productivity Tasks / Reminders
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    due_date TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table 4: Notes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table 5: RAG Knowledge Chunks (Phase 5)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER DEFAULT 0,
                    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

        # Seed default user profile if table is empty
        self.seed_default_user_facts()

    def seed_default_user_facts(self):
        """Seeds Ashwin's complete personal profile into long-term memory if empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM long_term_memory")
            count = cursor.fetchone()[0]
            if count == 0:
                user_facts = [
                    ('personal', 'user_name', 'Ashwin'),
                    ('personal', 'preferred_name', 'Ash'),
                    ('personal', 'profession', 'Computer Science Engineering Student'),
                    ('personal', 'university', 'VTU'),
                    ('personal', 'graduation_year', '2027'),
                    ('personal', 'country', 'India'),
                    ('personal', 'timezone', 'Asia/Kolkata'),
                    
                    ('preferences', 'theme', 'Dark Glass'),
                    ('preferences', 'ui_style', 'Minimal Modern'),
                    ('preferences', 'assistant_name', 'Jarvis'),
                    ('preferences', 'response_style', 'Concise'),
                    ('preferences', 'language', 'English'),
                    ('preferences', 'voice', 'Male'),
                    ('preferences', 'wake_word', 'Hey Jarvis'),
                    
                    ('development', 'favorite_language', 'Python'),
                    ('development', 'frontend', 'React'),
                    ('development', 'backend', 'FastAPI'),
                    ('development', 'database', 'PostgreSQL'),
                    ('development', 'editor', 'VS Code'),
                    ('development', 'terminal', 'PowerShell'),
                    ('development', 'git_username', 'ashwin2k23'),
                    
                    ('projects', 'project_jarvis', 'Desktop AI Assistant | Stack: Python, PySide6, FastAPI, SQLite | Status: Active | Next: Personal Memory Integration'),
                    ('projects', 'project_warehouse', 'FEFO Inventory System | Status: Active'),
                    ('projects', 'project_portfolio', 'Personal Portfolio | Status: Active'),
                    ('projects', 'project_devverse', 'Developer Platform | Status: Active'),
                    
                    ('goals', 'goal_internship', 'Get Software Engineer Internship | Deadline: December 2026 | Priority: High'),
                    
                    ('education', 'university', 'VTU'),
                    ('education', 'degree', 'B.E Computer Science'),
                    ('education', 'semester', '7'),
                    ('education', 'cgpa', '7.9'),
                    
                    ('devices', 'laptop', 'ASUS Vivobook 15 | Specs: 16GB RAM, i5-13420H CPU, Intel UHD GPU, Windows 11 OS'),
                    ('devices', 'phone', 'Nothing Phone 4a'),
                    
                    ('skills', 'skill_python', 'Intermediate'),
                    ('skills', 'skill_react', 'Advanced'),
                    ('skills', 'skill_aws', 'Learning'),
                    ('skills', 'skill_docker', 'Intermediate'),
                    ('skills', 'skill_terraform', 'Learning'),
                    
                    ('accounts', 'github_username', 'ashwin2k23'),
                    ('accounts', 'linkedin', 'Ashwin'),
                    ('accounts', 'portfolio', 'Ashwin Portfolio'),
                    
                    ('notes', 'note_indentation', 'Prefers tabs over spaces'),
                    ('notes', 'note_ui_preference', 'Hates neon UI, prefers quiet minimal modern UI'),
                    ('notes', 'note_git_flow', 'Uses GitHub Flow'),
                    ('notes', 'note_ui_design_rule', 'Always generate modern, sleek, premium UI'),
                    
                    ('ai_preferences', 'ai_pref_explain_first', 'Always explain before coding'),
                    ('ai_preferences', 'ai_pref_code_language', 'Prefer Python examples'),
                    ('ai_preferences', 'ai_pref_docker_rule', 'Don\'t use Docker unless asked'),
                    ('ai_preferences', 'ai_pref_brevity', 'Use concise answers'),
                    ('ai_preferences', 'ai_pref_shortcuts', 'Prefer keyboard shortcuts'),
                    
                    ('career', 'target_role', 'Software Engineer'),
                    ('career', 'preferred_company', 'Microsoft'),
                    ('career', 'interested_in', 'Backend Development'),
                    ('career', 'remote_work', 'Yes'),
                ]
                cursor.executemany("""
                    INSERT INTO long_term_memory (category, key_name, value_content, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key_name) DO UPDATE SET
                        value_content = excluded.value_content,
                        category = excluded.category,
                        updated_at = CURRENT_TIMESTAMP
                """, user_facts)
                conn.commit()

    def add_message(self, sender: str, content: str, session_id: str = "default", metadata: dict = None):
        meta_str = json.dumps(metadata) if metadata else "{}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (session_id, sender, content, metadata) VALUES (?, ?, ?, ?)",
                (session_id, sender, content, meta_str)
            )
            conn.commit()

    def get_recent_messages(self, limit: int = 50, session_id: str = "default") -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender, content, timestamp, metadata FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = []
            for sender, content, timestamp, meta_str in reversed(rows):
                messages.append({
                    "sender": sender,
                    "content": content,
                    "timestamp": timestamp,
                    "metadata": json.loads(meta_str) if meta_str else {}
                })
            return messages

    def get_all_chat_sessions(self) -> list:
        """Returns list of all chat sessions with their latest message snippet and timestamp."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, content, timestamp
                FROM conversations
                WHERE id IN (
                    SELECT MAX(id) FROM conversations GROUP BY session_id
                )
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()
            sessions = []
            for session_id, last_msg, timestamp in rows:
                title = last_msg[:35] + "..." if len(last_msg) > 35 else last_msg
                sessions.append({
                    "session_id": session_id,
                    "title": title.strip() if title.strip() else f"Chat {session_id}",
                    "timestamp": timestamp
                })
            return sessions

    def delete_chat_session(self, session_id: str):
        """Deletes all messages for a specific session_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()


    def save_memory_fact(self, category: str, key_name: str, value_content: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO long_term_memory (category, key_name, value_content, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key_name) DO UPDATE SET
                    value_content = excluded.value_content,
                    category = excluded.category,
                    updated_at = CURRENT_TIMESTAMP
            """, (category, key_name, value_content))
            conn.commit()

    def get_all_memory_facts(self) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, key_name, value_content, updated_at FROM long_term_memory ORDER BY category")
            rows = cursor.fetchall()
            return [{"category": r[0], "key": r[1], "value": r[2], "updated_at": r[3]} for r in rows]

    def search_memory_facts(self, query: str) -> list:
        """Searches long-term memory facts using keyword matching across key and value."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            like_query = f"%{query.lower()}%"
            cursor.execute(
                """SELECT category, key_name, value_content, updated_at
                   FROM long_term_memory
                   WHERE LOWER(key_name) LIKE ? OR LOWER(value_content) LIKE ?
                   ORDER BY updated_at DESC LIMIT 10""",
                (like_query, like_query)
            )
            rows = cursor.fetchall()
            return [{"category": r[0], "key": r[1], "value": r[2], "updated_at": r[3]} for r in rows]

    def delete_memory_fact(self, key_name: str):
        """Deletes a specific memory fact by its key name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM long_term_memory WHERE key_name = ?", (key_name,))
            conn.commit()

    def add_rag_chunk(self, filepath: str, chunk_text: str, chunk_index: int = 0):
        """Stores a text chunk from a local file for RAG retrieval."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rag_chunks (filepath, chunk_text, chunk_index) VALUES (?, ?, ?)",
                (filepath, chunk_text, chunk_index)
            )
            conn.commit()

    def get_rag_chunks_by_file(self, filepath: str) -> list:
        """Returns all stored chunks for a given file path."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT chunk_text, chunk_index FROM rag_chunks WHERE filepath = ? ORDER BY chunk_index",
                (filepath,)
            )
            return [{"text": r[0], "index": r[1]} for r in cursor.fetchall()]

    def get_all_rag_chunks(self) -> list:
        """Returns all indexed RAG chunks for search."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, chunk_text, chunk_index FROM rag_chunks")
            return [{"filepath": r[0], "text": r[1], "index": r[2]} for r in cursor.fetchall()]

    def clear_rag_chunks_for_file(self, filepath: str):
        """Removes all previously indexed chunks for a file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rag_chunks WHERE filepath = ?", (filepath,))
            conn.commit()

    def clear_all_rag_chunks(self):
        """Clears all indexed files and chunks from the knowledge base."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rag_chunks")
            conn.commit()

    def get_indexed_files(self) -> list:
        """Returns a distinct list of all indexed file paths."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT filepath, MAX(indexed_at) as last_indexed FROM rag_chunks GROUP BY filepath")
            return [{"filepath": r[0], "indexed_at": r[1]} for r in cursor.fetchall()]

    def get_indexed_files_with_counts(self) -> list:
        """Returns distinct indexed files with chunk counts."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath, COUNT(*) as chunk_count, MAX(indexed_at) as last_indexed FROM rag_chunks GROUP BY filepath ORDER BY last_indexed DESC")
            return [{"filepath": r[0], "chunks": r[1], "indexed_at": r[2]} for r in cursor.fetchall()]


    def add_task(self, title: str, due_date: str = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (title, due_date) VALUES (?, ?)", (title, due_date))
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, status: str = None) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT id, title, status, due_date, created_at FROM tasks WHERE status = ?", (status,))
            else:
                cursor.execute("SELECT id, title, status, due_date, created_at FROM tasks ORDER BY id DESC")
            rows = cursor.fetchall()
            return [{"id": r[0], "title": r[1], "status": r[2], "due_date": r[3], "created_at": r[4]} for r in rows]

    def update_task_status(self, task_id: int, status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()

    def add_note(self, title: str, content: str, tags: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)", (title, content, tags))
            conn.commit()
            return cursor.lastrowid

    def get_notes(self) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content, tags, created_at FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [{"id": r[0], "title": r[1], "content": r[2], "tags": r[3], "created_at": r[4]} for r in rows]

    def clear_history(self, session_id: str = "default"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()
