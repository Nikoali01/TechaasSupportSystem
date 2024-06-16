from langchain_community.vectorstores import Chroma
import chromadb
import os
from clean_and_chroma import get_embedding
from clean_and_chroma import get_collection_name


def get_prompt(message: str, messages):
    chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_URL",default="localhost"), port=8000)
    vector_db = Chroma(client=chroma_client, collection_name=get_collection_name(), embedding_function=get_embedding())
    retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 6})
    docs_rel = retriever.get_relevant_documents(message)
    res = ''
    for i in range(len(docs_rel)):
        res += docs_rel[i].page_content
    prompt = (f'Отвечай только на технические вопросы. Отвечай вежливо и не повторяй вопросы пользователя.'
              f' При малейших сомнениях'
              f' выводи сообщение: "К сожалению, не обладаю данной информацией. Обратитесь к оператору тех поддержки". '
              f'({res}).\nПользователь спрашивает: {message} и просит приложить название файла с данными из которых ты '
              f'берешь ответ (это название приложено в информации в формате "file_name": ). Далее будет контекст '
              f'предыдущей переписки пользователя с технической поддержкой на который ты можешь опираться: {messages}')
    return prompt


def add_message(items):
    messages = [{"role": "system",
                 "content": "Cпециалист технической поддержки большой компании, которая связана с документами."}]
    for i in range(len(items) - 1):
        if list(items[i].keys())[0] == "system":
            messages.append({"role": "assistant", "content": list(items[i].values())[0]})
        elif list(items[i].keys())[0] == "user":
            messages.append({"role": "user", "content": list(items[i].values())[0]})
    hui = get_prompt(list(items[-1].values())[0], messages)
    messages.append({"role": "user", "content": hui})
    return messages
