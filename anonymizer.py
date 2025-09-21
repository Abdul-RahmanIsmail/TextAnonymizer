# import re
# from faker import Faker
# fake = Faker()

# def anonymize_text(original, entities, selected_labels, style="*****", use_faker=False):
#     # ===== 1) معالجة الكيانات من NER =====
#     entities = [e for e in entities if e["entity_group"] in selected_labels]
#     entities.sort(key=lambda e: e["start"])

#     out, last = [], 0
#     for e in entities:
#         out.append(original[last:e["start"]])
#         if use_faker and e["entity_group"] == "PER":
#             out.append(fake.name())
#         elif use_faker and e["entity_group"] == "LOC":
#             out.append(fake.city())
#         elif use_faker and e["entity_group"] == "ORG":
#             out.append(fake.company())
#         else:
#             out.append(style)
#         last = e["end"]
#     out.append(original[last:])
#     text_after_ner = "".join(out)

#     # ===== 2) معالجة إضافية باستخدام Regex =====
#     patterns = {
#         # بريد إلكتروني
#         r'[\w\.-]+@[\w\.-]+\.\w+': style,
#         # رقم هاتف (مبسّط)
#         r'(\+?\d[\d\-\s]{7,}\d)': style,
#         # بطاقات ائتمان (13–16 رقم)
#         r'\b(?:\d[ -]*?){13,16}\b': style,
#         # تواريخ (dd/mm/yyyy أو yyyy-mm-dd)
#         r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b': style,
#         r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b': style,
#     }

#     text_final = text_after_ner
#     for pat, repl in patterns.items():
#         text_final = re.sub(pat, repl, text_final)

#     return text_final



import re
from faker import Faker
fake = Faker()

# def anonymize_text(original, entities, selected_labels, style="*****", use_faker=False):
#     # ===== 1) دمج الكيانات من NER والـ Regex =====
    
#     # قائمة الكيانات من NER (مفلترة)
#     detected_entities = [e for e in entities if e["entity_group"] in selected_labels]

#     # إضافة الكيانات من Regex
#     patterns = {
#         'EMAIL': r'[\w\.-]+@[\w\.-]+\.\w+',
#         'PHONE': r'(\+?\d[\d\-\s]{7,}\d)',
#         # يمكنك إضافة المزيد هنا
#     }
    
#     for entity_type, pattern in patterns.items():
#         for match in re.finditer(pattern, original):
#             detected_entities.append({
#                 "entity_group": entity_type,
#                 "start": match.start(),
#                 "end": match.end(),
#                 "word": match.group(0)
#             })

#     # ===== 2) معالجة جميع الكيانات المكتشفة =====
    
#     detected_entities.sort(key=lambda e: e["start"])

#     out, last = [], 0
#     for e in detected_entities:
#         out.append(original[last:e["start"]])
        
#         # استخدام Faker للكيانات التي يمكنه التعامل معها
#         if use_faker:
#             if e["entity_group"] == "PER":
#                 out.append(fake.name())
#             elif e["entity_group"] == "LOC":
#                 out.append(fake.city())
#             elif e["entity_group"] == "ORG":
#                 out.append(fake.company())
#             elif e["entity_group"] == "EMAIL":
#                 out.append(fake.email()) # Faker لديه وظيفة للبريد الإلكتروني
#             elif e["entity_group"] == "PHONE":
#                 out.append(fake.phone_number()) # Faker لديه وظيفة لأرقام الهواتف
#             else:
#                 out.append(style) # للأنواع غير المعرفة في Faker
#         else:
#             out.append(style) # استخدام النمط المحدد إذا لم يتم تفعيل Faker
            
#         last = e["end"]
#     out.append(original[last:])
#     return "".join(out)


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
