# 🔐 Credential Generator

A terminal application that automatically detects form fields on any website and generates realistic fake credentials to fill them.

> **Note**: Generated data is fake but realistic-looking. It won't pass services that verify emails/phones via OTP.

## ✨ Features

- 🌐 **URL-based** – Paste any website URL and the tool analyzes its forms
- 🔍 **Smart field detection** – Recognizes 25+ field types (name, email, phone, address, DOB, password, etc.)
- 🎭 **Realistic data** – Uses the Faker library for locale-aware, realistic-looking credentials
- 🔑 **Strong passwords** – Auto-generates secure passwords with configurable complexity
- 📋 **Copy to clipboard** – One-click copy of all generated credentials
- 💾 **Save to JSON** – Export credentials for later reference
- 🌍 **Locale support** – Generate data in different locales (US, India, UK, etc.)
- 🎨 **Beautiful UI** – Rich terminal interface with colored tables and spinners

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/Ayush-Giri/credential_generator.git
cd credential_generator

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Optional: JavaScript-heavy sites

For websites that render forms with JavaScript (React, Angular, etc.):

```bash
pip install playwright
playwright install chromium
```

## 📖 Usage

### Interactive Mode

```bash
python main.py
```

You'll see an interactive prompt where you can paste URLs and get credentials generated instantly.

### Direct URL Mode

```bash
python main.py https://example.com/signup
```

### With Locale

```bash
python main.py https://example.com/signup --locale en_IN
```

Supported locales: `en_US`, `en_IN`, `en_GB`, `de_DE`, `fr_FR`, `ja_JP`, and [many more](https://faker.readthedocs.io/en/master/locales.html).

## 🎯 How It Works

```
URL → Fetch HTML → Parse Forms → Classify Fields → Generate Data → Display
```

1. **Fetch** – Downloads the page HTML (with optional Playwright fallback for SPAs)
2. **Parse** – Extracts all `<form>`, `<input>`, `<select>`, `<textarea>` elements
3. **Classify** – Uses a 4-layer heuristic to identify field types:
   - `autocomplete` attribute
   - Keyword matching on `name`, `id`, `placeholder`, `label`
   - HTML `type` attribute
   - Fallback to generic text
4. **Generate** – Maps each field type to a Faker method for realistic data
5. **Display** – Shows results in a beautiful terminal table

## 🔍 Supported Field Types

| Type | Examples |
|------|----------|
| Name | First name, last name, full name |
| Contact | Email, phone number |
| Auth | Username, password |
| Personal | Age, date of birth, gender |
| Address | Street, city, state, zip, country |
| Professional | Company, job title |
| Financial | Credit card, CVV, expiry |
| Other | Website, SSN, generic text |

## 📁 Project Structure

```
credential_generator/
├── main.py            # CLI entry point & interactive loop
├── scraper.py         # Web page fetching & form extraction
├── classifier.py      # Field type classification
├── generator.py       # Fake data generation
├── models.py          # Data classes & enums
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## 🤝 Contributing

Pull requests are welcome! Feel free to open issues for bugs or feature requests.

## ⚠️ Disclaimer

This tool generates **fake data** for testing and development purposes only. Do not use it for:
- Identity fraud or impersonation
- Violating any website's Terms of Service
- Any illegal activity

Use responsibly and ethically.
