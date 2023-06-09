from aiogram import Dispatcher
from aiogram import types
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.reply.student import reply_student_kb
from tg_bot.misc.database import db_add_func, db_session
from tg_bot.misc.states import SelectRole, RegisterStudent
from tg_bot.models.models import Student, User, Group


async def check_student_fullname(message: types.Message, state: FSMContext):
    # Проверяем введенное ФИО на наличие 3-ёх слов
    if len(message.text.split()) == 3:
        # переводим full_name в нижний регистр и кладем в словарь MemoryStorage
        await state.update_data(full_name=message.text.lower())
        await state.set_state(RegisterStudent.student_study_group)
        await message.answer(
            text="Теперь введите группу, в который вы обучаетесь.\n"
        )
    else:
        # ФИО состоит не из трёх слов
        await message.answer(
            text="ФИО должно состоять из 3-ёх слов"
        )


async def check_student_group(message: types.Message, state: FSMContext):
    if len(message.text.split('-')) == 2:
        group = db_session.query(Group).filter_by(name=message.text.lower()).first()
        if not group:
            group = Group(name=message.text.lower())
            db_add_func(group)
        await state.update_data(group_id=group.id)
        student_data = await state.get_data()
        # Создаем ОРМ объекты нового пользователя и нового студента
        user_exists = db_session.query(User).filter(User.tg_username == message.from_user.username).first()
        # Проверяем существует ли пользователь с такими данными
        if user_exists:
            new_student = Student(user_id=user_exists.id, group_id=group.id)
            # user_exists.student.append(new_student)
            # group.students.append(new_student)
            # db_commit_func()
            db_add_func(new_student)
        else:
            new_user = User(
                full_name=student_data['full_name'],
                tg_username=student_data['tg_username'],
            )
            db_add_func(new_user)
            new_student = Student(user_id=new_user.id, group_id=group.id)
            db_add_func(new_student)
        # Запишем id студента из базы данных в MemoryStorage
        await state.update_data(student_id=new_student.id)
        # установка состояния студента и отправка сообщения об удачной регистрации
        await state.set_state(SelectRole.student)
        await message.answer(
            text="Регистрация прошла успешно!\n"
                 "Можете приступать к работе с заданиями!",
            reply_markup=reply_student_kb()
        )
    else:
        await message.answer(
            text="Вы ввели неверное название группы.\n"
                 "Оно должно состоять из 2-ух словах, разделенных тире.\n"
                 "Попробуйте еще раз."
        )


def register_student(dp: Dispatcher):
    # state handlers
    dp.message.register(check_student_fullname, RegisterStudent.student_full_name)  # Добавить проверку на ContentType
    dp.message.register(check_student_group, RegisterStudent.student_study_group)
