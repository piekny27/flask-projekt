from testy import db,bcrypt,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userId):
    return User.query.get(int(userId))

def Singleton(class_):
    instances = {}
    def GetInstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return GetInstance

@Singleton
class DBConnection():
    def __init__(self):
        self._engine = db
        Session = self._engine.session
        self.session = Session
    def Flush(self):
        self.session.commit()

    def AddUser(self, user):
        self._engine.session.add(user)


# tables
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False, unique = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    passwordHash = db.Column(db.String(60), nullable = False)
    active = db.Column(db.Boolean(), nullable = False, default = True)
    roleId = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    @property
    def password(self):
        return self.passwordHash

    @password.setter
    def password(self, passwordText):
        self.passwordHash = bcrypt.generate_password_hash(passwordText, 10).decode('utf-8')

    def VerifyPassword(self, attemptedPassword):
        return bcrypt.check_password_hash(self.passwordHash, attemptedPassword)
    
    def GetRole(self):
        return DBConnection().getRoleName(self.roleId)

class UserRole(db.Model):
    BASIC = "BASIC"
    ADMIN = "ADMIN"
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    user = db.relationship('User', backref=db.backref('users'))