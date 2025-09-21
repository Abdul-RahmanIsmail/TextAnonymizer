from transformers import pipeline

# تحميل مرة واحدة
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def get_entities(text: str):
    return ner(text)
