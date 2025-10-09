from urllib import request
from . models import Friend, UserRegistration,Expense,FriendExpense,Groups
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
import random
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db.models import Sum, Avg
from django.urls import reverse
# Create your views here.

def index(request):
    return redirect('register')

@never_cache
def register(request):
      # If user is already logged in, redirect to landing page
    if request.session.get('username'):
        return redirect('landing_page')
    # Retrieving the form data and allowing user to register
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        c_password = request.POST.get('c_password')

        #validating password and email
        if password != c_password:
            messages.error(request, "Password do not match")
            return redirect('register')
        
        elif UserRegistration.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
        
        else:
            #Generate OTP
            otp_code = generate_otp()
            
            #Now, before we make another request to server and lose our data stored in the python variables, lets store them in session
            request.session['username'] = name
            request.session['email'] = email
            request.session['password'] = password               #Not safe, we should hash it first and then store it
            request.session['generated_otp'] = otp_code
            
            #Sending OTP to the user's email
            send_mail(
                subject='Your OTP Code',
                message=f'Hello {name}, your OTP is {otp_code}.',
                from_email="yashp07052004@gmail.com",
                recipient_list=[email],
                fail_silently=False,
            )

            return redirect('otp_page')
    return render(request, 'tracker/register.html')

@never_cache
def otp_page(request):
    if request.method == "POST":
        entered_otp = request.POST.get('user_otp')                   #Retrieving the OTP entered by user
        generated_otp = request.session.get('generated_otp')         #Retrieving the OTP stored in session

        #Validating the OTP
        if str(entered_otp) == str(generated_otp):
            #Creating a new user in the database
            user = UserRegistration(
                name = request.session.get('username'),
                email = request.session.get('email'),
                password = request.session.get('password'),
            )
            user.save()

            #Removing OTP from session data
            request.session.pop('generated_otp', None)
            messages.success(request, "Registration Successful! You can now log in.")
            return redirect('login')

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('otp_page')
    return render(request, 'tracker/otp_page.html')

#Helper Function
def generate_otp():
    return random.randint(1000,9999)

@never_cache
def login_page(request):
    # If user is already logged in, redirect to landing page
    if request.session.get('username'):
        return redirect('landing_page')
    

    # Retrieving the form data and allowing user to login
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            #user = UserRegistration.objects.filter(email=email, password=password).exists() # cannot use since it returns a boolean value and does not give access to user id and name
            #Therefore we use this :-
            user = UserRegistration.objects.get(email=email, password=password) # will raise DoesNotExist exception if no user found

            # Storing user info in session
            request.session['user_id'] = user.id
            request.session['username'] = user.name


            messages.success(request, "Login Successful!")
            return redirect('landing_page')
        

        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid Credentials. Please try again.")
            return redirect('login')
        
    return render(request, 'tracker/login.html')

