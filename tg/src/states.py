from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationState(StatesGroup):
    WaitingForAction = State()
    WaitingForUsername = State()
    WaitingForFirstName = State()
    WaitingForLastName = State()
    WaitingForBirthday = State()
    WaitingForProject = State()
    WaitingForDateProject = State()
    WaitingForHoursProject = State()
    WaitingForTextReportProject = State()
    WaitingForViewsReport = State()
    WaitingForViewsReportDate = State()
    WaitingForViewsReportProject = State()
    