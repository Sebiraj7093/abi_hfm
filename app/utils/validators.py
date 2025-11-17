"""SQL Query Validator"""
import re
from typing import Dict, Tuple

DANGEROUS_PATTERNS = [
    re.compile(r'\bDROP\b', re.IGNORECASE),
    re.compile(r'\bDELETE\b', re.IGNORECASE),
    re.compile(r'\bUPDATE\b', re.IGNORECASE),
    re.compile(r'\bINSERT\b', re.IGNORECASE),
]

class SQLValidator:
    @staticmethod
    def security_check(sql: str) -> Tuple[bool, str]:
        if not sql.strip().upper().startswith('SELECT'):
            return False, "SECURITY_VIOLATION: Only SELECT queries allowed."
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(sql):
                return False, "SECURITY_VIOLATION: Dangerous operation detected."
        return True, "OK"
    
    @staticmethod
    def validate_complete(sql: str, user_query: str) -> Dict:
        is_valid, msg = SQLValidator.security_check(sql)
        if not is_valid:
            return {"valid": False, "error": msg}
        return {"valid": True, "error": None}
