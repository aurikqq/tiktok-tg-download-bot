from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    reg_name_state = State()
    reg_nick_state = State()
    reg_bd_state = State()
    reg_s_state = State()
    reg_country_state = State()

    edit_profile_state = State()
    end_profile_state = State()
    edit_bd_state = State()
    edit_join_state = State()
    delete_profile_state = State()

    rename_idea_state = State()

    ach_id_state = State()
    ach_name_state = State()
    ach_desc_state = State()

    city_name_state = State()
    city_citizens_state = State()
    city_coords_state = State()
    city_name_edit_state = State()
    city_citizens_edit_state = State()
    city_coords_edit_state = State()