from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm
from . import auth
from app import db
from ..decorators import admin_required, permission_required


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Welcome %s" % user.username)
            return redirect(url_for('main.%s' % current_user.current_role().lower()))
        else:
            flash("Invalid username or password")
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Log out successfully.")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET','POST'])
@login_required
@admin_required
def sign_up():
    if not current_user.is_authenticated and not current_user.is_admin():
        flash("Please log in as administrator.")
        return redirect(url_for('auth.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        flash("Sign Up success.")
        return redirect('/admin/user')
    return render_template('auth/signup.html', form=form)