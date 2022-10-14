from aiogram.dispatcher.filters.state import StatesGroup, State


class MainSG(StatesGroup):
    main = State()
    help = State()
    org_list = State()
    global_event_list = State()
    global_event = State()


class RegisterProfileSG(StatesGroup):
    region = State()
    not_region = State()
    district = State()
    activity = State()
    confirm = State()


class RegisterVolunteerSG(StatesGroup):
    name = State()
    age = State()
    volunteer_type = State()


class ProfileManagementSG(StatesGroup):
    main = State()
    activity_info = State()
    profile_info = State()
    events_info = State()
    change_activity = State()
    change_region = State()
    change_state = State()


class ProfileDeleteSG(StatesGroup):
    confirm = State()


class RegisterOrganizationSG(StatesGroup):
    activity = State()
    region = State()
    not_region = State()
    district = State()
    name = State()
    confirm = State()


class OrganizationManagementSG(StatesGroup):
    menu = State()
    chat = State()
    event_list = State()


class CreateEventSG(StatesGroup):
    district = State()
    event_type = State()
    volunteer_type = State()
    activity = State()
    name = State()
    description = State()
    confirm = State()
