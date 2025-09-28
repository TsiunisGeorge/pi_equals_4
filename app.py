import streamlit as st
import tempfile
import os
import json
import time
import docx  # Required to create .docx files dynamically

from AI_asistant import *
from file_converter import parse_file
from generate.test1 import quick_generate
from process_data import *


# --- Mock Functions (placeholders for your actual modules) ---
# These functions simulate the behavior of your imported modules,
# allowing this script to run standalone for testing purposes.


DATA_FILE = "documents.json"

st.set_page_config(page_title="AI Документация", layout="wide")

# --- Initialize session_state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                st.session_state.documents = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            st.session_state.documents = []
    else:
        st.session_state.documents = []

st.title("AI Ассистент по документации")

# --- Sidebar for document management ---
with st.sidebar:
    st.header("Список подключенных документов:")
    if st.session_state.documents:
        for doc in st.session_state.documents:
            st.markdown(f"📄 {doc['name']}")
    else:
        st.info("Документы пока не подключены.")

    st.divider()

    st.header("⚙️ Управление документами")
    uploaded_file = st.file_uploader("➕ Загрузить документ",
                                     type=["pdf", "docx", "doc", "txt", "html", "htm"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        try:
            parsed_text = parse_file(temp_path)
            if uploaded_file.name not in [d['name'] for d in st.session_state.documents]:
                st.session_state.documents.append({
                    "name": uploaded_file.name,
                    "content": parsed_text
                })
                process(parsed_text, uploaded_file.name.split('.')[0])
                st.success(f"✅ Файл {uploaded_file.name} успешно добавлен!")
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.documents, f, ensure_ascii=False, indent=2)
                st.rerun()
            else:
                st.warning(f"Файл с именем {uploaded_file.name} уже существует.")
        except Exception as e:
            st.error(f"Ошибка при обработке файла: {e}")
        finally:
            os.remove(temp_path)

    st.divider()

    # --- Document Generation Section ---
    st.header("📑 Генерация документов")

    if st.session_state.documents:
        # 🔑 ИЗМЕНЕНИЕ: Фильтруем список, оставляя только .docx файлы для селектора
        docx_doc_names = [
            doc["name"] for doc in st.session_state.documents if doc["name"].lower().endswith(".docx")
        ]

        if docx_doc_names:  # Показываем UI генерации, только если есть подходящие файлы
            selected_doc_name = st.selectbox(
                "Выберите базовый документ (.docx):",  # Обновили название для ясности
                options=docx_doc_names
            )

            generation_prompt = st.text_area(
                "Что вы хотите получить?",
                placeholder="Например: Создай техническое задание по разработке кружки-непроливайки на основе документа.",
                height=100
            )
            output_filename = st.text_input(
                "Имя выходного файла:",
                value="Сгенерированный_документ.docx"
            )

            if st.button("🔄 Сгенерировать документ"):
                if not selected_doc_name:
                    st.warning("Выберите базовый документ!")
                elif not generation_prompt.strip():
                    st.warning("Введите описание того, что вы хотите получить!")
                elif not output_filename.strip():
                    st.warning("Введите имя выходного файла!")
                else:
                    with st.spinner("Генерирую документ..."):
                        lst = search(generation_prompt)
                        generation_prompt += 'доп информация:' + dop_prompt(generation_prompt,lst)

                        # ... (остальная логика генерации остается без изменений)
                        temp_input_path = None
                        temp_output_path = None
                        try:
                            selected_doc_data = next(doc for doc in st.session_state.documents if doc["name"] == selected_doc_name)
                            doc_content = selected_doc_data['content']
                            temp_doc = docx.Document()
                            temp_doc.add_paragraph(doc_content)

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_input_file:
                                temp_input_path = temp_input_file.name
                                temp_doc.save(temp_input_path)

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_output_file:
                                temp_output_path = temp_output_file.name

                            quick_generate(
                                input_doc=temp_input_path,
                                prompt=generation_prompt,
                                output_doc=temp_output_path,
                            )

                            with open(temp_output_path, "rb") as f:
                                doc_bytes = f.read()

                            st.success("✅ Документ успешно сгенерирован!")
                            st.download_button(
                                label="📥 Скачать сгенерированный документ",
                                data=doc_bytes,
                                file_name=output_filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        except Exception as e:
                            st.error(f"Ошибка при генерации документа: {e}")
                        finally:
                            if temp_input_path and os.path.exists(temp_input_path):
                                os.unlink(temp_input_path)
                            if temp_output_path and os.path.exists(temp_output_path):
                                os.unlink(temp_output_path)
        else:
            # Сообщение, если нет .docx файлов
            st.warning("Для генерации нужен хотя бы один документ формата .docx.")

    else:
        st.info("Сначала загрузите документы, чтобы начать генерацию.")


# --- Chat Message History ---
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Chat Input Field ---
if prompt := st.chat_input("Введите вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Ищу ответ..."):
            docs = [doc["content"] for doc in st.session_state.documents]
            answer = get_final_answer(prompt, docs)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

