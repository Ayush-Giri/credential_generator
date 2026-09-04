"""Quick smoke test – run the pipeline against a known HTML form."""

import sys
sys.path.insert(0, ".")

from scraper import extract_forms
from classifier import classify_fields
from generator import generate_credentials

# A form with checkboxes, radios, confirm password, and regular fields
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

  <label for="password">Password</label>
  <input type="password" id="password" name="password" required>

  <label for="confirm_password">Confirm Password</label>
  <input type="password" id="confirm_password" name="confirm_password" required>

  <label for="gender">Gender</label>
  <select id="gender" name="gender">
    <option value="">Select...</option>
    <option value="male">Male</option>
    <option value="female">Female</option>
  </select>

  <!-- These should be SKIPPED -->
  <input type="checkbox" name="terms" id="terms"> I agree to terms
  <input type="checkbox" name="newsletter" id="newsletter"> Subscribe
  <input type="radio" name="plan" value="free"> Free
  <input type="radio" name="plan" value="pro"> Pro
  <input type="file" name="avatar" id="avatar">
  <input type="hidden" name="csrf" value="abc123">
  <input type="submit" value="Sign Up">
</form>
</body></html>
"""

def test():
    forms = extract_forms(SAMPLE_HTML)
    assert len(forms) == 1, f"Expected 1 form, got {len(forms)}"

    fields = forms[0]
    print(f"Extracted {len(fields)} fields (should be 7, no checkboxes/radios/file/hidden/submit)")
    assert len(fields) == 7, f"Expected 7 fields, got {len(fields)}"

    # Verify no checkbox/radio/file fields leaked through
    for f in fields:
        assert f.input_type not in ("checkbox", "radio", "file", "hidden", "submit"), \
            f"Non-writable field leaked through: {f.name} (type={f.input_type})"
    print("PASS: No checkboxes, radios, or file inputs in results")

    classified = classify_fields(fields)
    print("\\n--- Classified Fields ---")
    for cf in classified:
        print(f"  {cf.display_name:20s} -> {cf.semantic_type.name}")

    creds = generate_credentials(classified)
    print("\\n--- Generated Credentials ---")
    for k, v in creds.items():
        print(f"  {k:20s} : {v}")

    # Verify password and confirm password match
    pw = creds.get("Password")
    cpw = creds.get("Confirm Password")
    assert pw is not None, "Password field not found in results"
    assert cpw is not None, "Confirm Password field not found in results"
    assert pw == cpw, f"Password mismatch: '{pw}' != '{cpw}'"
    print(f"\\nPASS: Password and Confirm Password match: {pw}")

    print("\\nAll tests passed!")

if __name__ == "__main__":
    test()
