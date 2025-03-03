from . import config
from . import dbworker

reminder_description_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_REMINDER_DESC.value or \
    dbworker.get_current_state(message.chat.id) == config.States.S_START.value

reminder_date_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_REMINDER_DATE_OR_ADDITION.value \
    and message.text in ['/create_reminder_from_note', '/создать_напоминание_из_заметки',
                         'create reminder from note', 'создать напоминание из заметки']

get_reminder_date_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_REMINDER_DATE_OR_ADDITION.value

reminder_delete_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_REMINDER_DELETE.value

note_delete_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_NOTE_DELETE.value

choose_language_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_CHOOSE_LANGUAGE.value

choose_timezone_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_GET_TIMEZONE.value

reminder_or_note_period_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_NOTE_PERIOD.value \
    or dbworker.get_current_state(message.chat.id) == config.States.S_REMINDER_PERIOD.value

reminder_or_note_edit_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_NOTE_EDIT.value \
    or dbworker.get_current_state(message.chat.id) == config.States.S_GET_REMINDER_ID.value

new_note_or_reminder_text_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_GET_NEW_NOTE_TEXT.value \
    or dbworker.get_current_state(message.chat.id) == config.States.S_GET_NEW_REMINDER_TEXT.value

get_editable_object_in_reminder = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_GET_EDITABLE_REMINDER_OBJECT.value \
    and message.text in ['/text', '/date', '/текст', 'дату', 'text', 'date', 'текст', 'дату']

get_new_date_for_reminder = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_GET_NEW_REMINDER_DATE.value

create_more_reminders_status = lambda message: \
    dbworker.get_current_state(message.chat.id) == config.States.S_CREATE_MORE_REMINDERS.value

cancel_operation = lambda message: message.text in ['cancel', 'отмена', 'main menu', 'главное меню',
                                                    '/cancel', '/отмена', '/main_menu', '/главное_меню']

available_date_formats = lambda message: message.text in ['date formats', 'форматы даты',
                                                          '/date_formats', '/форматы_даты']

start = lambda message: message.text in ['start', '/start', '/старт', 'старт']

reminders_or_notes_for_period = lambda message: \
    message.text in ['/reminders_for_period', 'reminders for period',
                     '/reminders_for_date', 'reminders for date',
                     '/notes_for_period', 'notes for period',
                     '/notes_for_date', 'notes for date',
                     '/напоминания_на_период', 'напоминания на период',
                     '/заметки_на_период', 'заметки на период',
                     '/напоминания_на_дату', 'напоминания на дату',
                     '/заметки_на_дату', 'заметки на дату']

help_message = lambda message: message.text in ['/Help', '/Помощь', 'Help', 'Помощь']

other_functions = lambda message: message.text in ['Other', 'Дополнительно', '/Other', '/Дополнительно']

settings = lambda message: message.text in ['Settings', 'Настройки', '/Settings', '/Настройки']

change_delay = lambda message: message.text in ['change delay', 'изменить время задержки', '/change_delay',
                                                '/изменить_время_задержки']

enable_cleaning_mode = lambda message: message.text in ['enable message cleaning', 'включить удаление сообщений']

disable_cleaning_mode = lambda message: message.text in ['disable message cleaning', 'выключить удаление сообщений']

get_new_delay_time = lambda message: dbworker.get_current_state(message.chat.id) \
                                     == config.States.S_GET_NEW_DELAY_TIME.value

change_user_timezone = lambda message: message.text in ['/change_timezone', '/изменить_часовой_пояс',
                                                        'change timezone', 'сменить часовой пояс']

user_reminders = lambda message: message.text in ['/Reminders', '/Напоминания',
                                                  'Reminders', 'Напоминания']

user_notes = lambda message: message.text in ['/Notes', '/Заметки',
                                              'Notes', 'Заметки']

show_reminders_or_notes = lambda message: \
    message.text in ['/all_notes', '/all_reminders', '/все_заметки', '/все_напоминания',
                     'all notes', 'all reminders', 'все заметки', 'все напоминания']

show_more_reminders_or_notes = lambda message: \
    message.text in ['/show_more_notes', '/show_more_reminders',
                     '/показать_больше_заметок', '/показать_больше_напоминаний',
                     'show more notes', 'show more reminders',
                     'показать больше заметок', 'показать больше напоминаний',
                     ]

delete_reminder_flow = lambda message: message.text in ['delete reminder', 'удалить напоминание',
                                                        '/delete_reminder', '/удалить_напоминание']

delete_note_flow = lambda message: message.text in ['/delete_note', '/удалить_заметку',
                                                    'delete note', 'удалить заметку']

edit_note_flow = lambda message: \
    message.text in ['edit note', 'edit reminder', 'редактировать заметку', 'редактировать напоминание',
                     '/edit_note', '/edit_reminder', '/редактировать_заметку', '/редактировать_напоминание']

new_reminder = lambda message: message.text in ['New note', 'Новая заметка',
                                                '/New_note', '/Новая_заметка']
