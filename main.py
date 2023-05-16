from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ContentType
from aiogram.filters import Command, Text, CommandStart
import random
from environs import Env # имппортируем из библиотеки класс Env

env = Env() # создаем экземпляр класса
env.read_env() # читаем данные из файла .env и загружаем их в окружение
bot_token = env('BOT_TOKEN') # считываем токен из окружения

bot: Bot = Bot(token=bot_token)
dp: Dispatcher = Dispatcher()

ATTEMPTS: int = 7

# создаем словарь с состояниями пользователей
users: dict = {}

random_stickers = {1: 'CAACAgIAAxkBAAIBsGRPfevCf87UOSqhQN32GVryerIJAAKQEAACa16oSBwaTsyegEWYLwQ',
                   2: 'CAACAgIAAxkBAAIBsmRPfmUOO_fITHL20uQrHqdF0w4GAAIQAAPANk8T6oGKKfEfAugvBA',
                   3: 'CAACAgIAAxkBAAIBtGRPfn4ckTudthWmT1Cm4RrY2RzXAAIVAAPANk8TzVamO2GeZOcvBA',
                   4: 'CAACAgIAAxkBAAIBtmRPfs7SeU0-O09GDl-QtZkuFFkHAAIDAAPANk8TpCnu5n3zwHgvBA',
                   5: 'CAACAgIAAxkBAAIBuGRPfvXNotS9KAf1zsY2i2-8gzQPAAJCEAACM8UpSZAO1BGnKkqCLwQ',
                   6: 'CAACAgIAAxkBAAIBumRPfxWPewES54OYIzMxwloKtM-WAAIUAAPANk8TrWWZ5Lkw9j4vBA',
                   7: 'CAACAgIAAxkBAAIB02RPgdzCRSwzRmVJBtOJuAgyZUA1AAIYAAPANk8T1vonv5xqGPgvBA',
                   8: 'CAACAgIAAxkBAAIB22RPglY5656l46NL_rV2wJYNsWFLAAJaAAPANk8TC_wPT9xGGeEvBA'
                   }


def random_digits() -> int:
    return random.randint(1, 100)


# создаем хэндлер для обработки команды \start
@dp.message(CommandStart())
async def command_start(msg: Message):
    await msg.answer('Привет!\nДавай сыграем со мной в игру "Угадай число"?\n\n'
                     'Для получения правил игры и списка доступных команд нажми кнопку \help')
    if msg.from_user.id not in users:  # type: ignore
        users[msg.from_user.id] = {'in_game': False,  # type: ignore
                                   'secret_numbers': None,
                                   'attempts': None,
                                   'total_games': 0,
                                   'wins': 0
                                   }


@dp.message(Command('help'))
async def command_help(msg: Message):
    await msg.answer(f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                     f'а вам нужно его угадать.\nУ вас есть {ATTEMPTS} '
                     f'попыток\n\nДоступные команды:\n/help - правила '
                     f'игры и список команд\n/cancel - выйти из игры\n'
                     f'/stat - посмотреть статистику\n\nДавай сыграем?')


@dp.message(Command(commands=['stat']))
async def command_stat(msg: Message):
    if msg.from_user.id in users:
        await msg.answer(f'Всего игр сыграно: {users[msg.from_user.id]["total_games"]}\n'
                     f'игр выиграно: {users[msg.from_user.id]["wins"]}.')
    else:
        await msg.answer('Вы еще не стартовали игру')


@dp.message(Command('cancel'))
async def command_cancel(msg: Message):
    if users[msg.from_user.id]['in_game']:  # type: ignore
        await msg.answer('Вы вышли из игры. Если захотите сыграть '
                         'снова - напишите об этом')
        users[msg.from_user.id]['in_game'] = False
    if users[msg.from_user.id]['in_game'] == False:
        await msg.answer('А мы итак не играем. Может начнем игру?')

@dp.message(lambda msg: msg.sticker) # отлавливаем стикеры от юзера
async def user_sticker(msg: Message):
    await msg.answer_sticker('CAACAgIAAxkBAAIEV2Rdpfh6HD9_sU6Tg-z6I0IMePfNAAIZAAPANk8T0EOA9iBXFEsvBA') # отправляем стикер в ответ


