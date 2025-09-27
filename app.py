from AI_asistant import get_optimized_query, get_final_answer
from process_data import search


def main():
    # Задаем вопрос от имени пользователя
    print("Введите запрос: ")
    user_question = input()

    # Этап 1: Оптимизируем запрос
    optimized_query = get_optimized_query(user_question)

    if optimized_query:
        # Этап 1.5: Ищем в векторной БД
        retrieved_docs = search(optimized_query)

        # Этап 2: Генерируем финальный ответ
        final_answer = get_final_answer(user_question, retrieved_docs)

        # Выводим результат
        print("=" * 40)
        print("✅ ИТОГОВЫЙ ОТВЕТ ДЛЯ ПОЛЬЗОВАТЕЛЯ:")
        print("=" * 40)
        print(final_answer)




main()