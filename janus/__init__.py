import os
if os.getenv("USE_PYMYSQL", "0") == "1":
    import pymysql
    pymysql.install_as_MySQLdb()