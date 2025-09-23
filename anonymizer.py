import re  # (Regular Expressions) لاستخدام التعبيرات العادية
from faker import Faker  # لإنشاء بيانات وهمية تبدو طبيعية

fake = Faker()


def anonymize_text(
    original, entities, selected_labels, model_name, style="*****", use_faker=False
):
    """
    يقوم بتعمية النص بناءً على الكيانات المكتشفة والنموذج المستخدم.

    Args:
        original (str): النص الأصلي.
        entities (list): قائمة الكيانات المكتشفة من النموذج.
        selected_labels (list): قائمة الفئات التي اختارها المستخدم للتعمية.
        model_name (str): اسم النموذج المستخدم ("bert-base" أو "zero-shot").
        style (str): النمط المستخدم للاستبدال إذا لم يتم استخدام Faker.
        use_faker (bool): هل يتم استخدام مكتبة Faker للاستبدال.

    Returns:
        str: النص المعمّى.
    """
    detected_entities = []

    if model_name == "bert-base":
        #  BERT base من نموذج NER معالجة كيانات
        # تصفية الكيانات التي وجدها النموذج، مع تحديد فقط ما طلبه المستخدم
        detected_entities = [
            e for e in entities if e["entity_group"] in selected_labels
        ]

        #  Regex اكتشاف البريد الإلكتروني ورقم الهاتف باستخدام
        if "EMAIL" in selected_labels:
            # تعريف نمط البريد الإلكتروني
            pattern_email = r"[\w\.-]+@[\w\.-]+\.\w+"
            # البحث عن كل بريد يحقق النمط
            for match in re.finditer(pattern_email, original):
                # إضافة كل ما يطابق إلى قائمة الكيانات التي سيتم تعميتها
                detected_entities.append(
                    {
                        "entity_group": "EMAIL",  # تعيين نوع الكيان
                        "start": match.start(),  # تحديد بداية الكيان
                        "end": match.end(),  # تحديد نهاية الكيان
                        "word": match.group(0),  # استخراج النص الفعلي للكيان
                    }
                )

        if "PHONE" in selected_labels:
            # تعريف نمط رقم الهاتف
            pattern_phone = r"(\+?\d[\d\-\s]{7,}\d)"
            # البحث عن كل أرقام الهواتف في النص
            for match in re.finditer(pattern_phone, original):
                # إضافة كل رقم هاتف إلى قائمة الكيانات
                detected_entities.append(
                    {
                        "entity_group": "PHONE",
                        "start": match.start(),
                        "end": match.end(),
                        "word": match.group(0),
                    }
                )

    elif model_name == "zero-shot":
        # ----- Zero-shot معالجة كيانات -----
        # لتحديد المواقع Regex بما أن هذا النموذج لا يعطي إحداثيات دقيقة، سنعتمد على

        # فهمها Regex تحويل أسماء الفئات إلى أنماط يمكن لـ
        label_mapping = {
            "PER": r"\b[A-Z][a-z]+\s[A-Z][a-z]+\b",  # مثال: يبحث عن اسمين يبدآن بحرف كبير
            "ORG": r"\b(Inc|Corp|Ltd|LLC)\b",  # مثال: يبحث عن اختصارات الشركات
            "LOC": r"\b(City|State|Province)\b",  # مثال: يبحث عن أسماء أماكن شائعة
            "EMAIL": r"[\w\.-]+@[\w\.-]+\.\w+",
            "PHONE": r"(\+?\d[\d\-\s]{7,}\d)",
        }

        for label in selected_labels:
            pattern = label_mapping.get(label.upper())
            if pattern:
                for match in re.finditer(pattern, original):
                    detected_entities.append(
                        {
                            "entity_group": label.upper(),
                            "start": match.start(),
                            "end": match.end(),
                            "word": match.group(0),
                        }
                    )

    # فرز الكيانات حسب موقعها في النص لكي لا تتداخل التعمية
    detected_entities.sort(key=lambda e: e["start"])

    # --------------------- تعمية النص ---------------------#

    # out: لتخزين الأجزاء
    # last: لتتبع آخر موضع تمت معالجته
    out, last = [], 0
    # المرور على كل كيان تم تحديده
    for e in detected_entities:
        # إضافة جزء النص الذي يسبق الكيان
        out.append(original[last : e["start"]])

        # Faker التحقق إذا كان سيتم استخدام
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
                out.append(style)  # أستخدام النمط الذي حدده المستخدم
        else:
            # أستخدام النمط الذي حدده المستخدم
            out.append(style)
            
        # تحديث آخر موضع تمت معالجته
        last = e["end"]
    # إضافة الجزء الأخير من النص بعد آخر كيان
    out.append(original[last:])
    # دمج الأجزاء في نص واحد
    return "".join(out)
