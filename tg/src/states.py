from aiogram.dispatcher.filters.state import State, StatesGroup

class RegistrationState(StatesGroup):
    WaitingForAction = State()
    WaitingForUsername = State()
    WaitingForFirstName = State()
    WaitingForLastName = State()
    WaitingForBirthday = State()
    WaitingForPassword = State()

