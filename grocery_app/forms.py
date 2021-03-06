from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, URL
from grocery_app.models import ItemCategory, GroceryStore

class GroceryStoreForm(FlaskForm):
    """Form for adding/updating a GroceryStore."""

    # TODO: Add the following fields to the form class:
    # - title - StringField
    # - address - StringField
    # - submit button
    title = StringField('Store\'s Title', validators=[DataRequired(), Length(max=80)])
    address = StringField('Store\'s Address', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')

class GroceryItemForm(FlaskForm):
    """Form for adding/updating a GroceryItem."""

    # TODO: Add the following fields to the form class:
    # - name - StringField
    # - price - FloatField
    # - category - SelectField (specify the 'choices' param)
    # - photo_url - StringField (use a URL validator)
    # - store - QuerySelectField (specify the `query_factory` param)
    # - submit button
    name = StringField('Item\'s Name', validators=[DataRequired(), Length(max=80)])
    price = FloatField('Item\'s Price', validators=[DataRequired()]) # VERIFICA SI PUEDES UTILIZAR SOLO UNO!
    category = SelectField('Item\'s Category', choices=ItemCategory.choices())
    photo_url = StringField('Item\'s Photo URL', validators=[URL()])
    store = QuerySelectField('Stores', query_factory=lambda: GroceryStore.query, get_label='title')
    submit = SubmitField('Submit')
