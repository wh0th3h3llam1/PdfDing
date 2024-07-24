from django.test import override_settings
from django.urls import reverse
from playwright.sync_api import sync_playwright, expect

from helpers import PdfDingE2ETestCase, PdfDingE2ENoLoginTestCase


class UsersE2ETestCase(PdfDingE2ETestCase):
    def test_settings_change_theme(self):
        with sync_playwright() as p:
            self.open(reverse('profile-settings'), p)

            # test that light theme is used
            expect(self.page.locator('html')).not_to_have_attribute('class', 'dark')
            expect(self.page.locator('html')).to_have_attribute('data-theme', 'Green')
            expect(self.page.locator("#theme")).to_contain_text("Light + Green")
            expect(self.page.locator('body')).to_have_css('background-color', 'rgba(0, 0, 0, 0)')
            expect(self.page.locator('header')).to_have_css('background-color', 'rgb(74, 222, 128)')

            # change to dark mode
            self.page.locator("#theme-edit").click()
            # check that selected option is correct
            expect(self.page.locator("#id_dark_mode")).to_have_value("Light")
            expect(self.page.locator("#id_theme_color")).to_have_value("Green")
            self.page.locator("#id_dark_mode").select_option("Dark")
            self.page.locator("#id_theme_color").select_option("Blue")
            self.page.get_by_role("button", name="Submit").click()

            # check that theme was changed to dark
            expect(self.page.locator('html')).to_have_attribute('class', 'dark')
            expect(self.page.locator('html')).to_have_attribute('data-theme', 'Blue')
            expect(self.page.locator("#theme")).to_contain_text("Dark + Blue")
            expect(self.page.locator('body')).to_have_css('background-color', 'rgb(30, 41, 59)')
            expect(self.page.locator('header')).to_have_css('background-color', 'rgb(71, 147, 204)')

            # trigger dropdown again
            self.page.locator("#theme-edit").click()
            # check that selected option is correct
            expect(self.page.locator("#id_dark_mode")).to_have_value("Dark")
            expect(self.page.locator("#id_theme_color")).to_have_value("Blue")

    def test_settings_email_change(self):
        with sync_playwright() as p:
            self.open(reverse('profile-settings'), p)

            # check email address before changing
            expect(self.page.locator('#email-address')).to_contain_text('a@a.com')
            expect(self.page.locator('content')).to_contain_text('Verified')

            # change email address
            self.page.locator('#email-edit').click()
            self.page.locator('#id_email').click()
            self.page.locator('#id_email').press('ControlOrMeta+a')
            self.page.locator('#id_email').fill('a@b.com')
            self.page.get_by_role('button', name='Submit').click()

            # check email address after changing
            expect(self.page.locator('#email-address')).to_contain_text('a@b.com')
            expect(self.page.locator('content')).to_contain_text('Not verified')

    def test_settings_delete(self):
        with sync_playwright() as p:
            self.open(reverse('profile-settings'), p)

            # we just check if delete button is displayed, rest is covered by unit test
            self.page.get_by_role('link', name='Delete').click()
            expect(self.page.get_by_role('button')).to_contain_text('Yes, I want to delete my account')

    def test_settings_edit_cancel(self):
        with sync_playwright() as p:
            self.open(reverse('profile-settings'), p)
            self.page.locator('#email-edit').click()
            expect(self.page.locator('#email-edit')).to_contain_text('Cancel')
            self.page.get_by_role('link', name='Cancel').click()
            expect(self.page.locator('#email-edit')).to_contain_text('Edit')

            self.page.locator('#theme-edit').click()
            expect(self.page.locator('#theme-edit')).to_contain_text('Cancel')
            self.page.get_by_role('link', name='Cancel').click()
            expect(self.page.locator('#theme-edit')).to_contain_text('Edit')

    def test_settings_change_password(self):
        with sync_playwright() as p:
            self.open(reverse('profile-settings'), p)

            # we just check if allauth change password is displayed
            self.page.get_by_role('link', name='Edit').click()
            expect(self.page.get_by_role('button')).to_contain_text('Change Password')

    def test_header_dropdown(self):
        with sync_playwright() as p:
            self.open(reverse('pdf_overview'), p)
            self.page.get_by_role('list').locator('a').nth(2).click()
            expect(self.page.get_by_role('navigation')).to_contain_text('a@a.com')


class UsersLoginE2ETestCase(PdfDingE2ENoLoginTestCase):
    def test_login(self):
        with sync_playwright() as p:
            self.open(reverse('home'), p)
            expect(self.page.get_by_role('heading')).to_contain_text('Sign In')
            self.page.get_by_placeholder('Email address').click()
            self.page.get_by_placeholder('Email address').fill(self.email)
            self.page.get_by_placeholder('Email address').press('Tab')
            self.page.get_by_placeholder('Password').fill(self.password)
            self.page.get_by_role('button', name='Sign In', exact=True).click()
            expect(self.page.locator('body')).to_contain_text('PDFs')

    def test_login_header_normal(self):
        with sync_playwright() as p:
            self.open(reverse('home'), p)
            # login and signup should be displayed if not in oidc only mode
            expect(self.page.get_by_role('navigation')).to_contain_text('Login Signup')

    @override_settings(SOCIALACCOUNT_ONLY=True)
    def test_login_header_oidc_only(self):
        with sync_playwright() as p:
            self.open(reverse('home'), p)
            expect(self.page.get_by_role('navigation')).to_contain_text('Login')
            # signup should not be displayed in oidc only mode
            expect(self.page.get_by_role('navigation')).not_to_contain_text('Signup')

    def test_login_theme(self):
        with sync_playwright() as p:
            self.open(reverse('home'), p)

            # test that light theme is used
            expect(self.page.locator('html')).not_to_have_attribute('class', 'dark')
            expect(self.page.locator('html')).to_have_attribute('data-theme', 'Green')
            expect(self.page.locator('body')).to_have_css('background-color', 'rgba(0, 0, 0, 0)')
            expect(self.page.locator('header')).to_have_css('background-color', 'rgb(74, 222, 128)')
