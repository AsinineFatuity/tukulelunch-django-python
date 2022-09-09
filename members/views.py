from typing import IO
from django.core import paginator
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,get_object_or_404,redirect
from .models import Category, Commitment, CommittedItem,Item,PledgeItem,Pledge,Payment


#imports to handle the forms
from django.contrib.auth.models import Group, User
from .forms import SignUpForm,ContactForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout

#to show the logged in user their pledge history we first import login required functionality
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

#to handle the emails
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.template.loader import get_template
from django.core.mail import EmailMessage, message,send_mail,BadHeaderError

#to aid in the password reset
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from datetime import datetime

def home_page(request):
    return render(request,'home.html')
#display the specific item and the description
def item_page(request,category_slug,item_slug):
    try:
        #the __ is used to access the slug field of the foreign key category this is instead of dot (a django feature)
        item=Item.objects.get(category__slug=category_slug,slug=item_slug)
    except Exception as e:
        raise e
    return render(request,'item.html',{'item':item})
#use the category slugs to find the different categories and display all the products therein
def display_page(request,category_slug=None):
    category_page=None
    items_list=None
    if category_slug!=None:
        category_page=get_object_or_404(Category,slug=category_slug)
        items_list=Item.objects.filter(category=category_page,available=True)
    else:
        items_list=Item.objects.all().filter(available=True)
    # Set up Pagination, we want to paginate the list of items with four items displayed per page
    paginator = Paginator(items_list,4)
    #Keep track of what page we are on in the app by getting the value of the GET variable called page and if it does not exist return 1, we cast page to integer
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1
    try:
        items = paginator.page(page) # returns for example <page 1 of 2> object whose specific objects can be accessed using products.object_list
    except(EmptyPage,InvalidPage):
        items = paginator.page(paginator.num_pages)
    return render(request,'display.html',{'category':category_page,'items':items})
#persist the pledges as the user is still browsing the webapp
def pledge_id_fn(request):
    pledge=request.session.session_key
    if not pledge:
        pledge=request.session.create()
    return pledge
#add pledge and the quantity
def add_pledge(request,item_id):
  
    item=Item.objects.get(id=item_id)
    #ensure item is not added more than once in a  pledge (analogous to cart)
    try:
        pledge=Pledge.objects.get(pledge_id=pledge_id_fn(request))   
    except Pledge.DoesNotExist:
        pledge=Pledge.objects.create(
            pledge_id=pledge_id_fn(request)
        )
        pledge.save()
    try:
        pledge_item=PledgeItem.objects.get(item=item,pledge=pledge)
        #only increment if the item has not been fully pledged
        if pledge_item.quantity < pledge_item.item.stock:
            pledge_item.quantity +=1
        pledge_item.save()
    except PledgeItem.DoesNotExist:
        pledge_item=PledgeItem.objects.create(
            item=item,
            quantity=1,
            pledge=pledge
        )
        pledge_item.save()
    return redirect('pledge_detail')
#create all pledged items in the current session if none exists then ignore using pass
def pledge_detail(request,total=0,counter=0,pledge_items=None):
    try:
        pledge=Pledge.objects.get(pledge_id=pledge_id_fn(request))
        pledge_items=PledgeItem.objects.filter(pledge=pledge,active=True)
        for pledge_item in pledge_items:
            total+=(pledge_item.item.price*pledge_item.quantity)
            counter+=pledge_item.quantity
    except ObjectDoesNotExist:
        pass
    #process the commitment form once the commitment has been made
    if request.method == 'POST':
        try:
            token = request.POST['csrfmiddlewaretoken']
            name = request.POST['name']
            email = request.POST['email']
            phone = request.POST['phone']
            ministry=request.POST['ministry']
        except Exception as request_error:
            raise request_error
        #Create the Committment Model
        try:
            commitment_details=Commitment.objects.create(
                token=token,
                name=name,
                email_address=email,
                phone_number=phone,
                ministry=ministry,
                commitment_date = datetime.date(datetime.now()),
                total=total       
            )
            commitment_details.save()
        #commit the committed items to database
            for committed_item in pledge_items:
                comm_item_to_db=CommittedItem.objects.create(
                item = committed_item.item.name,
                quantity = committed_item.quantity,
                price = committed_item.item.price,
                commitment = commitment_details
            )
                comm_item_to_db.save()
               #Since pledge has been committed to, we will then reduce the stock in our database Begin by getting the product in the Product model using the committed item id
                items = Item.objects.get(id=committed_item.item.id)
                items.stock = int(committed_item.item.stock-committed_item.quantity)
                items.save() #update the stock 
                #Now remove the items from the Pledging Cart (analogous to shopping cart)
                committed_item.delete() #can decide to delay the deleting till after payment so as to show case progress (Not necessary I have the committed items Model' this is a safer business logic)
            try:
                #send the email with the committment items
                send_email(commitment_details.id)
            except IOError as ioe:
                return ioe
            #Redirect to the thank you page after successful processing of the commitment details pass the specific commitment id too
            return redirect('danke_prima',commitment_details.id)

        except Exception as commitment_error:
            raise commitment_error
    return render(request,'pledge.html',dict(pledge_items=pledge_items,total=total,counter=counter))
