Recommending posts by email
We will allow users to share blog posts with others by sending post recommendations via email. You
will learn how to create forms in Django, handle data submission, and send emails with Django, en-
hancing your blog with a personal touch.
Take a minute to think about how you could use views, URLs, and templates to create this functionality
using what you learned in the preceding chapter.
To allow users to share posts via email, we will need to:
1.Create a form for users to fill in their name, their email address, the recipient’s email address,
and optional comments
2.Create a view in the views.py file that handles the posted data and sends the email
3.Add a URL pattern for the new view in the urls.py file of the blog application
4.Create a template to display the form

Creating forms with Django
Let’s start by building the form to share posts. Django has a built-in forms framework that allows you
to create forms easily. The forms framework makes it simple to define the fields of the form, specify
how they have to be displayed, and indicate how they have to validate input data. The Django forms
framework offers a flexible way to render forms in HTML and handle data.
Django comes with two base classes to build forms:
•Form: This allows you to build standard forms by defining fields and validations.
•ModelForm: This allows you to build forms tied to model instances. It provides all the func-
tionalities of the base Form class, but form fields can be explicitly declared, or automatically
generated, from model fields. The form can be used to create or edit model instances.
First, create a forms.py file inside the directory of your blog application and add the following code to it:
from django import forms
class EmailPostForm(forms.Form):
name = forms.CharField(max_length=25)
email = forms.EmailField()
to = forms.EmailField()
comments = forms.CharField(
required=False,
widget=forms.Textarea
)
We have defined our first Django form. The EmailPostForm form inherits from the base Form class.
We use different field types to validate data accordingly.
Forms can reside anywhere in your Django project. The convention is to place them inside
a forms.py file for each application.
The form contains the following fields:
•name: An instance of CharField with a maximum length of 25 characters. We will use it for the
name of the person sending the post.
•email: An instance of EmailField. We will use the email of the person sending the post rec-
ommendation.
•
to: An instance of EmailField. We will use the email address of the recipient, who will receive
an email recommending the post.
•
comments: An instance of CharField. We will use it for comments to include in the post rec-
ommendation email. We have made this field optional by setting required to False, and we
have specified a custom widget to render the field.

Each field type has a default widget that determines how the field is rendered in HTML. The name field
is an instance of CharField. This type of field is rendered as an <input type="text"> HTML element.
The default widget can be overridden with the widget attribute. In the comments field, we use the
Textarea widget to display it as a <textarea> HTML element instead of the default <input> element.
Field validation also depends on the field type. For example, the email and to fields are EmailField
fields. Both fields require a valid email address; the field validation will otherwise raise a forms.
ValidationError exception and the form will not validate. Other parameters are also taken into
account for the form field validation, such as the name field having a maximum length of 25 or the
comments field being optional.
These are only some of the field types that Django provides for forms. You can find a list of all field
types available at https://docs.djangoproject.com/en/5.0/ref/forms/fields/.
Handling forms in views
We have defined the form to recommend posts via email. Now, we need a view to create an instance
of the form and handle the form submission.
Edit the views.py file of the blog application and add the following code to it:
from .forms import EmailPostForm
def post_share(request, post_id):
# Retrieve post by id
post = get_object_or_404(
Post,
id=post_id,
status=Post.Status.PUBLISHED
)
if request.method == 'POST':
# Form was submitted
form = EmailPostForm(request.POST)
if form.is_valid():
# Form fields passed validation
cd = form.cleaned_data
# ... send email
else:
form = EmailPostForm()
return render(
request,
'blog/post/share.html',
{'post': post,
'form': form
}
)

We have defined the post_share view that takes the request object and the post_id variable as pa-
rameters. We use the get_object_or_404() shortcut to retrieve a published post by its id.
We use the same view both for displaying the initial form and processing the submitted data. The HTTP
request method allows us to differentiate whether the form is being submitted. A GET request will
indicate that an empty form has to be displayed to the user and a POST request will indicate the form
is being submitted. We use request.method == 'POST' to differentiate between the two scenarios.
This is the process to display the form and handle the form submission:
1.
When the page is loaded for the first time, the view receives a GET request. In this case, a new
EmailPostForm instance is created and stored in the form variable. This form instance will be
used to display the empty form in the template:
form = EmailPostForm()
2.
When the user fills in the form and submits it via POST, a form instance is created using the
submitted data contained in request.POST:
if request.method == 'POST':
# Form was submitted
form = EmailPostForm(request.POST)
3.After this, the data submitted is validated using the form’s is_valid() method. This method
validates the data introduced in the form and returns True if all fields contain valid data. If
any field contains invalid data, then is_valid() returns False. The list of validation errors
can be obtained with form.errors.
4.If the form is not valid, the form is rendered in the template again, including the data submitted.
Validation errors will be displayed in the template.
5.If the form is valid, the validated data is retrieved with form.cleaned_data. This attribute is a
dictionary of form fields and their values. Forms not only validate the data but also clean the
data by normalizing it to a consistent format.
If your form data does not validate, cleaned_data will contain only the valid fields.
We have implemented the view to display the form and handle the form submission. We will now
learn how to send emails using Django and then we will add that functionality to the post_share view.

