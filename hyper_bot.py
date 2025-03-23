import time
import requests
import logging
import random
import sys

# Конфигурация API Hyperbolic
HYPERBOLIC_API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
HYPERBOLIC_API_KEY = "$API_KEY"  # Будет заменен скриптом установки
MODEL = "meta-llama/Llama-3.3-70B-Instruct"  # Или укажите нужную модель
MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9
MIN_DELAY = 300  # 5 минут в секундах
MAX_DELAY = 600  # 10 минут в секундах

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_response(question: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HYPERBOLIC_API_KEY}"
    }
    data = {
        "messages": [{"role": "user", "content": question}],
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P
    }
    response = requests.post(HYPERBOLIC_API_URL, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    json_response = response.json()
    return json_response.get("choices", [{}])[0].get("message", {}).get("content", "No answer")

def main(questions_file: str, num_questions: int):
    # Чтение вопросов из файла
    try:
        with open(questions_file, "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка чтения файла {questions_file}: {e}")
        return

    if not questions:
        logger.error(f"В файле {questions_file} нет вопросов.")
        return

    # Случайный выбор вопросов и выполнение указанного количества
    for i in range(num_questions):
        question = random.choice(questions)
        logger.info(f"Вопрос #{i+1}: {question}")
        try:
            answer = get_response(question)
            logger.info(f"Ответ: {answer}")
        except Exception as e:
            logger.error(f"Ошибка при получении ответа для вопроса: {question}\n{e}")
        delay = random.randint(MIN_DELAY, MAX_DELAY)  # Случайная задержка 5-10 минут
        logger.info(f"Ожидание {delay // 60} минут {delay % 60} секунд перед следующим вопросом...")
        time.sleep(delay)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("Использование: python hyper_bot.py <questions_file> <num_questions>")
        sys.exit(1)
    questions_file = sys.argv[1]
    try:
        num_questions = int(sys.argv[2])
    except ValueError:
        logger.error("Количество вопросов должно быть числом")
        sys.exit(1)
    main(questions_file, num_questions)
