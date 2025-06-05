import sqlite3
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DBManager:
    """Manages SQLite database operations for migration tracking."""
    
    def __init__(self, db_path: str = "migration_data.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                source_system TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_data TEXT NOT NULL,
                error_message TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'failed',
                additional_info TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_id ON failed_migrations (source_id)')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS migration_map (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                squadcast_id TEXT,
                source_system TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )'''
            )
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_id ON migration_map (source_id)')

            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def record_failed_migration(
        self, 
        source_id: str, 
        source_system: str,
        entity_type: str, 
        entity_data: Dict[str, Any],
        error_message: str,
        additional_info: Dict[str, Any] = None
    ) -> int:
        """
        Record a failed migration attempt.
        
        Args:
            source_id: ID of the entity in the source system
            source_system: Name of the source system (e.g., 'opsgenie')
            entity_type: Type of entity being migrated (e.g., 'user', 'team')
            entity_data: JSON serializable dictionary of entity data
            error_message: Error message from the failed migration
            additional_info: Optional additional information about the migration
            
        Returns:
            The ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        exists = self.get_failed_migration(
            source_id=source_id,
            source_system=source_system,
            entity_type=entity_type
        )
        if exists:
            logger.debug(f"Migration record already exists for {entity_type} {source_id}. Updating status.")
            self.update_migration_status(
                record_id=exists['id'],
                status='failed',
                error_message=error_message
            )
            self.increment_retry_count(exists['id'])
            logger.debug(f"Incremented retry count for {entity_type} {source_id}.")
            return exists['id']
        
        cursor.execute(
            '''
            INSERT INTO failed_migrations 
            (source_id, source_system, entity_type, entity_data, error_message, additional_info) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', 
            (source_id, source_system, entity_type, json.dumps(entity_data), error_message, json.dumps(additional_info) if additional_info else None)
        )
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Recorded failed migration for {entity_type} {source_id}")
        return last_id
    
    def get_failed_migration(
        self,
        source_id: str,
        source_system: str,
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Get a specific failed migration record by source ID, source system, and entity type.
        
        Args:
            source_id: ID of the entity in the source system
            source_system: Name of the source system (e.g., 'opsgenie')
            entity_type: Type of entity being migrated (e.g., 'user', 'team')
            
        Returns:
            A dictionary containing the failed migration record, or an empty dictionary if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT * FROM failed_migrations 
            WHERE source_id = ? AND source_system = ? AND entity_type = ?
            ''',
            (source_id, source_system, entity_type)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            record = dict(row)
            record['entity_data'] = json.loads(record['entity_data'])
            if record['additional_info']:
                record['additional_info'] = json.loads(record['additional_info'])
            else:
                record['additional_info'] = {}
            return record
        return {}
    
    def get_failed_migrations(
        self, 
        entity_type: str = None, 
        status: str = "failed"
    ) -> List[Dict[str, Any]]:
        """
        Get all failed migrations with optional filtering.
        
        Args:
            entity_type: Filter by entity type (e.g., 'user', 'team')
            status: Filter by status (e.g., 'failed', 'retried', 'resolved')
            
        Returns:
            List of failed migration records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM failed_migrations WHERE status = ?"
        params = [status]
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            record = dict(row)
            record['entity_data'] = json.loads(record['entity_data'])
            if record['additional_info']:
                record['additional_info'] = json.loads(record['additional_info'])
            else:
                record['additional_info'] = {}
            results.append(record)
            
        conn.close()
        return results
    
    def update_migration_status(self, record_id: int, status: str, error_message: str = None) -> None:
        """
        Update the status of a failed migration record.
        
        Args:
            record_id: ID of the record to update
            status: New status ('failed', 'retried', 'resolved')
            error_message: Optional error message to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if error_message:
            cursor.execute(
                '''
                UPDATE failed_migrations 
                SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                ''',
                (status, error_message, record_id)
            )
        else:
            cursor.execute(
                '''
                UPDATE failed_migrations 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
                ''',
                (status, record_id)
            )
            
        conn.commit()
        conn.close()
        
        logger.debug(f"Updated migration record {record_id} status to {status}")
    
    def increment_retry_count(self, record_id: int) -> None:
        """
        Increment the retry count for a failed migration record.
        
        Args:
            record_id: ID of the record to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            UPDATE failed_migrations 
            SET retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            ''',
            (record_id,)
        )
            
        conn.commit()
        conn.close()

    def record_migration_map(
        self, 
        source_id: str, 
        squadcast_id: str, 
        source_system: str, 
        entity_type: str
    ) -> int:
        """
        Record a successful migration mapping.
        
        Args:
            source_id: ID of the entity in the source system
            squadcast_id: ID of the entity in Squadcast
            source_system: Name of the source system (e.g., 'opsgenie')
            entity_type: Type of entity being migrated (e.g., 'user', 'team')
            
        Returns:
            The ID of the inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO migration_map 
            (source_id, squadcast_id, source_system, entity_type) 
            VALUES (?, ?, ?, ?)
            ''', 
            (source_id, squadcast_id, source_system, entity_type)
        )
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.debug(f"Recorded migration map for {entity_type} {source_id} to Squadcast ID {squadcast_id}")
        return last_id

    def get_migration_map(self, source_id: str, source_system: str, entity_type: str) -> Dict[str, Any]:
        """
        Get the migration map for a specific source ID and entity type.

        Args:
            source_id: ID of the entity in the source system
            entity_type: Type of entity being migrated (e.g., 'user', 'team')
            
        Returns:
            A dictionary containing the migration details, or an empty dictionary if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            SELECT * FROM migration_map WHERE source_id = ? AND entity_type = ? AND source_system = ?
            ''',
            (source_id, entity_type, source_system)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return {}

    def get_all_migration_maps(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all migration maps for a specific entity type.

        Args:
            entity_type: Type of entity being migrated (e.g., 'user', 'team')

        Returns:
            A list of dictionaries containing all migration maps for the specified entity type
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM migration_map WHERE entity_type = ?', (entity_type,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            record = dict(row)
            results.append(record)
        
        conn.close()
        return results