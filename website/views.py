from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import GPU, Price, Users, Subscriptions
from . import db
import json
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

views = Blueprint('views', __name__)

class SubscriptionForm(FlaskForm):
    desired_price = IntegerField('Desired Price', validators=[DataRequired()])
    submit = SubmitField('Subscribe')

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    gpus = GPU.query.all()  # Get all GPUs from the database
    prices = Price.query.all()  # Get all prices from the database
    subscriptions = Subscriptions.query.filter(Subscriptions.users.has(id=current_user.id)).all()
    
    for subscription in subscriptions:
        gpu = GPU.query.get(subscription.gpu_id)
        if gpu:
            latest_price = gpu.price[-1].price if gpu.price else 'N/A'
            subscription.gpu_model = gpu.model
            subscription.latest_price = latest_price

    subscription_form = SubscriptionForm()
    return render_template("home.html", gpus=gpus, prices=prices, subscriptions=subscriptions, user=current_user, subscription_form=subscription_form)




@views.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    gpu_id = request.form.get('gpu-id')
    desired_price = request.form.get('desired-price')

    print(gpu_id, desired_price)

    if gpu_id is None or desired_price is None:
        flash('Invalid data', 'error')
        return redirect(url_for('views.home'))
    
    existing_subscription = Subscriptions.query.filter_by(user_id=current_user.id, gpu_id=gpu_id).first()

    if existing_subscription:
        existing_subscription.desired_price = desired_price

    else: 
        gpu_instance = GPU.query.get(gpu_id)
        if gpu_instance is None:
            flash('GPU not found', 'error')
            return redirect(url_for('views.home'))

        subscription = Subscriptions(users=current_user, gpu_id=gpu_id, desired_price=desired_price)
        db.session.add(subscription)
    db.session.commit()

    flash('Subscription added', 'success')
    return redirect(url_for('views.home'))

@views.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    subscription_id = request.form.get('subscription-id')

    if subscription_id is None:
        flash('Invalid data', 'error')
        return redirect(url_for('views.home'))

    subscription = Subscriptions.query.get(subscription_id)
    if subscription and subscription.user_id == current_user.id:
        db.session.delete(subscription)
        db.session.commit()
        flash('Subscription canceled', 'success')
    else:
        flash('Invalid subscription', 'error')

    return redirect(url_for('views.home'))

