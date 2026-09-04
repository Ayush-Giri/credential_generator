# Credential Generator

A terminal command that generates fake credentials for any website. Just run `generate <url>` — it detects the form fields and fills them instantly.

## Demo

```
$ generate https://www.tutorialspoint.com/selenium/practice/register.php

      Credentials for https://www.tutorialspoint.com/...
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field              ┃ Value                          ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ First Name         │ Jennifer                       │
│ lastname           │ Smith                          │
│ UserName           │ ebean                          │
│ Password           │ Z-*xzM4so&UDHRne               │
└────────────────────┴────────────────────────────────┘
```

## Installation

```bash
git clone https://github.com/Ayush-Giri/credential_generator.git
cd credential_generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then add the command to your PATH — add this line to your `~/.zshrc` (or `~/.bashrc`):

```bash
export PATH="$HOME/Documents/credential_generator/bin:$PATH"
```

Restart your terminal and you're good to go.

## Usage

```bash
generate <url>
```

That's it. Some examples:

```bash
generate https://www.tumblr.com/register
generate https://the-internet.herokuapp.com/login
generate https://www.tutorialspoint.com/selenium/practice/register.php
```

### Options

| Flag | What it does | Example |
|------|-------------|---------|
| `--locale` | Generate region-specific data (Indian names, phones, etc.) | `generate <url> --locale en_IN` |
| `--json` | Output as JSON instead of a table | `generate <url> --json` |

### Supported Locales

`en_US` (default), `en_IN`, `en_GB`, `de_DE`, `fr_FR`, `ja_JP`, and [many more](https://faker.readthedocs.io/en/master/locales.html).

## What It Detects

The tool recognizes **25+ field types** automatically:

| Category | Fields |
|----------|--------|
| **Identity** | First name, last name, full name, username, gender, age, date of birth |
| **Contact** | Email, phone number |
| **Auth** | Password |
| **Location** | Full address, street, city, state, zip code, country |
| **Professional** | Company, job title, website |
| **Financial** | Credit card number, CVV, expiry date, SSN |

## How It Works

```
URL -> Fetch HTML -> Find <form> tags -> Classify fields -> Generate fake data -> Display
```

1. **Fetches** the page HTML
2. **Parses** all `<form>`, `<input>`, `<select>`, `<textarea>` elements
3. **Classifies** each field using keyword matching on `name`, `id`, `placeholder`, `label`, and `autocomplete` attributes
4. **Generates** realistic fake data using [Faker](https://github.com/joke2k/faker)
5. **Displays** results in a clean terminal table

## Limitations

- **JavaScript-rendered forms** (React, Angular, Vue SPAs) won't be detected with the default setup. Install Playwright for those:
  ```bash
  pip install playwright
  playwright install chromium
  ```
- **Sites that block scrapers** (GitHub, StackOverflow, Facebook) will return errors — they require browser authentication or CAPTCHA
- Generated data is **fake but realistic-looking**. It won't pass OTP verification or email confirmation

## Project Structure

```
credential_generator/
├── bin/generate       # CLI command (add to PATH)
├── main.py            # Entry point
├── scraper.py         # Fetches pages & extracts form fields
├── classifier.py      # Detects field types via keyword matching
├── generator.py       # Generates fake data using Faker
├── models.py          # Data classes & enums
├── test_smoke.py      # Smoke test
└── requirements.txt   # Dependencies
```

## Disclaimer

This tool generates **fake data** for testing and development purposes only. Do not use it for identity fraud, violating any website's Terms of Service, or any illegal activity. Use responsibly.
