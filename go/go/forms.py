# Django Imports
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils import timezone

# App Imports
from go.models import URL, RegisteredUser

# Other Imports
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div, Field
from crispy_forms.bootstrap import StrictButton, PrependedText, Accordion, AccordionGroup
from bootstrap3_datetime.widgets import DateTimePicker
from datetime import date, datetime, timedelta

"""
    The form that is used in URL creation.
"""
class URLForm(forms.ModelForm):

    # Prevent redirect loop links
    def clean_target(self):
        # get the entered target link
        target = self.cleaned_data.get('target')
        # if the host (go.gmu.edu) is in the entered target link
        if self.host in target:
            raise ValidationError("You can't make a Go link to Go silly!")
        else:
            return target

    # Custom target URL field
    target = forms.URLField(
        required=True,
        label='Long URL (Required)',
        max_length=1000,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://yoursite.com/'
        })
    )

    # Check to make sure the short url has not been used
    def unique_short(value):
        try:
            # if we're able to get a URL with the same short url
            URL.objects.get(short__iexact=value)
        except URL.DoesNotExist:
            return
        # then raise a ValidationError
        raise ValidationError('Short url already exists.')

    # Custom short-url field with validators.
    short = forms.SlugField(
        required = False,
        label = 'Short URL (Optional)',
        widget = forms.TextInput(),
        validators = [unique_short],
        max_length = 20,
        min_length = 3,
    )

    # define some string date standards
    DAY = '1 Day'
    WEEK = '1 Week'
    MONTH = '1 Month'
    CUSTOM = 'Custom Date'
    NEVER = 'Never'

    # define a tuple of string date standards to be used as our date choices
    EXPIRATION_CHOICES = (
        (DAY, DAY),
        (WEEK, WEEK),
        (MONTH, MONTH),
        (NEVER, NEVER),
        (CUSTOM, CUSTOM),
    )

    # Add preset expiration choices.
    expires = forms.ChoiceField(
        required = True,
        label = 'Expiration (Required)',
        choices = EXPIRATION_CHOICES,
        initial = NEVER,
        widget = forms.RadioSelect(),
    )

    # Check if the selected date is a valid date
    def valid_date(value):
        # a valid date is one that is greater than today
        if value > timezone.now():
            return
        # raise a ValidationError if the date is invalid
        else:
            raise ValidationError('Date must be after today.')


    # Add a custom expiration choice.
    expires_custom = forms.DateTimeField(
        required = False,
        label = 'Custom Date',
        input_formats = ['%m-%d-%Y'],
        validators = [valid_date],
        initial = lambda: datetime.now() + timedelta(days=1),
        widget = DateTimePicker(
            options={
                "format": "MM-DD-YYYY",
                "pickTime": False,
            },
            icon_attrs={
                "class": "fa fa-calendar",
            },
        )
    )

    # on initialization of the form, crispy forms renders this layout
    def __init__(self, *args, **kwargs):
        # Grab that host info
        self.host = kwargs.pop('host', None)
        super(URLForm, self).__init__(*args, **kwargs)
        # Define the basics for crispy-forms
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        # Some xtra vars for form css purposes
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-1'
        self.helper.field_class = 'col-md-6'

        # The main "layout" defined
        self.helper.layout = Layout(
            Fieldset('',
            #######################
                Accordion(
                    # Step 1: Long URL
                    AccordionGroup('Step 1: Long URL',
                        Div(
                            HTML("""
                                <h4>Paste the URL you would like to shorten:</h4>
                                <br />"""),
                            'target',
                            style="background: rgb(#F6F6F6);"),
                        active=True,
                        template='crispy/accordian-group.html'),

                    # Step 2: Short URL
                    AccordionGroup('Step 2: Short URL',
                        Div(
                            HTML("""
                                <h4>Create a custom Go address:</h4>
                                <br />"""),
                            PrependedText(
                            'short', 'https://go.gmu.edu/', template='crispy/customPrepended.html'),
                            style="background: rgb(#F6F6F6);"),
                        active=True,
                        template='crispy/accordian-group.html',),

                    # Step 3: Expiration
                    AccordionGroup('Step 3: URL Expiration',
                        Div(
                            HTML("""
                                <h4>Set when you would like your Go address to expire:</h4>
                                <br />"""),
                            'expires',
                            Field('expires_custom', template="crispy/customDateField.html"),
                            style="background: rgb(#F6F6F6);"),
                        active=True,
                        template='crispy/accordian-group.html'),

                    # FIN
                    template='crispy/accordian.html'),
            #######################
            HTML("""
                <br />"""),
            StrictButton('Shorten', css_class="btn btn-primary btn-md col-md-4", type='submit')))

    # metadata about this ModelForm
    class Meta:
        # what model this form is for
        model = URL
        # what attributes are included
        fields = ['target',]

"""
    The form that is used when a user is signing up to be a RegisteredUser
"""
class SignupForm(forms.ModelForm):

    # The full name of the RegisteredUser
    full_name = forms.CharField(
        required = True,
        label = 'Full Name (Required)',
        max_length = 100,
        widget = forms.TextInput(),
    )

    # The RegisteredUser's chosen organization
    organization = forms.CharField(
        required = True,
        label = 'Organization (Required)',
        max_length = 100,
        widget = forms.TextInput(),
    )

    # The RegisteredUser's reason for signing up to us Go
    description = forms.CharField(
        required = False,
        label = 'Description (Optional)',
        max_length = 200,
        widget = forms.Textarea(),
    )

    # A user becomes registered when they agree to the TOS
    registered = forms.BooleanField(
        required=True,
        # ***Need to replace lower url with production URL*** ie. go.gmu.edu/about#terms
        label = mark_safe('Do you accept the <a href="http://127.0.0.1:8000/about#terms">Terms of Service</a>?'),
    )

    # on initialization of the form, crispy forms renders this layout
    def __init__(self, request, *args, **kwargs):
        # Necessary to call request in forms.py, is otherwise restricted to views.py and models.py
        self.request = request
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-6'

        self.helper.layout = Layout(
            Fieldset('',
                Div(
                    # Place in form fields
                    Div(
                        'full_name',
                        'organization',
                        'description',
                        'registered',
                        css_class='well'),

                    # Extras at bottom
                    StrictButton('Submit',css_class='btn btn-primary btn-md col-md-4', type='submit'),
                    css_class='col-md-6')))

    # metadata about this ModelForm
    class Meta:
        # what model this form is for
        model = RegisteredUser
        # what attributes are included
        fields = ['full_name', 'organization', 'description', 'registered',]
