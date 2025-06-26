from flask import Blueprint, render_template, session, request, flash, redirect

profile = Blueprint('profile', __name__, url_prefix='/profile')

@profile.route('/', methods=['GET', 'POST'])
def index():
    user = {
        'username': session.get('username', 'demo'),
        'role': session.get('role', 'guest'),
        'email': session.get('email', 'demo@lab.com'),
        'full_name': session.get('full_name', 'Demo User')
    }
    if request.method == 'POST':
        # Here you would update user info in DB
        flash('Profile updated (demo only).', 'success')
        return redirect('/profile/')
    return render_template('modules/profile.html', user=user)
