from src.app.core.enums import UserRole, ExportFormat, AppEnv


def test_user_role_values():
    assert UserRole.USER == "user"
    assert UserRole.ADMIN == "admin"


def test_user_role_is_str():
    assert isinstance(UserRole.USER, str)
    assert isinstance(UserRole.ADMIN, str)


def test_user_role_members():
    members = set(UserRole)
    expected = {UserRole.USER, UserRole.ADMIN}
    assert members == expected


def test_user_role_convert_to_str():
    assert str(UserRole.USER) == "user"
    assert str(UserRole.ADMIN) == "admin"


def test_export_format_values():
    assert ExportFormat.CSV == "csv"
    assert ExportFormat.JSON == "json"
    assert ExportFormat.XLSX == "xlsx"


def test_export_format_is_str():
    assert isinstance(ExportFormat.CSV, str)
    assert isinstance(ExportFormat.JSON, str)
    assert isinstance(ExportFormat.XLSX, str)


def test_export_format_members():
    members = set(ExportFormat)
    expected = {ExportFormat.CSV, ExportFormat.JSON, ExportFormat.XLSX}
    assert members == expected


def test_export_format_convert_to_str():
    assert str(ExportFormat.CSV) == "csv"
    assert str(ExportFormat.JSON) == "json"
    assert str(ExportFormat.XLSX) == "xlsx"


def test_app_env_values():
    assert AppEnv.DEV == "dev"
    assert AppEnv.PROD == "prod"


def test_app_env_is_str():
    assert isinstance(AppEnv.DEV, str)
    assert isinstance(AppEnv.PROD, str)
