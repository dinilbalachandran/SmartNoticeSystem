from flask import Flask
from database.database import initialize_database

from routes.dashboard_routes import dashboard_bp
from routes.faculty_routes import faculty_bp
from routes.notice_routes import notice_bp
from routes.email_routes import email_bp
from routes.settings_routes import settings_bp
from routes.department_routes import department_bp

app = Flask(__name__)
initialize_database()

app.register_blueprint(dashboard_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(notice_bp)
app.register_blueprint(email_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(department_bp)

if __name__ == "__main__":
    app.run(debug=True)