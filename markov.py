import json
import random
import re

def clean_text(text):
    replacements = {
        "—": "-",  
        "«": "\"",  
        "»": "\"",  
        "…": "..."  
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    words = text.split()
    cleaned_words = [word for word in words if re.fullmatch(r'[а-яА-Я0-9.,!?!"№;%:?*()ёЁ\"-]+', word)]
    
    return ' '.join(cleaned_words)

def build_markov_chain(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = clean_text(f.read())
    words = text.split()
    chain = {}
    start_words = []

    for i in range(len(words) - 2):
        current_word = words[i]
        next_word = words[i + 1]

        # Для начала цепочки, если предшествующее слово заканчивается на пунктуацию
        if i == 0 or words[i - 1][-1] in ".!?":
            start_words.append((current_word, next_word))

        # Добавляем биграмму в цепь
        if (current_word, next_word) not in chain:
            chain[(current_word, next_word)] = {}

        if i + 2 < len(words):
            following_word = words[i + 2]
            # Используем кортеж как ключ и обновляем частоту перехода
            chain[(current_word, next_word)][following_word] = chain[(current_word, next_word)].get(following_word, 0) + 1

    # Преобразуем цепь в вероятностную форму
    chain_prob = {}
    for bigram, transitions in chain.items():
        total = sum(transitions.values())
        rounded_probs = {next_word: round(count / total, 4) for next_word, count in transitions.items()}
        adjustment = 1.0 - sum(rounded_probs.values())
        if adjustment != 0:
            first_key = next(iter(rounded_probs))
            rounded_probs[first_key] += adjustment
        chain_prob[str(bigram)] = rounded_probs  # Преобразуем кортеж в строку

    return chain_prob, start_words

def generate_text(chain, start_words, word_count=50):
    if not start_words:
        start_words = list(chain.keys())

    current_bigram = random.choice(start_words)
    generated_words = list(current_bigram)

    for _ in range(word_count - 2):
        next_words = chain.get(str(current_bigram))  # Преобразуем кортеж в строку
        if not next_words:
            current_bigram = random.choice(start_words)
        else:
            words, probs = zip(*next_words.items())
            next_word = random.choices(words, weights=probs, k=1)[0]
            generated_words.append(next_word)
            current_bigram = (current_bigram[1], next_word)

    return ' '.join(generated_words)

def save_chain(chain, start_words, filename='chain.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        # Сохраняем в JSON, преобразовав кортежи в строки
        json.dump({"chain": chain, "start_words": start_words}, f, ensure_ascii=False, indent=2)

def load_chain(filename='chain.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Преобразуем строки обратно в кортежи
        data['chain'] = {eval(key): value for key, value in data['chain'].items()}
        return data['chain'], data['start_words']

if __name__ == '__main__':
    chain, start_words = build_markov_chain('training_text.txt')

    # Сохраняем цепь
    save_chain(chain, start_words)

    # Генерируем тестовый текст
    test_text = generate_text(chain, start_words, word_count=50)
    print("Сгенерированный текст:")
    print(test_text)
