def normalize_phone_lib(phone: str) -> str:
    import phonenumbers
    
    parsed = phonenumbers.parse(phone, "VN")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone")

    # format về quốc tế
    e164 = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )

    # đổi về 0xxxxxxxx
    return "0" + e164[3:]