def logout_page(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect ('login')

@never_cache
def landing_page(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    else:
        return render(request, 'tracker/landing_page.html')

#Personal Dashboard
@never_cache
def personal_dashboard(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    
    #fetch Expenses for the logged-in user
    expenses = Expense.objects.filter(user_id=request.session['user_id']).order_by('-date')

    #Get filter values from GET parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', '')

   #Apply search filter
    if search_query:
        expenses = expenses.filter(title__icontains=search_query)

    #Apply category filter
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    #Apply sorting
    if sort_by == 'amount_asc':
        expenses = expenses.order_by('amount')
    elif sort_by == 'amount_desc':
        expenses = expenses.order_by('-amount')
    else:
        expenses = expenses.order_by('-date')  # Default sorting by date descending

    
    #Statistics Section
    total_spent = expenses.aggregate(total = Sum('amount'))['total'] or 0
    avg_spent = expenses.aggregate(avg=Avg('amount'))['avg'] or 0

    #Current month expenses
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_expenses = expenses.filter(date__month =current_month, date__year=current_year)
    monthly_total = monthly_expenses.aggregate(total=Sum('amount'))['total'] or 0

    #Category-wise totals
    category_totals = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'expenses': expenses,
        'username': request.session.get('username'),
        'total_spent': total_spent,
        'avg_spent': avg_spent,
        'monthly_total': monthly_total,
        'category_totals': category_totals,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }

    #Passing them to the template
    return render(request, 'tracker/personal.html', context)

#Friends Dashboard

    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
    return render(request, 'tracker/friends.html')

#Friends Dashboard
def friends_dashboard(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    else:
        #Fetch user_id from session and list his friends
        user_id = request.session.get('user_id')
        friends = Friend.objects.filter(user_id=user_id)
    return render(request, 'tracker/friends.html', {'friends': friends})

def add_friend(request):
    if request.method == 'POST':
        friend_email = request.POST.get('friend_email')
        print('Trying Friend:',friend_email)
        print(UserRegistration.objects.values_list('name','email'))
        try:
            friend_user = UserRegistration.objects.get(email=friend_email)
            user = UserRegistration.objects.get(id=request.session.get('user_id'))
            #Create a Friend instance 
            Friend.objects.create(user=user, friend_user=friend_user)
            messages.success(request, "Friend added successfully!")
            #Send invite email
            try:
                send_mail(
                    subject=f"{user.name} is inviting you to 'tracker'",
                    message=f"{user.name} is inviting you to join 'tracker' to share and manage your expenses together.",
                    from_email='yashp07052004@gmail.com',
                    recipient_list=[friend_user.email],
                    fail_silently=True
                )
            except Exception as e:
                print("Email sending failed", e)
                messages.warning(request, "Friend added, but email failed")
        except UserRegistration.DoesNotExist:
            messages.error(request, "User not found.")
        return redirect('friends_dashboard')
    return render(request, 'tracker/add_friend.html')

def friend_details(request, friend_id):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    user_id = request.session.get('user_id')
    #passing user and friend to the template from this view
    user = UserRegistration.objects.get(id=user_id)
    friend = UserRegistration.objects.get(id=friend_id)
    friend = UserRegistration.objects.get(id=friend_id)
    expenses = FriendExpense.objects.filter(
        Q(user_id=user_id, friend_user_id=friend_id) |
        Q(user_id=friend_id, friend_user_id=user_id)
    ).order_by('-date')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'friend': friend,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'user':user
    }
    return render(request, 'tracker/friend_details.html', context)

def remove_friend(request,friend_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        #Remove both directions
        Friend.objects.filter(user_id=user_id, friend_user_id=friend_id).delete()
        Friend.objects.filter(user_id=friend_id, friend_user_id=user_id).delete()
        messages.success(request, "Friend removed")
    return redirect('friends_dashboard')

def add_expense_with_friend(request, friend_id):
    if 'username' not in request.session:
        return redirect('login')
    friend = UserRegistration.objects.get(id=friend_id)
    user = UserRegistration.objects.get(id=request.session.get('user_id'))
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description', '')
        try:
            paid_by_id = int(request.POST.get('paid_by'))
            paid_by = UserRegistration.objects.get(id=paid_by_id)
        except (TypeError, ValueError, UserRegistration.DoesNotExist):
            messages.error(request,"Invalid payer selected")
            return redirect(request.path)
        #Split logic for now-->equal split
        amount_owed = amount / 2
        FriendExpense.objects.create(
            user=user,
            friend_user=friend,
            title=title,
            amount=amount,
            category=category,
            description=description,
            paid_by=paid_by,
            amount_owed=amount_owed,
        )
        messages.success(request, "Expense added successfully!")
        return redirect('friend_details', friend_id=friend_id)
    return render(request, 'tracker/add_expense_with_friend.html', {'friend': friend, 'user':user})

def expense_details(request, friend_id):
    user_id = request.session.get('user_id')
    user = UserRegistration.objects.get(id=user_id)
    friend = UserRegistration.objects.get(id=friend_id)
    title = request.GET.get('title', '')
    description = request.GET.get('description', '')
    category = request.GET.get('category', '')
    amount = float(request.GET.get('amount', 0))
    paid_by = int(request.GET.get('paid_by', user_id))
    return render(request, 'tracker/expense_details.html', {
        'user': user,
        'friend': friend,
        'title': title,
        'description': description,
        'category': category,
        'amount': amount,
        'paid_by': paid_by,
    })

def save_split_expense(request, friend_id):
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                # Handle case where user is not logged in
                return JsonResponse({'status': 'error', 'message': 'User not authenticated.'}, status=401)
            
            # Get data from the POST request
            amount = float(request.POST.get('amount'))
            friend = UserRegistration.objects.get(id=friend_id)
            user = UserRegistration.objects.get(id=user_id)
            user_share = float(request.POST.get('user_share'))
            friend_share = float(request.POST.get('friend_share'))
            paid_by_id = int(request.POST.get('paid_by'))
            paid_by = UserRegistration.objects.get(id=paid_by_id)

            # Determine who owes what
            # If the current user paid, the friend owes their share.
            # If the friend paid, the current user owes their share.
            amount_owed_by_friend_to_user = friend_share if paid_by_id == user_id else -user_share

            # Save the new expense record
            FriendExpense.objects.create(
                user=user,
                friend_user=friend,
                title=request.POST.get('title'),
                amount=amount,
                category=request.POST.get('category'),
                description=request.POST.get('description', ''),
                paid_by=paid_by,
                # amount_owed logic corrected to handle debt direction
                # Positive value means friend owes user, negative means user owes friend.
                amount_owed=amount_owed_by_friend_to_user 
            )

            messages.success(request, "Expense split and saved!")
            
            # **THE FIX**: Return a JSON response with the redirect URL
            redirect_url = reverse('friend_details', kwargs={'friend_id': friend_id})
            return JsonResponse({'status': 'success', 'redirect_url': redirect_url})

        except UserRegistration.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid user or friend ID.'}, status=404)
        except Exception as e:
            # Catch other potential errors (e.g., float conversion)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # Handle non-POST requests
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

#Groups Dashboard
def groups_dashboard(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    else:
        user_id = request.session.get('user_id')
        user = UserRegistration.objects.get(id=user_id)
        groups = Groups.objects.filter(members=user)
    return render(request, 'tracker/groups.html', {'groups' : groups})

def create_group(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    
    user_id = request.session.get('user_id')
    user = UserRegistration.objects.get(id=user_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')

        #Why if
        if name and category:
            group = Groups.objects.create(name=name, category=category, created_by=user)
            messages.success(request, "Group created successfully!")
            return redirect('groups')
        else:
            messages.error(request,"Please fill all fields.")
    return render(request, 'tracker/create_group.html')


#Activity Dashboard
def activity_dashboard(request):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    return render(request, 'tracker/activity.html')

#CRUD
def add_expense(request):
    if request.method == 'POST':

        #Get logged in user from session to know which user is adding the expense
        user_id = request.session.get('user_id')
        user = UserRegistration.objects.get(id=user_id)

        #Get form data
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date = request.POST.get('date')
        description = request.POST.get('description')

        #Save to DB
        expense = Expense(
            user=user,
            title=title,
            amount=amount,
            category=category,
            date=datetime.strptime(date, "%Y-%m-%d").date(),  # Convert string to date object
            description=description,
        )
        expense.save()

        #Show success message
        messages.success(request, "Expense added successfully!")
        return redirect('landing_page')

    return render(request, 'tracker/add_expense.html')

def edit_expense(request, expense_id):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    
    #Fetch the expense to be edited
    expense = get_object_or_404(Expense, id=expense_id, user_id=request.session['user_id'])

    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')
        expense.save()
        return redirect('landing_page')

    return render(request, 'tracker/edit_expense.html', {'expense': expense})

def delete_expense(request, expense_id):
    if 'username' not in request.session:
        messages.error(request, "Please log in to access this page.")
        return redirect('login')
    
    expense = get_object_or_404(Expense, id=expense_id, user_id=request.session['user_id'])

    if request.method == 'POST':
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect('landing_page')
    
    return render(request, 'tracker/delete_expense.html', {'expense': expense})