# admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User, Portfolio
from . import db

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main.dashboard'))

    total_users = User.query.count()
    total_portfolios = Portfolio.query.count()
    total_resumes = Portfolio.query.filter(Portfolio.resume_data != None).count()
    users = User.query.order_by(User.created_at.desc()).all()
    portfolios = Portfolio.query.order_by(Portfolio.created_at.desc()).all()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_portfolios=total_portfolios,
                           total_resumes=total_resumes,
                           users=users,
                           portfolios=portfolios)


@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete an admin user.", "warning")
        return redirect(url_for('admin.admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.full_name}' deleted successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/portfolio/delete/<int:portfolio_id>', methods=['POST'])
@login_required
def delete_portfolio(portfolio_id):
    if not current_user.is_admin:
        return redirect(url_for('main.dashboard'))

    portfolio = Portfolio.query.get_or_404(portfolio_id)
    db.session.delete(portfolio)
    db.session.commit()
    flash(f"Portfolio '{portfolio.title}' deleted successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))
