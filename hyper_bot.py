#!/bin/bash

# Цвета текста
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # Нет цвета (сброс цвета)

# Проверка наличия curl и установка, если не установлен
if ! command -v curl &> /dev/null; then
    sudo apt update
    sudo apt install curl -y
fi
sleep 1

# Отображаем логотип
curl -s https://raw.githubusercontent.com/noxuspace/cryptofortochka/main/logo_club.sh | bash

# Основная директория проекта
PROJECT_DIR="$HOME/hyperbolic"
ACCOUNTS_DIR="$PROJECT_DIR/accounts"
MAX_ACCOUNTS=50
ACTIVE_ACCOUNTS=5
MIN_QUESTIONS_PER_DAY=30
MAX_QUESTIONS_PER_DAY=100

# Меню
echo -e "${YELLOW}Выберите действие:${NC}"
echo -e "${CYAN}1) Установка бота${NC}"
echo -e "${CYAN}2) Обновление бота${NC}"
echo -e "${CYAN}3) Просмотр логов${NC}"
echo -e "${CYAN}4) Рестарт бота${NC}"
echo -e "${CYAN}5) Удаление бота${NC}"

echo -e "${YELLOW}Введите номер:${NC} "
read choice

case $choice in
    1)
        echo -e "${BLUE}Установка бота...${NC}"

        # --- 1. Обновление системы и установка необходимых пакетов ---
        sudo apt update && sudo apt upgrade -y
        sudo apt install -y python3 python3-venv python3-pip curl
        
        # --- 2. Создание папки проекта и поддиректории для аккаунтов ---
        mkdir -p "$ACCOUNTS_DIR"
        cd "$PROJECT_DIR" || exit 1
        
        # --- 3. Создание виртуального окружения и установка зависимостей ---
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install requests
        deactivate
        
        # --- 4. Сохранение hyper_bot.py в проекте ---
        cat << 'EOT' > "$PROJECT_DIR/hyper_bot.py"
import time
import requests
import logging
import random
import sys

HYPERBOLIC_API_URL = "https://api.hyperbolic.xyz/v1/chat/completions"
HYPERBOLIC_API_KEY = "$API_KEY"
MODEL = "meta-llama/Llama-3.3-70B-Instruct"
MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9
MIN_DELAY = 300
MAX_DELAY = 600

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
    try:
        with open(questions_file, "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка чтения файла {questions_file}: {e}")
        return

    if not questions:
        logger.error(f"В файле {questions_file} нет вопросов.")
        return

    for i in range(num_questions):
        question = random.choice(questions)
        logger.info(f"Вопрос #{i+1}: {question}")
        try:
            answer = get_response(question)
            logger.info(f"Ответ: {answer}")
        except Exception as e:
            logger.error(f"Ошибка при получении ответа для вопроса: {question}\n{e}")
        delay = random.randint(MIN_DELAY, MAX_DELAY)
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
EOT

        # --- 5. Запрос 50 API-ключей и создание структуры для аккаунтов ---
        echo -e "${YELLOW}Введите 50 API-ключей для Hyperbolic (по одному на строку, Enter после каждого):${NC}"
        for i in $(seq 1 $MAX_ACCOUNTS); do
            echo -e "${CYAN}API-ключ для аккаунта $i:${NC}"
            read API_KEY
            ACCOUNT_DIR="$ACCOUNTS_DIR/account_$i"
            mkdir -p "$ACCOUNT_DIR"
            cp "$PROJECT_DIR/hyper_bot.py" "$ACCOUNT_DIR/hyper_bot.py"
            sed -i "s/HYPERBOLIC_API_KEY = \"\$API_KEY\"/HYPERBOLIC_API_KEY = \"$API_KEY\"/" "$ACCOUNT_DIR/hyper_bot.py"
            # Скачивание файла вопросов для каждого аккаунта (можно заменить на разные URL)
            QUESTIONS_URL="https://raw.githubusercontent.com/noxuspace/cryptofortochka/main/hyperbolic/questions.txt"
            curl -fsSL -o "$ACCOUNT_DIR/questions.txt" "$QUESTIONS_URL"
        done

        # --- 6. Создание скрипта для запуска 5 случайных аккаунтов ---
        cat <<EOT > "$PROJECT_DIR/run_random_accounts.sh"
