# PdfDing
<hr>

## Overview

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuration](#configuration)
- [Tech Stack](#tech-stack)
- [Acknowledements](#acknowledements)

## Introduction
<hr>

PdfDing is a browser based PDF viewer that you can host yourself. It's designed be to be minimal, fast, and easy to 
set up using Docker. 
[base.html](pdfding%2Ftemplates%2Fbase.html)
PdfDing was created because I was searching for a selfhostable browser based PDF viewer. However, the existing solution
were (at least for my use case) too heavy and feature rich. Thus, I focused on making PDfDing a "simple" with a focus on
a single thing: viewing PDFs. This is also why you won't find any fancy AI or OCR in this project.

The name is a combination of PDF and *ding*. Ding is the German word for thing. Thus, PdfDing is a thing for
your PDFs. The name and the design of PdfDing are inspired by [linkding](https://github.com/sissbruecker/linkding).
Linkding is an excellent selfhostable bookmark manager. If you are unfamiliar with it be sure to check it out!

### Feature Overview
* Browser based PDF viewing
* Organize PDFs with tags
* Clean and responsive UI
Remembers current position - continue where you stopped reading
* SSO support via OIDC
* Every user can upload its own PDFs. There is no admin curating the content.

### Demo Video
![Demo gif](demo.gif)

## Installation
PdfDing is designed to be run with container solutions like Docker. The Docker image is compatible with ARM platforms,
so it can be run on a Raspberry Pi.

PdfDing uses an SQLite database by default. Alternatively PdfDing supports PostgreSQL.

### Using Docker Compose
To install linkding using Docker Compose, you can use one of the files in the
[deploy](https://codeberg.org/mrmn/PdfDing/src/branch/master/deploy) directory and running
e.g. `docker-compose -d -f sqlite.docker-compose.yaml`

### Admin user
If needed or wished it is possible to create an admin user. The admin user can view + delete users and pdfs at the
`/admin` path.

To give an user admin rights execute
`python pdfding/manage.py make_admin -e admin@pdfding.com` with the appropriate email address.

## Configuration
### `SECRET_KEY` 
Values: `string` | Default = None

This value is the key to securing signed data. Should be to a large random value! Example: `some_secret`

### `HOST_NAME`  
Values: `string` | Default = None

The host/domain name where PdfDing will be reachable. Example: `pdfding.com`   

### `HOST_PORT`
Values: `integer` | Default: `8000`

Allows to set a custom port for the PdfDing server. 

### `DATABASE_TYPE` 
Values: `SQLITE`, `POSTGRES` | Default `POSTGRES`

Specify which database type should be used.
### `POSTGRES_PASSWORD` 
Values: `string` | Default = None

The password for the postgres DB: Example: `password`
### `POSTGRES_PORT` 
Values: `integer` | Default: `5432`

The port of the postgres DB.

### `ACCOUNT_EMAIL_VERIFICATION`  
Values: `TRUE`, `FALSE` | Default: `TRUE`

Block users until they have verified their email address.

### `OIDC_CLIENT_ID`   
Values: `string` | Default = None

PdfDing's OIDC client id. By setting this value OIDC will be activated. Example: `pdfding`

### `OIDC_CLIENT_SECRET`   
Values: `string` | Default = None

PdfDing's OIDC client secret. Should be a large random value! Example: `another_long_secret`

### `OIDC_AUTH_URL`  
Values: `string` | Default = None

The URL to the OpenID configuration of the auth server. Example: 
`https://auth.pdfding.com/.well-known/openid-configuration`

### `OIDC_ONLY`   
Values: `TRUE`, `FALSE` | Default: `TRUE`

By setting this to `TRUE` users will only be able to authenticate using OIDC.

### `CSRF_COOKIE_SECURE`   
Values: `TRUE`, `FALSE` | Default: `TRUE`

Set this to True to avoid transmitting the CSRF cookie over HTTP accidentally.

### `SESSION_COOKIE_SECURE`  
Values: `TRUE`, `FALSE` | Default: `TRUE`

Set this to True to avoid transmitting the session cookie over HTTP accidentally. 

### `SECURE_SSL_REDIRECT`  
Values: `FALSE`, `TRUE` | Default: `FALSE`

Redirects all non-HTTPS requests to HTTPS. If PdfDing is running behind a reverse proxy this can cause infinite 
redirects.

### `SECURE_HSTS_SECONDS`
Values: `integer` | Default: None

For sites that should only be accessed over HTTPS, you can instruct modern browsers to refuse to connect to your domain
name via an insecure connection (for a given period of time) by setting the “Strict-Transport-Security” header. 
`SECURE_HSTS_SECONDS` will set this header for you on all HTTPS responses for the specified number of seconds. Test this
with a small value first. If everything works it can be set to a large value, e.g. `31536000` (1 year) , in order to
protect infrequent visitors.

### `ACCOUNT_DEFAULT_HTTP_PROTOCOL`
Values: `https`, `http` | Default: `https`

The default protocol for account related URLs, e.g. for the password forgotten procedure.

### `EMAIL_BACKEND `
Values: `CONSOLE`, `SMTP` | Default: `CONSOLE`

Whether to send account related emails, e.g a password reset or account verification, to the console or via an SMTP
server.

### `SMTP_HOST`
Values: `string` | Default = None

The host/domain name of the SMTP server. Example: `pdfding.com`

### `SMTP_PORT`
Values: `integer` | Default: `587`

The port of the SMTP server.

### `SMTP_USER`
Values: `string` | Default = None

The username used for logging into the SMTP server.

### `SMTP_PASSWORD`
Values: `string` | Default = None

The password used for logging into the SMTP server.

### `SMTP_USE_TLS`
Values: `FALSE`, `TRUE` | Default: `FALSE`

Secure the connection to the SMTP server with TLS. Some SMTP servers support only one kind and
some support both.

### `EMAIL_USE_SSL`
Values: `FALSE`, `TRUE` | Default: `FALSE`

Secure the connection to the SMTP server with SSL. Some SMTP servers support only one kind and
some support both.



## Tech Stack
* The web app is build using the Python web framework [Django](https://www.djangoproject.com/)
* Mozilla's [PDF.js](https://mozilla.github.io/pdf.js/) is used for viewing PDF files in the browser
* The frondend is build using [Alpine.js](https://alpinejs.dev/), [htmx](https://htmx.org/),
[jQuery](https://jquery.com/) and [Tailwind CSS](https://tailwindcss.com/)
* Authentication, registration, account management and OIDC is achieved by [django-allauth](https://docs.allauth.org/en/latest/)

## Acknowledements
* This project started by adjusting the django starter of Andreas Jud: [django-starter](https://github.com/andyjud/django-starter), [django-starter-assets](https://github.com/andyjud/django-starter-assets)
* As mentioned above, inspired by [linkding](https://github.com/sissbruecker/linkding).