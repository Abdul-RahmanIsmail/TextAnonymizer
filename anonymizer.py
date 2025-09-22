import re
from faker import Faker

fake = Faker()


def anonymize_text(
    original, entities, selected_labels, model_name, style="*****", use_faker=False
):
    # تصفية الكيانات التي وجدها النموذج، مع تحديد فقط ما طله المستخدم
    detected_entities = [e for e in entities if e["entity_group"] in selected_labels]

    # التحقق مما إذا كان المستخدم يرغب في تعمية البريد الإلكتروني.
    if "EMAIL" in selected_labels:
        # ألبريد الألكتروني pattern تعريف .
        pattern_email = r"[\w\.-]+@[\w\.-]+\.\w+"

        # البحث عن كل بريد يحقق النمط.
        for match in re.finditer(pattern_email, original):
            # إضافة كل ما يطابق إلى قائمة الكيانات التي سيتم تعميتها.
            detected_entities.append(
                {
                    "entity_group": "EMAIL",  # تعيين نوع الكيان.
                    "start": match.start(),  # تحديد بداية الكيان.
                    "end": match.end(),  # تحديد نهاية الكيان.
                    "word": match.group(0),  # استخراج النص الفعلي للكيان.
                }
            )

    # التحقق إذا كان المستخدم يرغب في تعمية أرقام الهاتف.
    if "PHONE" in selected_labels:
        # الخاص برفم الهاتف pattern تعريف .
        pattern_phone = r"(\+?\d[\d\-\s]{7,}\d)"
        # البحث عن كل أرقام الهواتف في النص.
        for match in re.finditer(pattern_phone, original):
            # إضافة كل رقم هاتف إلى قائمة الكيانات.
            detected_entities.append(
                {
                    "entity_group": "PHONE",
                    "start": match.start(),
                    "end": match.end(),
                    "word": match.group(0),
                }
            )

    # فرز الكيانات حسب موقعها في النص لكي لا تتداخل التعمية.
    detected_entities.sort(key=lambda e: e["start"])

    # --------------------- تعمية النص ---------------------#

    # out: لتخزين الأجزاء
    # last: لتتبع آخر موضع تمت معالجته.
    out, last = [], 0
    # المرور على كل كيان تم تحديده.
    for e in detected_entities:
        # إضافة جزء النص الذي يسبق الكيان.
        out.append(original[last : e["start"]])

        # Faker التحقق إذا كان سيتم استخدام.
        if use_faker:
            # Faker استبدال الكيان بنوع بيانات وهمية مناسب من
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
                out.append(
                    style
                )  # [REDACTED] او [XXXX] في حالة عدم وجود نوع محدد، نستخدم النص الذي ادخله المستخدم مثل
        else:
            out.append(
                style
            )  # Faker استبدال استخدام نمط التعمية المحدد من قبل المستخدم اذا لم يستخدم
        # تحديث آخر موضع تمت معالجته.
        last = e["end"]
    # إضافة الجزء الأخير من النص بعد آخر كيان.
    out.append(original[last:])
    # دمج الأجزاء في نص واحد.
    return "".join(out)