#!/bin/bash
PROJECT_DIR="$PROJECT_DIR"
ACCOUNTS_DIR="$ACCOUNTS_DIR"
source "\$PROJECT_DIR/venv/bin/activate"
for i in \$(shuf -i 1-$MAX_ACCOUNTS -n $ACTIVE_ACCOUNTS); do
    ACCOUNT_DIR="\$ACCOUNTS_DIR/account_\$i"
    QUESTIONS_FILE="\$ACCOUNT_DIR/questions.txt"
    QUESTIONS_COUNT=\$(shuf -i $MIN_QUESTIONS_PER_DAY-$MAX_QUESTIONS_PER_DAY -n 1)
    echo "Запуск аккаунта \$i с \$QUESTIONS_COUNT вопросами"
    python "\$ACCOUNT_DIR/hyper_bot.py" "\$QUESTIONS_FILE" \$QUESTIONS_COUNT &
done
wait
EOT
        chmod +x "$PROJECT_DIR/run_random_accounts.sh"

        # --- 7. Создание systemd сервиса ---
        USERNAME=$(whoami)
        HOME_DIR=$(eval echo ~$USERNAME)

        sudo bash -c "cat <<EOT > /etc/systemd/system/hyper-bot.service
[Unit]
Description=Hyperbolic API Bot Service
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/run_random_accounts.sh
Restart=always
Environment=PATH=$HOME_DIR/hyperbolic/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin

[Install]
WantedBy=multi-user.target
EOT"

        # --- 8. Обновление конфигурации systemd и запуск сервиса ---
        sudo systemctl daemon-reload
        sudo systemctl restart systemd-journald
        sudo systemctl enable hyper-bot.service
        sudo systemctl start hyper-bot.service
        
        # Заключительное сообщение
        echo -e "${PURPLE}-----------------------------------------------------------------------${NC}"
        echo -e "${YELLOW}Команда для проверки логов:${NC}"
        echo "sudo journalctl -u hyper-bot.service -f"
        echo -e "${PURPLE}-----------------------------------------------------------------------${NC}"
        echo -e "${GREEN}CRYPTO FORTOCHKA — вся крипта в одном месте!${NC}"
        echo -e "${CYAN}Наш Telegram https://t.me/cryptoforto${NC}"
        sleep 2
        sudo journalctl -u hyper-bot.service -f
        ;;

    2)
        echo -e "${BLUE}Обновление бота...${NC}"
        sleep 2
        echo -e "${GREEN}Обновление бота не требуется!${NC}"
        ;;

    3)
        echo -e "${BLUE}Просмотр логов...${NC}"
        sudo journalctl -u hyper-bot.service -f
        ;;

    4)
        echo -e "${BLUE}Рестарт бота...${NC}"
        sudo systemctl restart hyper-bot.service
        sudo journalctl -u hyper-bot.service -f
        ;;
        
    5)
        echo -e "${BLUE}Удаление бота...${NC}"
        sudo systemctl stop hyper-bot.service
        sudo systemctl disable hyper-bot.service
        sudo rm /etc/systemd/system/hyper-bot.service
        sudo systemctl daemon-reload
        sleep 2
        rm -rf "$PROJECT_DIR"
        echo -e "${GREEN}Бот успешно удален!${NC}"
        echo -e "${PURPLE}-----------------------------------------------------------------------${NC}"
        echo -e "${GREEN}CRYPTO FORTOCHKA — вся крипта в одном месте!${NC}"
        echo -e "${CYAN}Наш Telegram https://t.me/cryptoforto${NC}"
        sleep 1
        ;;

    *)
        echo -e "${RED}Неверный выбор. Пожалуйста, введите номер от 1 до 5!${NC}"
        ;;
esac
