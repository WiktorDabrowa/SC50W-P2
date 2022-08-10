from dataclasses import fields
from django.forms import ModelForm


from .models import Listing, Bid, Comment

class listingForm(ModelForm):
  class Meta:
    model = Listing
    exclude = ['seller','is_open','winner']
    labels={'photo':('Photo URL:')}

class bidForm(ModelForm):
  class Meta:
    model = Bid
    fields = ['price']
    labels = {'price':('Place your bid:')}

class CommentForm(ModelForm):
  class Meta:
    model = Comment
    fields = ['body']
    labels = {'body':('')}