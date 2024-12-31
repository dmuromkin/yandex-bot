from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, question_index):
    
    get_question_query = f"""
        DECLARE $question_id AS Uint64;

        SELECT question_text
        FROM `quiz_questions`
        WHERE id == $question_id;
    """
    
    get_answers_query = f"""
        DECLARE $question_id AS Uint64;

        SELECT answer_text, is_correct
        FROM `quiz_answers`
        WHERE question_id == $question_id;
    """
    
    question = execute_select_query(pool, get_question_query, question_id=question_index)[0]
    answers =  execute_select_query(pool, get_answers_query, question_id=question_index)
    
    correct_answer_index = -1
    for index, item in enumerate(answers):
        if item["is_correct"] == True:
            correct_answer_index = index
            break
    
    answers_list = []
    for item in answers:
        answers_list.append(item["answer_text"])

    kb = generate_options_keyboard(answers_list, answers_list[correct_answer_index])
    await message.answer(f"{question["question_text"]}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 1
    current_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_quiz_score(user_id, current_score)
    await get_question(message, current_question_index)


async def get_correct_answer(question_id):
    
    get_correct_answer_query = f"""
        DECLARE $question_id AS Uint64;

        SELECT answer_text
        FROM `quiz_answers`
        WHERE question_id == $question_id AND is_correct = True;
    """
    
    answer = execute_select_query(pool, get_correct_answer_query, question_id=question_id)[0]
    
    return answer["answer_text"]


async def get_quiz_length():
    get_quiz_length_query = f"""
        SELECT COUNT(*)
        AS rownumber 
        FROM `quiz_questions`;
    """
    result = execute_select_query(pool, get_quiz_length_query)
    
    if len(result) == 0:
        return 0
    if result[0]["rownumber"] is None:
        return 0
    return result[0]["rownumber"] 


async def get_quiz_index(user_id):
    get_user_index_query = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index_query, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["question_index"] is None:
        return 0
    return results[0]["question_index"]


async def get_quiz_score(user_id):
    get_user_score_query = f"""
        DECLARE $user_id AS Uint64;

        SELECT current_score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_score_query, user_id=user_id)

    if len(results) == 0:
        return 0
    if results[0]["current_score"] is None:
        return 0
    return results[0]["current_score"]     


async def update_quiz_index(user_id, question_index):
    set_quiz_index_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`)
        VALUES ($user_id, $question_index);
    """

    execute_update_query(
        pool,
        set_quiz_index_query,
        user_id=user_id,
        question_index=question_index,
    )
 
    
async def update_quiz_score(user_id, new_score):
    set_quiz_score_query = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $new_score AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `current_score`)
        VALUES ($user_id, $new_score);
    """

    execute_update_query(
        pool,
        set_quiz_score_query,
        user_id=user_id,
        new_score=new_score,
    )    