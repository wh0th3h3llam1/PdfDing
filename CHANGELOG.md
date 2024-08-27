# Changelog
<hr>

## 0.3.4 - Encrypted Backups to S3 Compatible Storage  (Aug 27, 2024)

* Add option to encrypt the PDFs and the Sqlite database when performing backups
* Bug Fix: Setting the Postgres host to something different from `postgres` was not possible beforehand

## 0.3.3 - Revamp tag sidebar, new version available and further image size reduction (Aug 17, 2024)

* Revamp the tag sidebar section, so that tags will be grouped by their starting character
* Add a new version available banner in admin section
* Further image size reduction by over 30% by switching to alpine
* Update dependencies

## 0.3.2 - Fix backup functionality (Aug 11, 2024)

* Fix backup functionality by re-adding setuptools to virtual environment

## 0.3.1 - Reduce image size and add PDFs per page setting (Aug 11, 2024)

* Reduce image size by almost 20%
* Add PDFs per page setting: control how many PDFs are shown in the PDF overview

### Bug introduced
* removing setuptools from virtual environment broke backup functionality


## 0.3.0 - Periodic Backups to S3 Compatible Storage (Aug 03, 2024)

* Add periodic backups to S3 compatible storage

## 0.2.0 - New Admin Area (Jul 27, 2024)

* Add new Admin Area - admins can delete users and grant + remove admin rights
* Remove standard Django Admin Area
* Add `OIDC_ENABLE` environment variable for enabling SSO via OIDC

### Breaking Changes

* In order to use SSO via OIDC the environment variable `OIDC_ENABLE` needs to be set to `TRUE`.
  For more information refer to the [configuration](https://codeberg.org/mrmn/PdfDing#configuration) section of the README.

## 0.1.2 - Colored Themes (Jul 24, 2024)

* Add theme colors
* Add view counter for PDFs
* Change profile icon



## 0.1.1 - Dark Mode (Jul 15, 2024)

* Add dark mode
* Update dependencies

## 0.1.0 - Initial Release (Jul 13, 2024)

* Browser based PDF viewing
* Organize PDFs with tags
* Clean and responsive UI Remembers current position - continue where you stopped reading
* SSO support via OIDC
* Every user can upload its own PDFs. There is no admin curating the content.
