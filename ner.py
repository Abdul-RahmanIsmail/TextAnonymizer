from transformers import pipeline
 # استيراد مكتبة Pipeline من Hugging Face لتسهيل استخدام النماذج.

# تحميل نموذج BERT base NER. هذا النموذج متخصص في التعرف على الكيانات.
# 'aggregation_strategy="simple"' لتجميع أجزاء الكلمات المنقسمة إلى كيان واحد.
bert_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# تحميل نموذج Zero-shot متعدد اللغات.
# تم اختيار هذا النموذج لأنه خفيف الوزن (حوالي 500 ميجابايت) ومرن.
zero_shot_classifier = pipeline("zero-shot-classification", model="distilbert-base-multilingual-cased")

def get_entities_bert(text: str):
    """
    تشغيل NER باستخدام نموذج BERT base.
    """
    return bert_ner(text)

def get_entities_zero_shot(text: str, candidate_labels: list):
    """
    تشغيل NER باستخدام نموذج Zero-shot.
    يقوم هذا التنفيذ بتصنيف النص بالكامل، ويعتمد على قائمة الفئات التي تم تحديدها.
    """
    # تحويل الفئات المختارة إلى تنسيق مناسب للنموذج
    results = zero_shot_classifier(text, candidate_labels, multi_label=True)
    
    # تحويل النتائج إلى تنسيق يشبه نتائج BERT لسهولة المعالجة لاحقًا
    # هذا جزء مبسط، حيث أن النموذج لا يوفر إحداثيات دقيقة
    entities = []
    for i, label in enumerate(results['labels']):
        if results['scores'][i] > 0.5:
            # هنا يجب عليك إضافة منطق لتحديد موقع الكيان في النص
            # سنقوم بإرجاع الكلمة نفسها مع افتراض الموقع
            entities.append({
                "entity_group": label.upper(),
                "word": label, # هذا يوضح المبدأ فقط
                "start": 0,
                "end": 0
            })
    return entities

def get_entities(text: str, model_name: str, labels: list):
    """
    التابع الرئيسي الذي يستخرج الكيانات من النص باستخدام النموذج المختار.
    """
    # إذا كان المستخدم اختار نموذج "bert-base".
    if model_name == "bert-base":
        return get_entities_bert(text)
    # إذا كان المستخدم اختار نموذج "zero-shot".
    elif model_name == "zero-shot":
        # Zero-shot يتطلب قائمة بالفئات التي سيبحث عنها
        return get_entities_zero_shot(text, labels)
    # إرجاع النموذج الافتراضي في حالة عدم اختيار نموذج.
    else:
        return get_entities_bert(text)