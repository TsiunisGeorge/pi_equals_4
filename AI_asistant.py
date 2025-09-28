
import os
from openai import OpenAI

# --- 1. НАСТРОЙКА КЛИЕНТА ---
# Рекомендуется использовать переменные окружения для вашего API-ключа
# os.environ["OPENAI_API_KEY"] = "sk-..."
# client = OpenAI()
#
# Для простоты примера, можно указать ключ напрямую:
client = OpenAI(api_key="")  # ЗАМЕНИТЕ НА ВАШ КЛЮЧ
MODEL_NAME = "gpt-4o-mini-2024-07-18"
#MODEL_NAME = "gpt-5-nano"
MAX_PROMPT_SIZE = 60000
# --- 2. СИСТЕМНЫЕ ПРОМПТЫ (как мы и определили) ---

SYSTEM_PROMPT_QUERY_TRANSFORMER = """
Ты — AI-преобразователь запросов. Твоя задача — принять вопрос пользователя и переформулировать его в лаконичный, семантически насыщенный запрос, идеально подходящий для поиска в векторной базе данных.

Правила:
1.  НЕ отвечай на вопрос. Только преобразуй его.
2.  Удали все лишние слова, приветствия, местоимения и вежливые обороты.
3.  Оставь только ключевые термины, синонимы и суть проблемы.
4.  Твой ответ должен содержать ТОЛЬКО строку с новым запросом без каких-либо пояснений.
"""

SYSTEM_PROMPT_ANSWER_GENERATOR = """
Ты — внимательный и точный AI-ассистент поддержки. Тебе будет предоставлен исходный вопрос пользователя и несколько пронумерованных фрагментов из внутренней документации.

Твоя задача — сформулировать исчерпывающий и понятный ответ на вопрос пользователя, основываясь СТРОГО на предоставленных фрагментах.

Правила:
1.  НИКОГДА не используй свои общие знания и не придумывай информацию. Вся информация для ответа должна быть взята из предоставленного контекста.
2.  Строй свой ответ на основе самых релевантных цитат из текстов.
3.  Если предоставленные фрагменты не содержат ответа на вопрос, вежливо сообщи: "К сожалению, я не смог найти точную информацию по вашему вопросу в документации."
4.  Отвечай на русском языке, вежливо и по делу.
5.  При формулировании ответа приводи цитаты из предоставленных фрагментов
"""

DOC_PROMPT_GENERATOR = """
Ты — внимательный и точный AI-ассистент поддержки. Тебе будет предоставлен исходный вопрос пользователя и несколько пронумерованных фрагментов из внутренней документации.

Твоя задача — сформулировать исчерпывающий и понятный документ на запрос пользователя, основываясь на предоставленных фрагментах.

Правила:
1.  НИКОГДА не используй свои общие знания и не придумывай информацию. Вся информация для ответа должна быть взята из предоставленного контекста.
2.  Строй свой ответ на основе самых релевантных цитат из текстов.
3.  Если предоставленные фрагменты не содержат ответа на вопрос, попытайся сформулировать дополнения для успешной генерации текстов"
4.  Отвечай на русском языке, вежливо и по делу.
"""


# --- 3. РЕАЛИЗАЦИЯ ЭТАПОВ ---

def get_optimized_query(user_question: str) -> str:
    """
    Этап 1: Преобразование вопроса пользователя в поисковый запрос.
    """
    print("--- Этап 1: Оптимизация запроса ---")
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_QUERY_TRANSFORMER},
                {"role": "user", "content": user_question}
            ],
            temperature=0.2  # Минимальная "креативность" для точности
        )
        optimized_query = response.choices[0].message.content
        print(f"Оригинальный вопрос: '{user_question}'")
        print(f"Оптимизированный запрос: '{optimized_query}'\n")
        return optimized_query
    except Exception as e:
        print(f"Ошибка на Этапе 1: {e}")
        return None


def get_final_answer(user_question: str, context_docs: list[str]) -> str:
    """
    Этап 2: Генерация ответа на основе вопроса и найденных документов.
    """
    print("--- Этап 2: Генерация финального ответа ---")
    if not context_docs:
        return "К сожалению, я не смог найти информацию по вашему вопросу в документации."

    # Собираем контекст в единый промпт для модели
    context_string = "\n".join(context_docs)
    if len(context_string) > MAX_PROMPT_SIZE:
        context_string = context_string[:MAX_PROMPT_SIZE]
    user_prompt = f"""
ИСХОДНЫЙ ВОПРОС ПОЛЬЗОВАТЕЛЯ:
"{user_question}"

ФРАГМЕНТЫ ИЗ ДОКУМЕНТАЦИИ:
{context_string}
"""
    print(len(user_prompt.split("\n")), user_prompt)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ANSWER_GENERATOR},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7  # Немного креативности для связного текста
        )
        final_answer = response.choices[0].message.content
        print("Ответ успешно сгенерирован.\n")
        return final_answer
    except Exception as e:
        print(f"Ошибка на Этапе 2: {e}")
        return "Произошла ошибка при генерации ответа."


def generate_chunk_quastion(chank):
    pass

def generate_question(paragraph: str) -> str:
    prompt = f"""
    You are given the following paragraph from a legislative act:
    ---
    {paragraph}
    ---
    Formulate one clear, practical question that an employee of an organization
    responsible for complying with this act might realistically ask.
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You generate compliance-related questions from laws."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


def dop_prompt(prompt: str, context_docs: list[str]):
    if not context_docs:
        return "К сожалению, я не смог найти информацию по вашему вопросу в документации."

    # Собираем контекст в единый промпт для модели
    context_string = "\n".join(context_docs)
    if len(context_string) > MAX_PROMPT_SIZE:
        context_string = context_string[:MAX_PROMPT_SIZE]
    user_prompt = f"""
    ИСХОДНЫЙ Требования ПОЛЬЗОВАТЕЛЯ:
    "{prompt}"

    ФРАГМЕНТЫ ИЗ ДОКУМЕНТАЦИИ:
    {context_string}
    """
    print(len(user_prompt.split("\n")), user_prompt)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": DOC_PROMPT_GENERATOR},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7  # Немного креативности для связного текста
        )
        final_answer = response.choices[0].message.content
        print("Ответ успешно сгенерирован.\n")
        return final_answer
    except Exception as e:
        print(f"Ошибка на Этапе 2: {e}")
        return "Произошла ошибка при генерации ответа."
