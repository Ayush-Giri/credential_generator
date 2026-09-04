# Credential Generator

A terminal command that generates fake credentials for any website. Just run `generate <url>` — it detects the form fields and fills them instantly.

## Demo

```
$ generate https://market.tutorialspoint.com/signup.jsp?v=1.0

                       Credentials for
     https://market.tutorialspoint.com/signup.jsp?v=1.0
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                    ┃ Value                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ First Name               │ Marisa                         │
│ Last Name                │ Glenn                          │
│ E-mail Address           │ williamglenn@example.org       │
│ Enter your Mobile number │ 412.669.0641                   │
│ Enter Password           │ +WMue4gpM5vF+QFy               │
│ Confirm Password         │ +WMue4gpM5vF+QFy               │
└──────────────────────────┴────────────────────────────────┘
```

```
$ generate https://parabank.parasoft.com/parabank/register.htm

                       Credentials for
     https://parabank.parasoft.com/parabank/register.htm
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                    ┃ Value                          ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ customer.firstName       │ David                          │
│ customer.lastName        │ Garcia                         │
│ customer.address.street  │ 9850 Richardson Brook Apt. 422 │
│ customer.address.city    │ Erikhaven                      │
│ customer.address.state   │ Arkansas                       │
│ customer.address.zipCode │ 80207                          │
│ customer.phoneNumber     │ (786)889-4297x11375            │
│ customer.ssn             │ 361-60-0168                    │
│ customer.username        │ ashleywalsh                    │
│ customer.password        │ Ly^9=rwSqm*VKQ2o               │
│ repeatedPassword         │ Ly^9=rwSqm*VKQ2o               │
└──────────────────────────┴────────────────────────────────┘
```

## Tested On

| Website | Fields Detected | Status |
|---------|----------------|--------|
| [TutorialsPoint Market Signup](https://market.tutorialspoint.com/signup.jsp?v=1.0) | First Name, Last Name, Email, Phone, Password, Confirm Password | Works |
| [Parabank Register](https://parabank.parasoft.com/parabank/register.htm) | Name, Address, City, State, Zip, Phone, SSN, Username, Password, Confirm Password | Works |
| [TutorialsPoint Selenium Practice](https://www.tutorialspoint.com/selenium/practice/register.php) | First Name, Last Name, Username, Password | Works |
| [Tumblr Register](https://www.tumblr.com/register) | Email, Password | Works |
| [Herokuapp Login](https://the-internet.herokuapp.com/login) | Username, Password | Works |
| [ExpandTesting Login](https://practice.expandtesting.com/login) | Username, Password | Works |
| [httpbin Forms](https://httpbin.org/forms/post) | Customer Name, Telephone, Email, Delivery Time, Instructions | Works |
| [DummyTicket](https://www.dummyticket.com/dummy-ticket-for-visa-application/) | Name, DOB, Cities, Phone, Email, Address, Zip | Works |
| [Automation Exercise](https://automationexercise.com/signup) | Email, Password | Works |

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
generate https://parabank.parasoft.com/parabank/register.htm
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
| **Auth** | Password, confirm password (always matching) |
| **Location** | Full address, street, city, state, zip code, country |
| **Professional** | Company, job title, website |
| **Financial** | Credit card number, CVV, expiry date, SSN |

## What It Skips

The tool only generates values for fields where you actually type. It automatically skips:

- Checkboxes and radio buttons
- File upload fields
- Dropdown menus (select)
- Hidden fields and CSRF tokens
- Submit/reset buttons
- Fields with no identifiable name, id, or label

## How It Works

```
URL -> Fetch HTML -> Find <form> tags -> Classify fields -> Generate fake data -> Display
```

1. **Fetches** the page HTML
2. **Parses** all `<form>`, `<input>`, `<textarea>` elements
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
