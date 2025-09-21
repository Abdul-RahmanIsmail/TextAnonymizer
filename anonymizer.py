import re
from faker import Faker
fake = Faker()


def anonymize_text(original, entities, selected_labels, style="*****", use_faker=False):
    # ===== 1) فلترة كيانات NER =====
    detected_entities = [e for e in entities if e["entity_group"] in selected_labels]

    # ===== 2) اكتشاف البريد الإلكتروني ورقم الهاتف حسب اختيار المستخدم =====
    if "EMAIL" in selected_labels:
        pattern_email = r'[\w\.-]+@[\w\.-]+\.\w+'
        for match in re.finditer(pattern_email, original):
            detected_entities.append({
                "entity_group": "EMAIL",
                "start": match.start(),
                "end": match.end(),
                "word": match.group(0)
            })

    if "PHONE" in selected_labels:
        pattern_phone = r'(\+?\d[\d\-\s]{7,}\d)'
        for match in re.finditer(pattern_phone, original):
            detected_entities.append({
                "entity_group": "PHONE",
                "start": match.start(),
                "end": match.end(),
                "word": match.group(0)
            })

    # ===== 3) ترتيب الكيانات =====
    detected_entities.sort(key=lambda e: e["start"])

    # ===== 4) بناء النص المعمّى =====
    out, last = [], 0
    for e in detected_entities:
        out.append(original[last:e["start"]])
        if use_faker:
            if e["entity_group"] == "PER":
                out.append(fake.name())
            elif e["entity_group"] == "LOC":
                out.append(fake.city())
            elif e["entity_group"] == "ORG":
                out.append(fake.company())
            elif e["entity_group"] == "EMAIL":
                out.append(fake.email())
            elif e["entity_group"] == "PHONE":
                out.append(fake.phone_number())
            else:
                out.append(style)
        else:
            out.append(style)
        last = e["end"]
    out.append(original[last:])
    return "".join(out)