#@dp.message(lambda msg: msg.sticker) # отлавливаем стикеры от юзера
#async def user_sticker(msg: Message):
    # пересылаем стикер другому пользователю
 #   await bot.send_sticker(chat_id=140973847, sticker=msg.sticker.file_id)

@dp.message(F.text.contains('хер'))
async def mat(msg: Message):
    await msg.answer('материться нельзя')


@dp.message(Text(text=['да', 'играем', 'сыграем', 'хорошо',
                       'ок', 'начинай', 'игра', 'давай'], ignore_case=True))
async def positiv_answer(msg: Message):
    if not users[msg.from_user.id]['in_game']:
        await msg.answer('Хорошо! Я загадал число от 1 до 100,\nпопробуй его угадать.')
        users[msg.from_user.id]['in_game'] = True
        users[msg.from_user.id]['secret_numbers'] = random_digits()
        users[msg.from_user.id]['attempts'] = ATTEMPTS
    else:
        await msg.answer('Пока мы играем в игру я могу '
                         'реагировать только на числа от 1 до 100 '
                         'и команды /cancel и /stat')


async def negative_answer(msg: Message):
    if not users[msg.from_user.id]['in_game']:
        await msg.answer('Жаль :((\n\nЕсли захотите поиграть, дайте команду.')
    else:
        await msg.answer('Предлагаю доиграть эту игру.\nПришлите число от 1 до 100.')


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def numbers_answer(msg: Message):
    if users[msg.from_user.id]['in_game']:
        if int(msg.text) == users[msg.from_user.id]['secret_numbers']:  # type: ignore
            await msg.answer('Ура! Вы угадали!\n\nМожет сыграем еще?')
            await msg.answer_sticker(random_stickers[random.randint(1, 8)])
            users[msg.from_user.id]['in_game'] = False
            users[msg.from_user.id]['total_games'] += 1
            users[msg.from_user.id]['wins'] += 1
        elif int(msg.text) > users[msg.from_user.id]['secret_numbers']:
            users[msg.from_user.id]['attempts'] -= 1
            await msg.answer(f'Ваше число больше.\nПопробуйте еще раз.\nУ вас осталось '
                             f'{users[msg.from_user.id]["attempts"]} попыток.')
        elif int(msg.text) < users[msg.from_user.id]['secret_numbers']:  # type: ignore
            users[msg.from_user.id]['attempts'] -= 1
            await msg.answer(f'Ваше число меньше.\nПопробуйте еще раз.\nУ вас осталось '
                             f'{users[msg.from_user.id]["attempts"]} попыток.')

        if users[msg.from_user.id]['attempts'] == 0:
            await msg.answer(f'К сожалению у вас не осталось попыток.\n'
                             f'Вы проиграли. Я загадал число {users[msg.from_user.id]["secret_numbers"]}.\n\n'  # type: ignore
                             f'Поиграем еще?')
            users[msg.from_user.id]['in_game'] = False
            users[msg.from_user.id]['total_games'] += 1
    else:
        await msg.answer('Мы еще не играем. Хотите сыграть?')


# @dp.message()
async def other_answer(msg: Message):
    if msg.from_user.id not in users:
        await msg.answer('Для начала игры нажмите /start')
    elif users[msg.from_user.id]['in_game']:
        await msg.answer('Мы же сейчас играем.\nПришлите, пожалуйста цифру от 1 до 100')
    else:
        await msg.answer('Я не понимаю. Давайте просто поиграем.\nВы можете написать '
                         'утвердительное или отрицательное сообщение.')


# dp.message.register(command_start, Command('start')) # зарегистрировали хэндлер старт в диспетчере
# dp.message.register(command_help, Command('help'))
# dp.message.register(command_stat, Command('stat'))
# dp.message.register(command_cancel, Command('cancel'))
dp.message.register(positiv_answer, Text(text=['да', 'играем', 'сыграем', 'хорошо',
                                               'ок', 'начинай', 'игра', 'давай'], ignore_case=True))
dp.message.register(negative_answer, Text(text=['Нет', 'Не', 'Не хочу', 'Не буду',
                                                'Отстань', 'Хватит', 'Надоело'],
                                          ignore_case=True))
# dp.message.register(numbers_answer, lambda x: x.text and x.text.isdigit and 1 <= int(x.text) <= 100)
dp.message.register(other_answer)

dp.run_polling(bot)
