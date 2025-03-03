from enum import Enum

db_file = "database.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    # """
    S_START = "0"  # Начало нового диалога
    S_REMINDER_DESC = "1"
    S_REMINDER_DATE_OR_ADDITION = "2"
    S_REMINDER_DELETE = "3"
    S_REMINDER_PERIOD = "4"
    S_NOTE_DELETE = "5"
    S_CHOOSE_LANGUAGE = "6"
    S_GET_TIMEZONE = "7"
    CHOOSE_NOTE_SHOW_VARIANT = "8"
    CHOOSE_REMINDER_SHOW_VARIANT = "9"
    S_NOTE_PERIOD = "10"
    S_NOTE_EDIT = "11"
    S_GET_NEW_NOTE_TEXT = "12"
    S_GET_REMINDER_ID = "13"
    S_GET_EDITABLE_REMINDER_OBJECT = "14"
    S_GET_NEW_REMINDER_TEXT = "15"
    S_GET_NEW_REMINDER_DATE = "16"
    S_GET_NEW_DELAY_TIME = "17"
    S_CREATE_MORE_REMINDERS = "18"


