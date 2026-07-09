from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class ExportFormat(StrEnum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
