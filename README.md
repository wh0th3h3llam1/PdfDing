# PdfDing
<hr>

## Introduction
<hr>

PdfDing is a browser based PDF viewer that you can host yourself. It's designed be to be minimal, fast, and easy to 
set up using Docker. 

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
* Remembers current position - continue where you stopped reading
* SSO support via OIDC
* Every user can upload its own PDFs. There is no admin curating the content.

### Video


## Installation
<hr>

## Acknowledements
* This project started by adjusting the django starter of Andreas Jud: [django-starter](https://github.com/andyjud/django-starter), [django-starter-assets](https://github.com/andyjud/django-starter-assets)
* As mentioned above, inspired by [linkding](https://github.com/sissbruecker/linkding).