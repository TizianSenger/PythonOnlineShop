"""
DSGVO-konformes Audit-Logging System
Loggt alle wichtigen Aktionen für Compliance und Sicherheit
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from enum import Enum


class AuditLogType(Enum):
    """Typen von Audit-Log-Einträgen"""
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    USER_DATA_EXPORT = "user_data_export"
    USER_DATA_DELETED = "user_data_deleted"
    USER_PROFILE_UPDATED = "user_profile_updated"
    ORDER_CREATED = "order_created"
    ORDER_STATUS_UPDATED = "order_status_updated"
    ORDER_DELETED = "order_deleted"
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    ADMIN_LOGIN = "admin_login"
    ADMIN_ACTION = "admin_action"
    DATA_ACCESS = "data_access"
    GDPR_CONSENT_GIVEN = "gdpr_consent_given"
    GDPR_CONSENT_REVOKED = "gdpr_consent_revoked"
    COOKIE_CONSENT = "cookie_consent"


class AuditLogger:
    """
    DSGVO-konformes Audit-Logging für Webshop
    Speichert alle wichtigen Aktionen für Compliance-Audits
    """
    
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = str(Path(__file__).parent.parent.parent / "data" / "logs")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit_log.csv"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Erstelle Audit-Log-Datei mit Headers, falls nicht vorhanden"""
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp',
                    'event_type',
                    'user_id',
                    'user_email',
                    'action',
                    'resource_type',
                    'resource_id',
                    'details',
                    'ip_address',
                    'status'
                ])
                writer.writeheader()
    
    def log(self, event_type: AuditLogType, user_id: str = None, user_email: str = None,
            action: str = None, resource_type: str = None, resource_id: str = None,
            details: dict = None, ip_address: str = None, status: str = "success"):
        """
        Logge einen Audit-Event
        
        Args:
            event_type: Typ des Events (AuditLogType Enum)
            user_id: ID des Benutzers
            user_email: E-Mail des Benutzers
            action: Beschreibung der Aktion
            resource_type: Typ der Ressource (z.B. "product", "order", "user")
            resource_id: ID der Ressource
            details: Zusätzliche Details als Dict
            ip_address: IP-Adresse des Clients
            status: Status des Events ("success", "failure", "pending")
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type.value,
                'user_id': user_id or '',
                'user_email': user_email or '',
                'action': action or '',
                'resource_type': resource_type or '',
                'resource_id': resource_id or '',
                'details': json.dumps(details, ensure_ascii=False) if details else '',
                'ip_address': ip_address or '',
                'status': status
            }
            
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'event_type', 'user_id', 'user_email', 'action',
                    'resource_type', 'resource_id', 'details', 'ip_address', 'status'
                ])
                writer.writerow(log_entry)
        except Exception as e:
            print(f"Fehler beim Schreiben des Audit-Logs: {e}")
    
    def get_user_logs(self, user_id: str) -> list:
        """Hole alle Log-Einträge für einen bestimmten Benutzer (für Datenexport)"""
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('user_id') == user_id:
                        logs.append(row)
        except Exception as e:
            print(f"Fehler beim Lesen der Logs: {e}")
        
        return logs
    
    def delete_user_logs(self, user_id: str) -> bool:
        """Lösche alle Log-Einträge für einen Benutzer (Right to be forgotten)"""
        try:
            logs = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('user_id') != user_id:
                        logs.append(row)
            
            # Schreibe alle Logs außer denen des Benutzers zurück
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'event_type', 'user_id', 'user_email', 'action',
                    'resource_type', 'resource_id', 'details', 'ip_address', 'status'
                ])
                writer.writeheader()
                writer.writerows(logs)
            
            return True
        except Exception as e:
            print(f"Fehler beim Löschen der Logs: {e}")
            return False
    
    def get_all_logs(self, limit: int = 1000) -> list:
        """Hole alle Audit-Logs (für Admin-Dashboard)"""
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    logs.append(row)
        except Exception as e:
            print(f"Fehler beim Lesen der Logs: {e}")
        
        return logs


# Global-Instanz
audit_logger = AuditLogger()
