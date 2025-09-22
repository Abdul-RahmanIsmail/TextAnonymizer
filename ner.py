from transformers import (
    pipeline,
)  # Hugging Face لتسهيل استخدام نماذج Pipeline استيراد مكتبة

# BERT base NER تحميل نموذج
# النموذج الذي تم استخدامه للتعرف على الكيانات
# 'aggregation_strategy="simple"' لتجميع أجزاء الكلمات المنقسمة إلى كيان واحد
bert_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")


#  بسبب حجمه الكبير  Zero-shot لم يتم استخدام
# zero_shot_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def get_ner_model(model_name: str):
    """ (bert-base حالياً متاح فقط) يفوم هذا التابع بإرجاع النموذج المناسب بناءً على اسم النموذج الذي يختاره المستخدم"""

    # bert-base إذا كان المستخدم اختار نموذج 
    if model_name == "bert-base":
        return bert_ner  # (إرجاع النموذج  (تم تحميله مسبقًا
    
    # لم يتم استخدام نموذج Zero-shot حاليًا، بسبب حجمه الكبير
    # elif model_name == "zero-shot":
    #    return zero_shot_ner
    
    else:
        return bert_ner  # إرجاع النموذج الافتراضي في حالة عدم اختيار نموذج


def get_entities(text: str, model_name: str = "bert-base"):
    """
    التابع الرئيسي الذي يستخرج الكيانات من النص باستخدام النموذج المختار
    """
    # الحصول على النموذج المناسب من الدالة المساعدة
    model = get_ner_model(model_name)
    # تشغيل النموذج على النص وإرجاع قائمة الكيانات التي تم تحديدها
    return model(text)
