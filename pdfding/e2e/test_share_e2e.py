from django.urls import reverse
from helpers import PdfDingE2ETestCase, cancel_delete_helper
from pdf.models import Pdf, SharedPdf
from playwright.sync_api import expect, sync_playwright


class NoSharedPdfE2ETestCase(PdfDingE2ETestCase):
    def test_shared_pdf_overview_no_shared_pdfs(self):
        with sync_playwright() as p:
            self.open(reverse('shared_pdf_overview'), p)
            expect(self.page.locator("body")).to_contain_text("You have not shared any PDFs yet")

    def test_add_pdf(self):
        Pdf.objects.create(owner=self.user.profile, name='some_pdf', description='description')

        with sync_playwright() as p:
            self.open(reverse('pdf_overview'), p)

            self.page.get_by_role("link", name="Share", exact=True).click()
            self.page.get_by_placeholder("Add Share Name").click()
            self.page.get_by_placeholder("Add Share Name").fill("some_shared_pdf")
            self.page.get_by_placeholder("Add a private description").click()
            self.page.get_by_placeholder("Add a private description").fill("some_description")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#shared-pdf-link-1")).to_contain_text("some_shared_pdf")
            expect(self.page.locator("body")).to_contain_text("some_pdf | some_description")
            expect(self.page.locator("body")).to_contain_text("Deleted in 1 hour |")


class PdfE2ETestCase(PdfDingE2ETestCase):
    def setUp(self, login: bool = True) -> None:
        super().setUp()

        self.pdf = Pdf.objects.create(owner=self.user.profile, name='some_pdf', description='some_description')

    def test_sort(self):
        # create some shared pdfs
        for name in ['Some_share', 'another_share', 'this is a share', 'PDF is shared']:
            SharedPdf.objects.create(owner=self.user.profile, name=name, pdf=self.pdf)

        with sync_playwright() as p:
            self.open(f"{reverse('shared_pdf_overview')}?sort=title_desc", p)

            expect(self.page.locator("#shared-pdf-link-1")).to_have_text("this is a share")
            expect(self.page.locator("#shared-pdf-link-2")).to_have_text("Some_share")
            expect(self.page.locator("#shared-pdf-link-3")).to_have_text("PDF is shared")
            expect(self.page.locator("#shared-pdf-link-4")).to_have_text("another_share")

    def test_delete(self):
        SharedPdf.objects.create(owner=self.user.profile, name='some_shared_pdf', pdf=self.pdf)

        with sync_playwright() as p:
            self.open(f"{reverse('shared_pdf_overview')}", p)

            expect(self.page.locator("#shared-pdf-link-1")).to_have_text("some_shared_pdf")
            self.page.get_by_role("button", name="Delete").click()
            self.page.get_by_text("Confirm").click()

            expect(self.page.locator("body")).to_contain_text("You have not shared any PDFs yet")

    def test_cancel_delete(self):
        SharedPdf.objects.create(owner=self.user.profile, name='some_shared_pdf', pdf=self.pdf)

        with sync_playwright() as p:
            self.open(f"{reverse('shared_pdf_overview')}", p)

            cancel_delete_helper(self.page)

    def test_details(self):
        shared_pdf = SharedPdf.objects.create(
            owner=self.user.profile, name='some_shared_pdf', description="some_description", pdf=self.pdf
        )
        shared_pdf.views = 1001
        shared_pdf.save()

        with sync_playwright() as p:
            self.open(reverse('shared_pdf_details', kwargs={'identifier': shared_pdf.id}), p)

            expect(self.page.locator("content")).to_contain_text("some_shared_pdf")
            expect(self.page.locator("#name")).to_contain_text("some_shared_pdf")
            expect(self.page.locator("content")).to_contain_text(f"pdf/shared/{shared_pdf.id}")
            expect(self.page.locator("#description")).to_contain_text("some_description")
            expect(self.page.locator("#pdf")).to_contain_text("some_pdf")
            expect(self.page.locator("content")).to_contain_text("1001")

    def test_change_details(self):
        shared_pdf = SharedPdf.objects.create(
            owner=self.user.profile, name='some_shared_pdf', description="some_description", pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(reverse('shared_pdf_details', kwargs={'identifier': shared_pdf.id}), p)

            self.page.locator("#name-edit").click()
            self.page.locator("#id_name").dblclick()
            self.page.locator("#id_name").fill("other name")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("content")).to_contain_text("other name")
            expect(self.page.locator("#name")).to_contain_text("other name")
            self.page.locator("#description-edit").click()
            self.page.get_by_text("some_description").click()
            self.page.get_by_text("some_description").fill("other description")
            self.page.get_by_role("button", name="Submit").click()
            expect(self.page.locator("#description")).to_contain_text("other description")

    def test_cancel_change_details(self):
        shared_pdf = SharedPdf.objects.create(
            owner=self.user.profile, name='some_shared_pdf', description="some_description", pdf=self.pdf
        )

        with sync_playwright() as p:
            self.open(reverse('shared_pdf_details', kwargs={'identifier': shared_pdf.id}), p)

            for edit_name in ['#name-edit', '#description-edit']:
                expect(self.page.locator(edit_name)).to_contain_text("Edit")
                self.page.locator(edit_name).click()
                expect(self.page.locator(edit_name)).to_contain_text("Cancel")
                self.page.get_by_role("link", name="Cancel").click()
                expect(self.page.locator(edit_name)).to_contain_text("Edit")

    def test_details_delete(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, name='some_shared_pdf', pdf=self.pdf)

        with sync_playwright() as p:
            self.open(reverse('shared_pdf_details', kwargs={'identifier': shared_pdf.id}), p)

            self.page.get_by_role("button", name="Delete").click()
            self.page.get_by_text("Confirm").click()

            expect(self.page.locator("body")).to_contain_text("You have not shared any PDFs yet")

    def test_details_cancel_delete(self):
        shared_pdf = SharedPdf.objects.create(owner=self.user.profile, name='some_shared_pdf', pdf=self.pdf)

        with sync_playwright() as p:
            self.open(reverse('shared_pdf_details', kwargs={'identifier': shared_pdf.id}), p)

            cancel_delete_helper(self.page)
