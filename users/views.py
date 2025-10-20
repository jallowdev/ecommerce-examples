from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.db import transaction
from django.shortcuts import render, redirect
from django.views import View

from core.commons.commons import generate_code
from core.commons.exception import CustomException
from users.forms import LoginForm, SignUpForm
from users.models import User, Entity, Profile, Address
from users.utils import CustomPasswordValidator, create_or_group_and_permission


class LoginView(View):

    def get(self, request):
        form = LoginForm(request.POST or None)
        sign_up_form = SignUpForm(request.POST or None)
        msg = None
        if request.user.is_authenticated and isinstance(request.user, User):
            return redirect('index_cosmos')
        return render(request, 'cosmos/users/login.html', {"sign_up_form": sign_up_form, "form": form, "msg": msg})

    def post(self, request):
        try:
            if request.method == "POST":
                email = request.POST.get('email')
                password = request.POST.get('password')
                user = authenticate(request, email=email, password=password)
                print(f'### LOGIN REQUEST  : {email} passe :{password} authenticated : {user}')

                if user is not None:
                    request.session['user_id'] = user.pk
                    request.session['username'] = email
                    msg = 'login avec succès. Bienvenue dans votre espace de travail.'
                    messages.success(request, message=msg)
                    return redirect('index_cosmos')

                else:
                    msg = 'Login ou mot de passe incorrect. Veuillez verifier vos credential.'
                    raise CustomException(message=msg,status=400)

            return redirect('login_cosmos')
        except CustomException as ex:
            print(f'## CustomException : {ex}')
            messages.warning(request, ex.detail)
            return redirect('login_cosmos')

        except Exception as ex:
            print(f'## EXCEPTION: {ex}')
            messages.error(request, 'Erreur de traitement du serveur..')
            return redirect('login_cosmos')


@transaction.atomic()
def logout_view(request):
    user_id = request.session.get('user_id')
    print(f"### session user: {user_id} id : {request.user.id} pk : {request.user.pk}")
    user = User.objects.filter(user__id=user_id).get()
    # logout_auth_session(account=userAccount)

    username = f'{user.first_name} {user.last_name}'
    logout(request)
    request.session.flush()
    messages.info(request, f"Vous avez été déconnecté avec succès. Au revoir {username}!")
    return redirect('login')


@transaction.atomic
def register_user(request):
    try:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if (password1 is not None and password2 is not None) and (password1 != password2):
            raise CustomException(message="Le deux mots de passe ne sont pas identiques. Veuillez verifier!",
                                  status=400)
        if password1:
            CustomPasswordValidator.validate(password=password1)
        email_valid = User.objects.filter(email=email)
        if email_valid:
            raise CustomException(message="Le mail exist déja avec un compte. Veuillez verifier!", status=400)

        new_user = User.objects.create(
            username=generate_code(8),
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_staff=True
        )
        new_user.set_password(password1)

        group_client = create_or_group_and_permission(name='CUSTOMER',permis=['list_products', 'create_order', 'checkout_cart'])
        new_user.groups.add(group_client)

        entity = Entity.objects.filter(identity='003')
        if not entity:
            raise CustomException(message="L'entité choisie n'exist pas dans le systeme. Veuillez verifier!",
                                  status=400)
        entity = entity.get()

        profile = Profile.objects.create(phone=phone)
        address = Address.objects.create(country="SENEGAL")
        new_user.entity = entity
        new_user.profile = profile
        new_user.address = address

        new_user.save()

        messages.info(request, f"Votre compte a été créé avec succes. Veuillez vous connecter!")
        return redirect('login')

    except CustomException as ex:
        print(f'## CustomException : {ex}')
        messages.error(request, ex.detail)
        return redirect('login_cosmos')

    except Exception as ex:
        print(f'## EXCEPTION: {ex}')
        messages.error(request, 'Erreur de traitement du serveur..')
        return redirect('login_cosmos')
