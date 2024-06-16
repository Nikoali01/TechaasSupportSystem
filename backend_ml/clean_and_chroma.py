import nltk
import os
import ssl

# Attempt to set NLTK data path manually
nltk_data_path = os.path.expanduser("./nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Update the NLTK data path
nltk.data.path.append(nltk_data_path)

# Fix SSL issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download the punkt tokenizer
nltk.download('punkt', download_dir=nltk_data_path)

import fitz
from PIL import Image
import re
import uuid
import langchain
import langchain.document_loaders
import langchain.text_splitter
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb


def clean_text(text):
    # Remove all punctuation except words, numbers, and hyphens
    text = re.sub(r'[^\w\s\-]', '', text)
    # Fix hyphenation and join split words
    text = text.replace('-\n', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()  # Strip leading and trailing whitespace


def remove_headers_and_footers(text):
    # Pattern to match headers and footers, adjust based on your document
    header_footer_patterns = [
        re.compile(r"Инструкция пользователей .*? Версия", re.DOTALL),
        re.compile(r"Инструкция пользователей D-1C1-\d+ .*? Версия", re.DOTALL),
    ]
    for pattern in header_footer_patterns:
        text = re.sub(pattern, '', text)
    return text.strip()  # Strip leading and trailing whitespace


def remove_table_of_contents(text):
    # Pattern to match table of contents, adjust based on your document
    toc_pattern = re.compile(r'Оглавление.*?(?=\d+\s+[A-ZА-Я])', re.DOTALL)
    return re.sub(toc_pattern, '', text).strip()  # Strip leading and trailing whitespace


def remove_numbered_lines(text):
    # Remove lines starting with numbers
    lines = text.split('\n')
    lines = [line for line in lines if not re.match(r'^\d+', line.strip())]
    return '\n'.join(lines).strip()  # Strip leading and trailing whitespace


def clean_pdf(input_pdf, output_txt):
    # Open the PDF
    doc = fitz.open(input_pdf)
    text_output = []
    image_counter = 1
    counter = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Skip header pages
        if page_num < 2:  # Adjust this number based on your specific PDF structure
            continue

        # Extract text, ignoring page numbers and converting tables to text
        text = page.get_text("text")

        # Remove page numbers (assuming they are at the bottom of the page)
        lines = text.split('\n')
        if lines and lines[-1].strip().isdigit():
            lines = lines[:-1]
        text = '\n'.join(lines)

        # Remove headers, footers, and table of contents
        text = remove_table_of_contents(text)
        # Remove lines starting with numbers
        text = remove_numbered_lines(text)
        # Clean the text
        text = clean_text(text)
        # Clean from header lines
        text = remove_headers_and_footers(text)
        # Add cleaned text to output
        text_output.append(text)

    # Write cleaned text to output file
    with open(output_txt, 'w', encoding='utf-8') as output_file:
        output_file.write('\n'.join(text_output))


def process_directory(input_dir, output_dir):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.pdf'):
            input_pdf = os.path.join(input_dir, filename)
            output_txt = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
            clean_pdf(input_pdf, output_txt)


# Example usage
input_dir = '/dataset/originals'
output_dir = '/dataset/to_txt'

process_directory(input_dir, output_dir)

# Load documents from the specified directory
loader = DirectoryLoader(output_dir, glob='*.txt')

# Создайте экземпляр сплиттера
splitter = langchain.text_splitter.RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=50)

# Загрузите документы и добавьте название файла в каждый документ
loaded_documents = loader.load()
documents_with_metadata = []
for doc in loaded_documents:
    file_name = doc.metadata.get('source', 'unknown')  # Получаем название файла из метаданных
    content = doc.page_content
    fragments = splitter.create_documents([content])
    for fragment in fragments:
        fragment.metadata['file_name'] = file_name
        documents_with_metadata.append(fragment)


def get_embedding():
    # Initialize the embedding model
    return HuggingFaceEmbeddings(model_name="distiluse-base-multilingual-cased-v2")


def get_collection_name():
    return "atom"


# Initialize the Chroma vector database
collection_name = get_collection_name()
chroma_client = chromadb.HttpClient(host=os.getenv("CHROMA_URL",default="localhost"), port=8000)
# Check if the collection exists, if not create it
try:
    collection = chroma_client.get_collection(collection_name)
    collection._embedding_function = get_embedding()

except Exception as e:
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=get_embedding()
    )

# Add document fragments to the vector database
vector_db = Chroma(client=chroma_client, collection_name=collection_name, embedding_function=get_embedding())
vector_db.add_documents(documents_with_metadata)
