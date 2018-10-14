from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager

from info import create_app, db

# 创建app
app = create_app("Development")

# 脚本管理flask以及添加迁移命令至脚本命令中
manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()
