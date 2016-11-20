from . import db, admin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, AnonymousUserMixin
from flask_admin.contrib.sqla import ModelView
from flask import current_app

from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    read_chassis = 0x001
    read_rail = 0x002
    read_truck = 0x004
    read_labor = 0x008
    read_all = read_rail | read_truck | read_chassis | read_labor

    ordering_transportation = 0x010
    confirm_transportation = 0x020
    complete_transportation = 0x040
    start_transportation = 0x080
    confirm_receive = 0x100

    permission10 = 0x200
    permission11 = 0x400

    Administrator = 0x800
    ADMIN = 0xfff

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (0x000, True),
            'Chassis': (Permission.read_chassis, False),
            'Labor': (Permission.read_labor, False),
            'Rail': (Permission.read_rail, False),
            'Truck': (Permission.read_truck, False),
            'Cargo': (Permission.ordering_transportation |
                       Permission.confirm_receive |
                       Permission.read_all, False),
            'Terminal': (Permission.read_all |
                          Permission.complete_transportation, False),
            'Shipline': (Permission.confirm_transportation |
                         Permission.start_transportation |
                         Permission.read_all, False),
            'Admin': (Permission.ADMIN, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions, role.default = roles[r]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=Permission.ADMIN).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def allow(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.allow(Permission.Administrator)

    def current_role(self):
        role_name = self.role.__repr__()
        tail = len(role_name) - 2
        curt_role = role_name[7:tail]
        return curt_role

    @property
    def password(self):
        raise AttributeError('password is an unreadable attriable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def allow(self, permissions):
        return False

    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser

class MyModelView(ModelView):
    page_size = 20  # the number of entries to display on the list view
    can_view_details = True

    def is_accessible(self):
        flag = current_user.is_admin()
        if not flag:
            from flask import flash
            flash("Please log in as administrator.")
        return flag

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