Sending emails with Django
Sending emails with Django is very straightforward. You need to have a local SMTP server, or you need
to access an external SMTP server, like your email service provider.
The following settings allow you to define the SMTP configuration to send emails with Django:
•EMAIL_HOST: The SMTP server host; the default is localhost
•EMAIL_PORT: The SMTP port; the default is 25
•EMAIL_HOST_USER: The username for the SMTP server
•EMAIL_HOST_PASSWORD: The password for the SMTP server
•EMAIL_USE_TLS: Whether to use a Transport Layer Security (TLS) secure connection
•EMAIL_USE_SSL: Whether to use an implicit TLS secure connection
Additionally, you can use the DEFAULT_FROM_EMAIL setting to specify the default sender when sending
emails with Django. For this example, we will use Google’s SMTP server with a standard Gmail account.
Working with environment variables
We will add SMTP configuration settings to the project, and we will load the SMTP credentials from
environment variables. By using environment variables, we will avoid embedding credentials in the
source code. There are multiple reasons to keep configuration separate from the code:
•Security: Credentials or secret keys in the code can lead to unintentional exposure, especially
if you push the code to public repositories.
•Flexibility: Keeping the configuration separate will allow you to use the same code base across
different environments without any changes. You will learn how to build multiple environments
in Chapter 17, Going Live.
•Maintainability: Changing a configuration won’t require a code change, ensuring that your
project remains consistent across versions.
To facilitate the separation of configuration from code, we are going to use python-decouple. This
library simplifies the use of environment variables in your projects. You can find information about
python-decouple at https://github.com/HBNetwork/python-decouple.
First, install python-decouple via pip by running the following command:
python -m pip install python-decouple==3.8
Then, create a new file inside your project’s root directory and name it .env. The .env file will contain
key-value pairs of environment variables. Add the following lines to the new file:
EMAIL_HOST_USER=your_account@gmail.com
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=My Blog <your_account@gmail.com>

If you have a Gmail account, replace your_account@gmail.com with your Gmail account. The EMAIL_
HOST_PASSWORD variable has no value yet, we will add it later. The DEFAULT_FROM_EMAIL variable will
be used to specify the default sender for our emails. If you don’t have a Gmail account, you can use
the SMTP credentials for your email service provider.
If you are using a git repository for your code, make sure to include .env in the .gitignore file of
your repository. By doing so, you ensure that credentials are excluded from the repository.
Edit the settings.py file of your project and add the following code to it:
from decouple import config
# ...
# Email server configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
The EMAIL_HOST_USER, EMAIL_HOST_PASSWORD and DEFAULT_FROM_EMAIL settings are now loaded from
environment variables defined in the .env file.
The provided EMAIL_HOST, EMAIL_PORT and EMAIL_USE_TLS settings are for Gmail’s SMTP server. If you
don’t have a Gmail account, you can use the SMTP server configuration of your email service provider.
Instead of Gmail, you can also use a professional, scalable email service that allows you to send emails
via SMTP using your own domain, such as SendGrid (https://sendgrid.com/) or Amazon Simple
Email Service (SES) (https://aws.amazon.com/ses/). Both services will require you to verify your
domain and sender email accounts and will provide you with SMTP credentials to send emails. The
django-anymail application simplifies the task of adding email service providers to your project
like SendGrid or Amazon SES. You can find installation instructions for django-anymail at https://
anymail.dev/en/stable/installation/, and the list of supported email service providers at https://
anymail.dev/en/stable/esps/.
If you can’t use an SMTP server, you can tel Django to write emails to the console by adding the fol-
lowing setting to the settings.py file:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
By using this setting, Django will output all emails to the shell instead of sending them. This is very
useful for testing your application without an SMTP server.
In order to send emails with Gmail’s SMTP server, make sure that two-step verification is active in
your Gmail account.