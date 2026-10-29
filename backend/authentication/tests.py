from django.contrib.auth import get_user_model
from django.test import TestCase


class RegisterViewTests(TestCase):
    def test_invalid_login_message_is_vietnamese(self):
        response = self.client.post(
            '/api/v1/auth/login/',
            {'username': 'missing-user', 'password': 'invalid-password'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()['detail'],
            'Tên đăng nhập hoặc mật khẩu không chính xác, hoặc tài khoản đã bị vô hiệu hóa.',
        )

    def test_register_creates_patient_and_hashes_password(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'new-patient',
                'email': 'patient@example.com',
                'password': 'A-strong-password-948!',
                'first_name': 'Nguyen',
                'last_name': 'An',
                'role': 'Patient',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201, response.content)
        user = get_user_model().objects.get(username='new-patient')
        self.assertEqual(user.email, 'patient@example.com')
        self.assertEqual(user.first_name, 'Nguyen')
        self.assertEqual(user.last_name, 'An')
        self.assertEqual(user.role, get_user_model().Role.PATIENT)
        self.assertTrue(user.check_password('A-strong-password-948!'))
        self.assertNotIn('password', response.json())

    def test_duplicate_username_returns_validation_error(self):
        get_user_model().objects.create_user(
            username='existing-patient',
            password='A-strong-password-948!',
        )

        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'existing-patient',
                'email': 'patient@example.com',
                'password': 'A-strong-password-948!',
                'first_name': 'Nguyen',
                'last_name': 'An',
                'role': 'Patient',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn('username', response.json())

    def test_registration_rejects_non_patient_role(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'new-admin',
                'email': 'admin@example.com',
                'password': 'A-strong-password-948!',
                'first_name': 'Clinic',
                'last_name': 'Admin',
                'role': 'Admin',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn('role', response.json())
        self.assertFalse(get_user_model().objects.filter(username='new-admin').exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'new-patient',
                'email': 'patient@example.com',
                'password': 'password',
                'first_name': 'Nguyen',
                'last_name': 'An',
                'role': 'Patient',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn('password', response.json())
        self.assertFalse(get_user_model().objects.filter(username='new-patient').exists())
