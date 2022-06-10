from email.policy import default
from testy import db,bcrypt,login_manager
from flask_login import UserMixin
from datetime import date, datetime

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

    def GetRoleName(self, id):
        return self.session.query(UserRole).filter(UserRole.id == id).first().name
    
    def AddProfile(self, profile):
        self._engine.session.add(profile)

    def AddDevice(self, device):
        self._engine.session.add(device)

    def DeleteDevice(self, device):
        self.session.delete(device)
        self.session.commit()

    def add_sp_data(self,sp_data):
        self.session.add(sp_data)
        self.session.commit()

    def add_hr_data(self,hr_data):
        self.session.add(hr_data)


# tables
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False, unique = True)
    email = db.Column(db.String(50), nullable = False, unique = True)
    passwordHash = db.Column(db.String(60), nullable = False)
    active = db.Column(db.Boolean(), nullable = False, default = True)
    roleId = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete='CASCADE'), nullable=False)
    profileId = db.Column(db.Integer, db.ForeignKey("profiles.id", ondelete='CASCADE'), nullable=False)
    deviceId = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete='CASCADE'), nullable=True)

    @property
    def password(self):
        return self.passwordHash

    @password.setter
    def password(self, passwordText):
        self.passwordHash = bcrypt.generate_password_hash(passwordText, 10).decode('utf-8')

    def VerifyPassword(self, attemptedPassword):
        return bcrypt.check_password_hash(self.passwordHash, attemptedPassword)
    
    def GetRole(self):
        return DBConnection().GetRoleName(self.roleId)

class UserRole(db.Model):
    BASIC = "BASIC"
    ADMIN = "ADMIN"
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    user = db.relationship('User', backref=db.backref('roles'))

measurement_id = db.Table('measurement_id',
    db.Column('user_profile_id', db.Integer, db.ForeignKey("profiles.id")),
    db.Column('measurements_id', db.Integer, db.ForeignKey("measurements.id"))
)

class UserProfile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    date_of_birth = db.Column(db.Date)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(6))
    nationality = db.Column(db.String(30))
    avatarName = db.Column(db.String(30))
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    measurements = db.relationship('Measurement', secondary=measurement_id, lazy='dynamic', backref=db.backref('profiles'))
    user = db.relationship('User', backref=db.backref('profiles'))

    @property
    def dob(self):
        return self.date_of_birth

    @dob.setter
    def dob(self, born):
        self.date_of_birth = born
        today = date.today()
        self.age = today.year - born.year - ((today.month, today.day)<(born.month, born.day))

class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, primary_key=True)
    device_key = db.Column(db.String(30), unique = True)
    pin = db.Column(db.Integer)
    serial_number = db.Column(db.String(30))
    version = db.Column(db.String(30))
    config_state = db.Column(db.Integer, default = 0)
    user = db.relationship('User', backref=db.backref('devices'))

class Sp_data(db.Model):
    __tablename__ = "sp_data"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Float(precision=3))

class Hr_data(db.Model):
    __tablename__ = "hr_data"
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Float(precision=3))

sp_data_id = db.Table('sp_data_id',
    db.Column('sp_id', db.Integer, db.ForeignKey("sp_data.id")),
    db.Column('measurements_id', db.Integer, db.ForeignKey("measurements.id"))
)

hr_data_id = db.Table('hr_data_id',
    db.Column('hr_id', db.Integer, db.ForeignKey("hr_data.id")),
    db.Column('measurements_id', db.Integer, db.ForeignKey("measurements.id"))
)

class Measurement(db.Model):
    __tablename__ = "measurements"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    sp_data_avg = db.Column(db.Float(precision=3))
    hr_data_avg = db.Column(db.Float(precision=3))
    sp_data = db.relationship("Sp_data", secondary=sp_data_id, backref=db.backref('sp_data'))
    hr_data = db.relationship("Hr_data", secondary=hr_data_id, backref=db.backref('hr_data'))

    def __init__(self):
        self.date = datetime.today()
    def __init__(self,date):
        self.date = date



