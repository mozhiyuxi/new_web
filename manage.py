from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from flask import Flask

from info import create_app, db, models

# 创建app
app = create_app("Development")  # type: Flask

# 脚本管理flask以及添加迁移命令至脚本命令中
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()
