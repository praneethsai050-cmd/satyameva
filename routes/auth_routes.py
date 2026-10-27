"""
Authentication: sign in, sign out, and role-based landing.

Sessions are Flask-Login sessions with a hard 5-minute idle timeout enforced
in `app.before_request`, matching the zero-trust posture in the project brief.
"""
import time

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, session, url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db, utcnow
from models.user import User
from security import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.home_endpoint()))

    if request.method == 'POST':
        identifier = (request.form.get('identifier') or '').strip()
        password = request.form.get('password') or ''

        user = User.query.filter(
            (User.username == identifier) | 
            (User.email == identifier.lower()) |
            ((User.username == 'praneeth') if identifier.lower() == 'praneethsai050' else False)
        ).first()

        if not user:
            from models.student import Student
            stu_match = Student.query.filter_by(roll_number=identifier).first()
            if stu_match and stu_match.user:
                user = stu_match.user

        if user and verify_password(password, user.password_salt,
                                    user.password_hash, user.password_iterations):
            # Re-hash at the current cost factor for accounts created earlier.
            target_iterations = current_app.config['PASSWORD_ITERATIONS']
            if user.password_iterations < target_iterations:
                salt, digest, iterations = hash_password(password, target_iterations)
                user.password_salt, user.password_hash = salt, digest
                user.password_iterations = iterations

            user.last_login_at = utcnow()
            db.session.commit()

            login_user(user)
            # Must use the same clock as the idle-timeout check in
            # app.enforce_idle_timeout — time.time(), not utcnow().timestamp().
            session['last_active'] = time.time()
            flash(f'Welcome back, {user.display_name}.', 'success')

            nxt = request.args.get('next')
            # Only honour same-site relative redirects — an absolute URL here
            # would be an open redirect.
            if nxt and nxt.startswith('/') and not nxt.startswith('//'):
                return redirect(nxt)
            return redirect(url_for(user.home_endpoint()))

        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(current_user.home_endpoint()))

    if request.method == 'POST':
        role = request.form.get('role')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Additional fields
        organization = request.form.get('organization') # For Issuer & Verifier
        full_name = request.form.get('full_name')       # For Student
        roll_number = request.form.get('roll_number')   # For Student
        program = request.form.get('program')           # For Student

        from models.student import Student
        from models.institution import Institution

        target_iterations = current_app.config.get('PASSWORD_ITERATIONS', 100000)
        salt, digest, iterations = hash_password(password, target_iterations)

        campus_select = (request.form.get('campus_select') or '').strip().upper()

        # Resolve campus institution if selected
        selected_inst = None
        if campus_select in ('JIIT', 'JUIT', 'JUET'):
            selected_inst = Institution.query.filter_by(short_code=campus_select).first()

        effective_org = organization
        if selected_inst:
            effective_org = selected_inst.name

        # If registering as student, check if an auto-provisioned student record already exists
        if role == 'student':
            clean_roll = (roll_number or '').strip()
            clean_email = (email or '').strip().lower()

            pre_student = None
            if clean_roll:
                pre_student = Student.query.filter_by(roll_number=clean_roll).first()
            if not pre_student and clean_email:
                pre_user = User.query.filter_by(email=clean_email).first()
                if pre_user and pre_user.role == 'student':
                    pre_student = Student.query.filter_by(user_id=pre_user.id).first()

            if pre_student and pre_student.user:
                # Check if this student account was an auto-provisioned placeholder waiting to be claimed
                u = pre_student.user
                is_placeholder = (
                    u.username.startswith('student.') or
                    u.email.endswith('.edu') or
                    u.email == clean_email
                )
                if is_placeholder:
                    # Update credentials with student's chosen username, email, and password
                    u.username = username
                    u.email = clean_email
                    u.password_salt = salt
                    u.password_hash = digest
                    u.password_iterations = iterations
                    if selected_inst:
                        u.institution_id = selected_inst.id
                        u.organization = selected_inst.name
                        pre_student.institution = selected_inst.name
                    if full_name:
                        pre_student.full_name = full_name
                    if clean_roll:
                        pre_student.roll_number = clean_roll
                    if program:
                        pre_student.program = program

                    db.session.commit()
                    flash('Account registered successfully! All pre-issued credentials have been linked to your dashboard.', 'success')
                    return redirect(url_for('auth.login'))

            if pre_student:
                flash('This roll number is already claimed. Please sign in.', 'danger')
                return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            user = User(
                username=username,
                email=email,
                role=role,
                organization=effective_org if role in ['issuer', 'verifier', 'student'] else None,
                institution_id=selected_inst.id if selected_inst else None,
                password_salt=salt,
                password_hash=digest,
                password_iterations=iterations
            )
            db.session.add(user)
            db.session.flush()  # Gets user.id without committing

            if role == 'student':
                student = Student(
                    user_id=user.id,
                    full_name=full_name,
                    roll_number=roll_number,
                    program=program,
                    institution=selected_inst.name if selected_inst else (organization or 'Jaypee Institute of Information Technology')
                )
                db.session.add(student)

            elif role == 'issuer' and not selected_inst and organization:
                # Custom institution registration
                short_code = ''.join(
                    w[0].upper() for w in organization.split() if w
                )[:10] or organization[:6].upper()
                base = short_code
                counter = 1
                while Institution.query.filter_by(short_code=short_code).first():
                    short_code = f'{base}{counter}'
                    counter += 1
                inst = Institution.query.filter(
                    Institution.name.ilike(organization)
                ).first()
                if not inst:
                    inst = Institution(
                        name=organization,
                        short_code=short_code,
                        is_approved=False,
                    )
                    db.session.add(inst)
                    db.session.flush()
                user.institution_id = inst.id

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please check your details and try again.', 'danger')
            return redirect(url_for('auth.register'))

        login_user(user)
        session['last_active'] = time.time()
        flash('Registration successful! Welcome to Satyameva.', 'success')
        return redirect(url_for(user.home_endpoint()))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    from models.student import Student
    clean_token = (token or '').strip()
    student = Student.query.filter_by(email_verify_token=clean_token).first()
    if not student:
        flash('Invalid or expired email verification link.', 'danger')
        return redirect(url_for('auth.login'))

    student.email_verified = True
    student.email_verify_token = None
    db.session.commit()
    target_mail = student.user.email if student.user else 'your account'
    flash(f'Student email ({target_mail}) verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))
