"""db_manage.py

Author: Caio Batista de Melo
Date Created: 2021-01-30
Date Modified: 2021-01-30
Description: Manages DB migrations.
"""

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from game import app, db

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()
