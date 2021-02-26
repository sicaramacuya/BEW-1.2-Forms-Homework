from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from grocery_app.models import GroceryStore, GroceryItem, User
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, SignUpForm, LoginForm
from grocery_app import bcrypt

# Import app and db from events_app package so that we can run app
from grocery_app import app, db

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    print(all_stores)
    return render_template('home.html', all_stores=all_stores)

@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = GroceryStoreForm()
    current_user_id = current_user.get_id()

    if form.validate_on_submit():
        new_store = GroceryStore(
            title=form.title.data,
            address=form.address.data,
            created_by_id=current_user.get_id()
        )
        db.session.add(new_store)
        db.session.commit()

        flash('New store was created succesfully.')
        return redirect(url_for('main.store_detail', store_id=new_store.id))

    return render_template('new_store.html', form=form)

@main.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    form = GroceryItemForm()

    if form.validate_on_submit():
        new_item = GroceryItem(
            name = form.name.data,
            price = form.price.data,
            category = form.category.data,
            photo_url = form.photo_url.data,
            store = form.store.data,
            created_by_id=current_user.get_id()
        )
        db.session.add(new_item)
        db.session.commit()

        flash('New item was created succesfully.')
        return redirect(url_for('main.item_detail', item_id=new_item.id))

    return render_template('new_item.html', form=form)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
@login_required
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    form = GroceryStoreForm(obj=store)
    store_created_by = User.query.filter_by(id=store.created_by_id).one()

    if form.validate_on_submit():
        store.title = form.title.data
        store.address = form.address.data

        db.session.add(store)
        db.session.commit()

        flash('Store was edited succesfully.')
        return redirect(url_for('main.store_detail', store_id=store.id))

    store = GroceryStore.query.get(store_id)
    return render_template('store_detail.html', store=store, form=form, store_created_by=store_created_by)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
@login_required
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    form = GroceryItemForm(obj=item)
    user_object = User.query.filter_by(id=item.created_by_id).one()
    is_item_in_shopping_list = bool

    if item in user_object.shopping_list_items:
        is_item_in_shopping_list = True
    else:
        is_item_in_shopping_list = False

    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.category = form.category.data
        item.photo_url = form.photo_url.data
        item.store = form.store.data

        db.session.add(item)
        db.session.commit()

        flash('Item was edited succesfully.')
        return redirect(url_for('main.item_detail', item_id=item.id))

    item = GroceryItem.query.get(item_id)
    return render_template('item_detail.html', item=item, form=form, item_created_by=user_object, is_item_in_shopping_list=is_item_in_shopping_list)

@main.route('/shopping_list')
@login_required
def shopping_list():
    current_user_id = current_user.get_id()
    user_object = User.query.filter_by(id=current_user_id).one()
    user_shopping_list_items = user_object.shopping_list_items

    return render_template('shopping_list.html', user_shopping_list_items=user_shopping_list_items)

@main.route('/add_to_shopping_list/<item_id>', methods=['POST'])
@login_required
def add_to_shopping_list(item_id):
    item = GroceryItem.query.get(item_id)

    current_user_id = current_user.get_id()
    user_object = User.query.filter_by(id=current_user_id).one()

    if not item in user_object.shopping_list_items:
        user_object.shopping_list_items.append(item)

        db.session.add(user_object)
        db.session.commit()

    return redirect(url_for('main.item_detail', item_id=item.id))

@main.route('/remove_from_shopping_list/<item_id>', methods=['POST'])
@login_required
def remove_from_shopping_list(item_id):
    item = GroceryItem.query.get(item_id)

    current_user_id = current_user.get_id()
    user_object = User.query.filter_by(id=current_user_id).one()

    if item in user_object.shopping_list_items:
        user_object.shopping_list_items.remove(item)

        db.session.add(user_object)
        db.session.commit()

    return redirect(url_for('main.item_detail', item_id=item.id))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    print('in signup')
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created.')
        print('created')
        return redirect(url_for('auth.login'))
    print(form.errors)
    
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.homepage'))
    
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))