import re
import requests

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt


def fetch_text_from_url(url):
    """
    Завантажує текстовий вміст за вказаною URL-адресою.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        print(f"Помилка під час отримання вмісту з {url}: {error}")
        return None


def count_word_frequencies(text_chunk):
    """
    Підраховує частоту зустрічання слів у переданому фрагменті тексту.
    """
    words = re.findall(r"\b\w+\b", text_chunk.lower())
    return Counter(words)


def merge_word_counts(word_count1, word_count2):
    """
    Об'єднує два словники підрахунку слів.
    """
    word_count1.update(word_count2)
    return word_count1


def display_top_words(word_counts, top_n=10):
    """
    Відображає діаграму з найпоширенішими словами.
    """
    top_words = word_counts.most_common(top_n)
    words, frequencies = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, frequencies, color="skyblue")
    plt.title(f"Топ {top_n} найбільш вживаних слів")
    plt.xlabel("Слова")
    plt.ylabel("Частота")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def split_text_into_chunks(text, num_chunks):
    """
    Розбиває текст на задану кількість фрагментів.
    """
    chunk_size = max(len(text) // num_chunks, 1)
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def analyze_text_from_url(url, num_threads=4, top_n=10):
    """
    Аналізує текст із веб-сторінки, використовуючи багатопотоковість.
    """
    text = fetch_text_from_url(url)
    if not text:
        print("Помилка: не вдалося завантажити текст.")
        return

    text_chunks = split_text_into_chunks(text, num_threads)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        word_counts_list = list(executor.map(count_word_frequencies, text_chunks))

    total_word_count = Counter()
    for word_count in word_counts_list:
        total_word_count = merge_word_counts(total_word_count, word_count)

    display_top_words(total_word_count, top_n)


if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100341.txt"

    analyze_text_from_url(url, num_threads=4, top_n=10)
