from transformers import pipeline
# لتسهيل استخدام النماذج Hugging من Pipeline استيراد مكتبة

#  النموذج المتخصص في التعرف على الكيانات BERT base NER تحميل نموذج
#  لتجميع أجزاء الكلمات المنقسمة إلى كيان واحد aggregation_strategy="simple"
bert_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# متعدد اللغات Zero-shot تحميل نموذج
# تم اختيار هذا النموذج لأنه خفيف الوزن (حوالي 500 ميجابايت) ومرن
zero_shot_classifier = pipeline(
    "zero-shot-classification", model="distilbert-base-multilingual-cased"
)


def get_entities_bert(text: str):
    """
    باستخدام نموذج     
    BERT base باستخدام نموذج NER تشغيل
    """
    return bert_ner(text)


def get_entities_zero_shot(text: str, candidate_labels: list):
    """
    Zero-shot باستخدام نموذج NER تشغيل
    يقوم هذا التنفيذ بتصنيف النص بالكامل، ويعتمد على قائمة الفئات التي تم تحديدها
    """
    
    # تحويل الفئات المختارة إلى تنسيق مناسب للنموذج
    results = zero_shot_classifier(text, candidate_labels, multi_label=True)

    # لسهولة المعالجة لاحقًا BERT تحويل النتائج إلى تنسيق يشبه نتائج 
    # هذا جزء مبسط، حيث أن النموذج لا يوفر إحداثيات دقيقة
    entities = []
    for i, label in enumerate(results["labels"]):
        if results["scores"][i] > 0.5:
            # هنا إضافة منطق لتحديد موقع الكيان في النص
            # سنقوم بإرجاع الكلمة نفسها مع افتراض الموقع
            entities.append(
                {
                    "entity_group": label.upper(),
                    "word": label,  # هذا يوضح المبدأ فقط
                    "start": 0,
                    "end": 0,
                }
            )
    return entities


def get_entities(text: str, model_name: str, labels: list):
    """
    التابع الرئيسي الذي يستخرج الكيانات من النص باستخدام النموذج المختار
    """
    # bert-base إذا كان المستخدم اختار نموذج 
    if model_name == "bert-base":
        return get_entities_bert(text)
    # zero-shot إذا كان المستخدم اختار نموذج
    elif model_name == "zero-shot":
        # يتطلب قائمة بالفئات التي سيبحث عنها Zero-shot
        return get_entities_zero_shot(text, labels)
    # إرجاع النموذج الافتراضي في حالة عدم اختيار نموذج
    else:
        return get_entities_bert(text)
