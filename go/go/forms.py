from django import forms
from go.models import URL, RegisteredUser
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div, Field
from crispy_forms.bootstrap import StrictButton, PrependedText, Accordion, AccordionGroup

class URLForm(forms.ModelForm):

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
            URL.objects.get(short__iexact=value)
        except URL.DoesNotExist:
            return
        raise ValidationError('Short url already exists.')

    # Custom short-url field with validators.
    short = forms.SlugField(
        required=False,
        label='Short URL (Optional)',
        widget=forms.TextInput(),
        validators=[unique_short],
        max_length=20,
        min_length=3,
    )

    DAY = '1 Day'
    WEEK = '1 Week'
    MONTH = '1 Month'
    NEVER = 'Never'

    EXPIRATION_CHOICES = (
        (DAY, DAY),
        (WEEK, WEEK),
        (MONTH, MONTH),
        (NEVER, NEVER),
    )

    # Add a custom expiration choice field.
    expires = forms.ChoiceField(
        required=True,
        label='Expiration (Required)',
        choices=EXPIRATION_CHOICES,
        initial=NEVER,
        widget=forms.RadioSelect(),
    )

    def __init__(self, *args, **kwargs):
        super(URLForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-1'
        self.helper.field_class = 'col-md-6'


        self.helper.layout = Layout(
            Fieldset(
                '',
                Accordion(
                    AccordionGroup('Step 1: Long URL',
                        Div(
                            HTML("""
                                <h4>Paste the URL you would like to shorten:</h4>
                                <br />
                            """),
                            'target',
                            style="background: rgb(#F6F6F6);",
                            title="target_url",
                            css_class="first_group",
                        ),
                        css_id='firstCollapse',
                        active=True,
                        template='crispy/accordian-group.html',
                    ),
                    AccordionGroup('Step 2: Short URL',
                        Div(
                            HTML("""
                                <h4>Create a custom Go address:</h4>
                                <br />
                            """),
                            PrependedText('short',
                            'https://go.gmu.edu/',
                            ),
                            style="background: rgb(#F6F6F6);",
                            title="short_url",
                            css_class="second_group",
                        ),
                        css_id='secondCollapse',
                        active=True,
                        template='crispy/accordian-group.html',
                    ),
                    AccordionGroup('Step 3: URL Expiration',
                        Div(
                            HTML("""
                                <h4>Set when you would like your Go address to expire:</h4>
                                <br />
                            """),
                            'expires',
                            style="background: rgb(#F6F6F6);",
                            title="expires_url",
                            css_class="third_group",
                        ),
                        css_id='thirdCollapse',
                        active=True,
                        template='crispy/accordian-group.html',
                    ),
                    css_id='accordian',
                    template='crispy/accordian.html'
                ),
            HTML("""
                <br />
            """),
            StrictButton('Shorten', css_class="btn-success", type='submit'),
        )
    )


    class Meta:
        model = URL
        fields = ('target',)
        exclude = ('owner', 'short', 'date_created', 'clicks', 'expires')


class SignupForm(forms.ModelForm):

    def validate_username(username):
        try:
            registered = RegisteredUser.objects.get(username=username)
            raise ValidationError('Username "%s" is already in use.' % username)
        except RegisteredUser.DoesNotExist:
            return

    username = forms.CharField(
        required=True,
        label='Mason NetID (Required)',
        max_length=30,
        validators=[validate_username],
        widget=forms.TextInput(attrs={
        }),
    )
    full_name = forms.CharField(
        required=True,
        label='Full Name (Required)',
        max_length=100,
        widget=forms.TextInput(attrs={
        }),
    )
    organization = forms.CharField(
        required=True,
        label='Organization (Required)',
        max_length=100,
        widget=forms.TextInput(attrs={
        })
    )
    description = forms.CharField(
        required=False,
        label='Description (Optional)',
        max_length=200,
        widget=forms.Textarea(attrs={
        }),
    )
    tos_box = forms.BooleanField(
        required=True,
        # Need to add a Terms of Service Page and replace the href below
        label = mark_safe('Do you accept the <a href="#" target="_blank">Terms of Service</a>?'),
    )

    def clean_username(self):
        # Prevent hax: (non-staff) Users cannot signup for other users
        cleaned_data = super(SignupForm, self).clean()
        data_username = cleaned_data.get("username")

        if not self.request.user.is_staff:
            if self.request.user.username not in data_username:
                self.add_error('username', "This is not your NetID!")
        return data_username

    def __init__(self, request, *args, **kwargs):
        # Necessary to call request in forms.py, is otherwise restricted to views.py and models.py
        self.request = request
        super(SignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(form=self)
        self.helper.form_method = 'POST'

    def clean_username(self):
        # Prevent hax: (non-staff) Users cannot signup for other users
        cleaned_data = super(SignupForm, self).clean()
        data_username = cleaned_data.get("username")

        if not self.request.user.is_staff:
            if self.request.user.username not in data_username:
                self.add_error('username', "This is not your NetID!")
        return data_username

    def __init__(self, request, *args, **kwargs):
        # Necessary to call request in forms.py, is otherwise restricted to views.py and models.py
        self.request = request
        super(SignupForm, self).__init__(*args, **kwargs)

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4'
        self.helper.field_class = 'col-md-6'

        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div(
                        'username',
                        'full_name',
                        'organization',
                        'description',
                        'tos_box',
                        css_class='well',
                    ),
                    StrictButton('Submit',css_class='btn btn-primary btn-md col-md-4', type='submit'),
                    css_class='col-md-6',
                ),
            )
        )
    class Meta:
        model = RegisteredUser
        fields = '__all__'
