# Changelog
<hr>

## 0.3.0 - Periodic Backups to S3 Compatible Storage (Aug 03, 2024)
<hr>

* Add periodic backups to S3 compatible storage

## 0.2.0 - New Admin Area (Jul 27, 2024)
<hr>

* Add new Admin Area - admins can delete users and grant + remove admin rights
* Remove standard Django Admin Area
* Add `OIDC_ENABLE` environment variable for enabling SSO via OIDC

### Breaking Changes

* In order to use SSO via OIDC the environment variable `OIDC_ENABLE` needs to be set to `TRUE`.
  For more information refer to the [configuration](https://codeberg.org/mrmn/PdfDing#configuration) section of the README.

## 0.1.2 - Colored Themes (Jul 24, 2024)
<hr>

* Add theme colors
* Add view counter for PDFs
* Change profile icon



## 0.1.1 - Dark Mode (Jul 15, 2024)
<hr>

* Add dark mode
* Update dependencies

## 0.1.0 - Initial Release (Jul 13, 2024)
<hr>

* Browser based PDF viewing
* Organize PDFs with tags
* Clean and responsive UI Remembers current position - continue where you stopped reading
* SSO support via OIDC
* Every user can upload its own PDFs. There is no admin curating the content.
