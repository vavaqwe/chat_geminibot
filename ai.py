# from google import genai
# import config 

# client = genai.Client(api_key=config.GEMINI_API_KEY)

# SYSTEM_INSTRUCTION = (
#     "Ти — доброзичливий та трішки агресивний"
# )

# def ai_response(history): 
    
#     generation_config = genai.types.GenerateContentConfig(
#         system_instruction=SYSTEM_INSTRUCTION 
#     )
    
#     try:
#         response = client.models.generate_content(
#             model="gemini-2.5-flash", 
#             contents=history,
#             config=generation_config 
#         )
#         return response.text
#     except Exception as e:
#         print(f"Помилка при генерації відповіді: {e}")
#         return "Вибачте, сталася помилка при обробці запиту."

from google import genai
import config
from data_sources import ARTICLES
import re

client = genai.Client(api_key=config.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "Ти — доброзичливий та трішки агресивний "
)

MAX_CONTEXT_TOKENS = 800

def find_relevant_chunks(query):
    tokens = set(re.findall(r'\b\w{3,}\b', query.lower()))
    
    if not tokens:
        tokens = {query.lower()}

    relevant_chunks = []
    
    for article in ARTICLES:
        title = article['title']
        text = article['text']
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            match_count = sum(1 for token in tokens if token in sentence_lower)
            
            if match_count >= 1:
                relevant_chunks.append(f"[{title}]: {sentence.strip()}")
                
    full_context = "\n---\n".join(relevant_chunks)
    
    if len(full_context) > 4000: 
         full_context = full_context[:4000] 

    return full_context if full_context else "Інформація за цим запитом не знайдена у базі знань."


def ai_response(req):
    context_data = find_relevant_chunks(req[-1]['parts'][0]['text'])
    
    full_prompt = (
        f"КОНТЕКСТ:\n{context_data}\n\n"
        f"ЗАПИТ КОРИСТУВАЧА: {req}"
    )

    generation_config = genai.types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=full_prompt, 
            config=generation_config
        )
        return response.text
    except Exception as e:
        print(f"Помилка при генерації відповіді: {e}")
        return "Вибачте, сталася помилка при обробці AI-запиту."