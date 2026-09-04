"""Quick smoke test – run the pipeline against a known HTML form."""

import sys
sys.path.insert(0, ".")

from scraper import extract_forms
from classifier import classify_fields
from generator import generate_credentials

# A minimal signup form HTML
SAMPLE_HTML = """
<html><body>
<form action="/signup" method="post">
  <label for="fname">First Name</label>
  <input type="text" id="fname" name="first_name" placeholder="Enter first name" required>

  <label for="lname">Last Name</label>
  <input type="text" id="lname" name="last_name" placeholder="Enter last name" required>

  <label for="email">Email Address</label>
  <input type="email" id="email" name="email" placeholder="you@example.com" required>

  <label for="phone">Phone Number</label>
  <input type="tel" id="phone" name="phone" placeholder="+1 (555) 000-0000">

  <label for="dob">Date of Birth</label>
  <input type="date" id="dob" name="dob">

  <label for="password">Password</label>
  <input type="password" id="password" name="password" required>

  <label for="gender">Gender</label>
  <select id="gender" name="gender">
    <option value="">Select...</option>
    <option value="male">Male</option>
    <option value="female">Female</option>
    <option value="other">Other</option>
  </select>

  <label for="address">Address</label>
  <textarea id="address" name="address" placeholder="Enter your full address"></textarea>

  <label for="age">Age</label>
  <input type="number" id="age" name="age" placeholder="25">

  <label for="username">Username</label>
  <input type="text" id="username" name="username" placeholder="Choose a username">

  <label for="company">Company</label>
  <input type="text" id="company" name="company" placeholder="Your company">

  <label for="website">Website</label>
  <input type="url" id="website" name="website" placeholder="https://example.com">

  <input type="submit" value="Sign Up">
</form>
</body></html>
"""

def test():
    forms = extract_forms(SAMPLE_HTML)
    assert len(forms) == 1, f"Expected 1 form, got {len(forms)}"

    fields = forms[0]
    print(f"✓ Extracted {len(fields)} fields")

    classified = classify_fields(fields)
    print("\\n--- Classified Fields ---")
    for cf in classified:
        print(f"  {cf.display_name:20s} → {cf.semantic_type.name}")

    creds = generate_credentials(classified)
    print("\\n--- Generated Credentials ---")
    for k, v in creds.items():
        print(f"  {k:20s} : {v}")

    print("\\n✅ All tests passed!")

if __name__ == "__main__":
    test()
