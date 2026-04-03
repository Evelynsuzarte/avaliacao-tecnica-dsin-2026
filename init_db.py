from flask_sqlalchemy import SQLAlchemy
from models.Admin import Admin

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

        if not Admin.query.filter_by(login='admin').first():
            admin_padrao = Admin(login='admin', senha='1234')
            db.session.add(admin_padrao)
            db.session.commit()