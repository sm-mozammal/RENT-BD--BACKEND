import pymysql

# Install PyMySQL as MySQLdb driver BEFORE importing Django's mysql backend
pymysql.install_as_MySQLdb()

from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# Enable full compatibility with XAMPP MariaDB (10.4.x+)
setattr(DatabaseWrapper, 'check_database_version_supported', lambda self: None)
setattr(DatabaseFeatures, 'can_return_columns_from_insert', property(lambda self: False))
setattr(DatabaseFeatures, 'has_native_uuid_field', property(lambda self: False))