#remove any deleted or deducted pledged item
def remove_pledge(request,item_id):
    pledge=Pledge.objects.get(pledge_id=pledge_id_fn(request)) #get the pledge in the current session 
    item=get_object_or_404(Item,id=item_id)
    pledge_item=PledgeItem.objects.get(item=item,pledge=pledge)
    if pledge_item.quantity>1:
        pledge_item.quantity-=1
        pledge_item.save()
    else:
        pledge_item.delete()
    return redirect('pledge_detail')
def delete_pledge(request,item_id):
    pledge=Pledge.objects.get(pledge_id=pledge_id_fn(request)) #get the pledge in the current session 
    item=get_object_or_404(Item,id=item_id)
    pledge_item=PledgeItem.objects.get(item=item,pledge=pledge)
    pledge_item.delete()
    return redirect('pledge_detail')
def thankyou_page(request,commitment_id):
    #we use the commitment_id to get the specific person
    if commitment_id:
        member_commitment=get_object_or_404(Commitment,id=commitment_id)
    return render(request,'thankyou.html',{'member_commitment':member_commitment})
#sign up view function
#sign up view function
def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            sign_up_user = User.objects.get(username=username)
            pledgers_group = Group.objects.get(name='Pledgers')
            pledgers_group.user_set.add(sign_up_user)
            signin_user = authenticate (username=username,password=raw_password)
            login(request,signin_user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request,'signup.html',{'form':form})
#sign in the user
def sign_in_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                return redirect('signup')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html',{'form':form})
#signout the user 
#(Note to myself: redirect does not take request as an argument else you will have the url redirecting to itself hence NoReverseMatch error)
def sign_out_view(request):
    logout(request)
    return redirect('signin')
#say something directive about the web app
def about(request):
    return render(request,'about.html')

#commitment_history
#to customize the login redirect from django's (accounts/login/?next=/) we add the following the login required decorator
@login_required (redirect_field_name='next',login_url='signin')
def commitment_history(request):
    if request.user.is_authenticated:
       #extract the user email from the request and then use it to match the one in the commitment details
       email = str(request.user.email)
       commitment_details = Commitment.objects.filter(email_address=email)
       #extract the url path so that I render commitment history or payment history depending on what the user clicks
       if request.method == 'GET':
           raw_url_path = str(request.path)
           ref_url_path =raw_url_path.replace('/','')
           if ref_url_path == "commitment_history":
               url_path = True
           elif ref_url_path == "payment_history":
               url_path = False                         
    return render (request,'commitment_history.html',{'commitment_details':commitment_details,'url_path':url_path})
# view to render the commitment details
@login_required (redirect_field_name='next',login_url='signin')
def commitment_details(request,commitment_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        commitment = Commitment.objects.get(id=commitment_id,email_address=email)
        commited_items = CommittedItem.objects.filter(commitment=commitment)
        try:
            payment_details = Payment.objects.filter(pay_commitment=commitment).order_by('-date_paid')[0] 
        except IndexError as ie:
            payment_details = Payment.objects.filter(pay_commitment=commitment).order_by('-date_paid')
    return render(request,'commitment_detail.html',{'commitment':commitment,'commited_items':commited_items,'payment':payment_details})
# view to render user's payment history
@login_required (redirect_field_name='next',login_url='signin')
def payment_detail(request,commitment_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        commitment_details = Commitment.objects.get(id=commitment_id,email_address=email)
        payment_details = Payment.objects.filter(pay_commitment=commitment_id) 
    return render (request, 'payment_history.html',{'commitment_details':commitment_details,'payment_details':payment_details})
#search function
def search(request):
    items = Item.objects.filter(name__contains=request.GET['item'])
    return render (request, 'display.html',{'items':items})
#send emails to the pledgers on their commitments
def send_email(commitment_id):
    transaction = Commitment.objects.get(id=commitment_id)
    commitment_items = CommittedItem.objects.filter(commitment=transaction)
    #configuring the email parameters
    try:
        subject = "Tukule Lunch - New Pledge Commitment #{}".format(transaction.id)
        to = ['{}'.format(transaction.email_address)]
        from_email = "tukulelunch@gmail.com"
        commitment_information = {
            'transaction':transaction,
            'commitment_items':commitment_items
        }
        #dynamically generate html for emails
        message = get_template('email/email.html').render(commitment_information)
        #fill the email message content
        msg = EmailMessage(subject,message,to=to,from_email=from_email)
        #change the default content type from plain text to html
        msg.content_subtype = 'html'
        #send the email
        msg.send()
    except IOError as ioe:
        return ioe
#contact page
def contact(request):
    if request.method == 'POST':  
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            name = form.cleaned_data.get('name')
            from_email = form.cleaned_data.get('from_email')
            message = form.cleaned_data.get('message')
            #human readable formatting
            message_format = "{0} has sent you a new message:\n\n{1}\n\n Email Address is: {2}".format(name,message,from_email)
            # create the email message
            msg = EmailMessage(
                subject,
                message_format,
                to=['tukulelunch@gmail.com'],
                from_email=from_email
                )
            msg.send()
            return render(request,'contact_success.html')
    else:
        form = ContactForm()

    return render(request,'contact.html',{'form':form})
#to handle forgotten password
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'tukulelunch.pythonanywhere.com',
					'site_name': 'TUKULE LUNCH',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'tukulelunch@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})
    