from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from service import get_question, new_quiz, get_quiz_index, update_quiz_index, get_quiz_length, get_correct_answer, get_quiz_score, update_quiz_score

router = Router()

@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    await callback.message.answer("Верно!")
    # Номер текущего вопроса в базе данных
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Набранные очки
    current_score = await get_quiz_score(callback.from_user.id)
    current_score += 1
    await update_quiz_score(callback.from_user.id, current_score)
    
    quiz_length = await get_quiz_length()

    if current_question_index < quiz_length:
        current_question_index += 1
        # Обновление номера текущего вопроса в базе данных
        await update_quiz_index(callback.from_user.id, current_question_index)
        await get_question(callback.message, current_question_index)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await callback.message.answer("Правильных ответов: " + str(current_score))

  
@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Получение номера текущего вопроса
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Правильный ответ
    correct_option = await get_correct_answer(current_question_index)

    await callback.message.answer(f"Неправильно. Правильный ответ: {correct_option}")
    
    quiz_length = await get_quiz_length()
    
    if current_question_index < quiz_length:
        current_question_index += 1
        await update_quiz_index(callback.from_user.id, current_question_index)
        await get_question(callback.message, current_question_index)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        current_score = await get_quiz_score(callback.from_user.id)        
        await callback.message.answer("Правильных ответов: " + str(current_score))


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    
    await message.answer(f"Давайте начнем квиз!")
    await message.answer_photo("https://storage.yandexcloud.net/bot-preview/images.jpg")
    await new_quiz(message)