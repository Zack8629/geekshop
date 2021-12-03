from django.conf import settings
from django.test import TestCase, Client

from authapp.models import ShopUser


class TestUserManagement(TestCase):
    fixtures = ['mainapp.json']

    def setUp(self):
        self.client = Client()
        self.superuser = ShopUser.objects.create_superuser(
            'django2', 'django2@geekshop.local', 'geekbrains'
        )
        self.user = ShopUser.objects.create_user(
            'user1', 'user1@geekshop.local', 'geekbrains'
        )
        self.user_with__first_name = ShopUser.objects.create_user(
            'user2', 'user2@geekshop.local', 'geekbrains', first_name='Пользователь 2'
        )

    def test_user_login(self):
        # главная без логина
        response = self.client.get('/')
        # print(dir(response))
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(response.context['page_title'], 'главная магазина')
        self.assertNotContains(response, 'Пользователь', status_code=200)

        # данные пользователя
        self.client.post('/auth/login/',
                         data={'username': 'user1',
                               'password': 'geekbrains'})

        # главная после логина
        response = self.client.get('/')
        self.assertEqual(self.user, response.context['user'])
        self.assertContains(response, 'Пользователь', status_code=200)

    def test_basket_login_redirect(self):
        # без логина должен переадресовать
        response = self.client.get('/basket/')
        self.assertEqual('/auth/login/?next=/basket/', response.url)
        self.assertEqual(302, response.status_code)

        # с логином все должно быть хорошо
        self.client.login(username='user1', password='geekbrains')

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([], list(response.context['user'].basket_items))
        self.assertEqual('/basket/', response.request['PATH_INFO'])
        self.assertIn('Ваша корзина,', response.content.decode('utf-8'))

    def test_user_logout(self):
        # данные пользователя
        self.client.login(username='user1', password='geekbrains')

        # логинимся
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        # выходим из системы
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)

        # главная после выхода
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)

    def test_user_register(self):
        # логин без данных пользователя
        response = self.client.get('/auth/user/registration/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('регистрация', response.context['page_title'])
        self.assertTrue(response.context['user'].is_anonymous)

        new_user_data = {
            'username': 'user3',
            'first_name': 'Пользователь',
            'last_name': 'три',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'user3@geekshop.local',
            'age': '21'
        }

        response = self.client.post('/auth/user/registration/', data=new_user_data)
        self.assertEqual(response.status_code, 302)

        new_user = ShopUser.objects.get(username=new_user_data['username'])
        self.assertFalse(new_user.is_active)

        activation_url = f"{settings.DOMAIN_NAME}/auth/user/verify/{new_user_data['email']}/" \
                         f"{new_user.activation_key}/"

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)

        # данные нового пользователя
        self.client.login(
            username=new_user_data['username'],
            password=new_user_data['password1']
        )

        # проверяем главную страницу
        response = self.client.get('/')
        self.assertContains(response, text=new_user_data['first_name'], status_code=200)

    def test_user_wrong_register(self):
        new_user_data = {
            'username': 'user4',
            'first_name': 'Пользователь 3',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'user4@geekshop.local',
            'age': '17'
        }

        response = self.client.post('/auth/user/registration/', data=new_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'age', 'Вам ещё нет 18!'
        )
