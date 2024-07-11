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
<hr>

### Admin user

## Configuration

| Name                            | Description                                                                               | Default / Example                                           |
|---------------------------------|-------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| `SECRET_KEY`                    | This value is the key to securing signed data. (Should be a large random value.)          | `long_secret`                                               |
| `HOST_NAME`                     | The host/domain name where PdfDing will be reachable                                      | `pdfding.com`                                               |
| `DATABASE_TYPE`                 | Specify which database type should be used                                                | `SQLITE` (or `POSTGRES`)                                    |
| `POSTGRES_PASSWORD`             | The password for the postgres db                                                          | `password`                                                  |
| `POSTGRES_PORT`                 | The port of the postgres db                                                               | `5432`                                                      |
| `ACCOUNT_EMAIL_VERIFICATION`    | Block users until they have verified their email address                                  | `TRUE` (or `FALSE`)                                         |
| `CSRF_COOKIE_SECURE`            | Set this to True to avoid transmitting the CSRF cookie over HTTP accidentally.            | `TRUE` (or `FALSE`)                                         |
| `SESSION_COOKIE_SECURE`         | Set this to True to avoid transmitting the session cookie over HTTP accidentally.         | `TRUE` (or `FALSE`)                                         |
| `OIDC_CLIENT_ID`                | PdfDing's OIDC client id. By setting this value OIDC will be activated.                   | `pdfding`                                                   |
| `OIDC_CLIENT_SECRET`            | PdfDing's OIDC client secret. (Should be a large random value.)                           | `long_secret`                                               |
| `OIDC_AUTH_URL`                 | Set this to True to avoid transmitting the session cookie over HTTP accidentally.         | `https://auth.pdfding.com/.well-known/openid-configuration` |
| `OIDC_ONLY`                     | By setting this to `TRUE` users will only be able to authenticate using OIDC              | `FALSE` (or `TRUE`)                                         |
| `ACCOUNT_DEFAULT_HTTP_PROTOCOL` | The default protocol for account related URLs, e.g. for the password forgotten procedure. | `https` (or `http`)                                         |


## Tech Stack
* The web app is build using the Python web framework [Django](https://www.djangoproject.com/)
* Mozilla's [PDF.js](https://mozilla.github.io/pdf.js/) is used for viewing PDF files in the browser
* The frondend is build using [Alpine.js](https://alpinejs.dev/), [htmx](https://htmx.org/),
[jQuery](https://jquery.com/) and [Tailwind CSS](https://tailwindcss.com/)
* Authentication, registration, account management and OIDC is achieved by [django-allauth](https://docs.allauth.org/en/latest/)

## Acknowledements
* This project started by adjusting the django starter of Andreas Jud: [django-starter](https://github.com/andyjud/django-starter), [django-starter-assets](https://github.com/andyjud/django-starter-assets)
* As mentioned above, inspired by [linkding](https://github.com/sissbruecker/linkding).