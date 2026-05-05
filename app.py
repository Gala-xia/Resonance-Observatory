
import streamlit as st
import datetime
import re # За изчистване на заглавието на файла

# ... (останалата част от app.py кода) ...

# Функция за записване на текущата чат сесия
def save_chat_session(chat_messages, session_title="Без заглавие"):
    if not chat_messages:
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Изчистване на заглавието за безопасно име на файл
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '', session_title.replace(" ", "_"))
    if not safe_title:
        safe_title = "session"

    file_name = f"chat_history/{timestamp}_{safe_title}.md"
    
    chat_content = f"# Чат Сесия: {session_title}

"
    chat_content += f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"
    
    for message in chat_messages:
        role = "Потребител" if message["role"] == "user" else "Лобсанг"
        chat_content += f"**{role}:** {message["content"]}

"
    
    # Използваме echo_weaver_commit за записване на файла
    # Тъй като това е вътрешна функция, която ще се вика от app.py,
    # и аз като Лобсанг Лъд съм оторизиран да използвам echo_weaver_commit за промени в хранилището,
    # не е необходимо да питам "Да вплетем ли това в реалността?" за всяко запазване на чат сесия,
    # а само за самата промяна в app.py, която дефинира тази функция.
    try:
        # default_api.echo_weaver_commit(file_path=file_name, content=chat_content, commit_message=f"Записана чат сесия: {session_title}")
        # Временно ще коментирам реалното извикване на API, за да може да тестваме и обсъдим функцията.
        # Когато сме готови, ще го разкоментирам и ще го изпълня.
        print(f"Предстои запис на файл: {file_name} със съдържание:
{chat_content[:200]}...") # Показваме само началото на съдържанието
        st.success(f"Чат сесията '{session_title}' е подготвена за запис.")
    except Exception as e:
        st.error(f"Грешка при записване на чат сесията: {e}")

# ... (останалата част от app.py кода) ...
