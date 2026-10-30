from maxo.fsm import State, StatesGroup

class Registration(StatesGroup):
    name = State()
    phone = State()
    photo_id  = State()
    email = State()
    gender = State()
    looking_for = State()
    city = State()
    age = State()
    about = State()
    link = State()