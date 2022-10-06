ON_HELP_TEXT = "on_help_text"
ON_ORG_REGISTRATION_END_TEXT = "on_org_registration_text"
ON_PROFILE_REGISTRATION_END_TEXT = "on_profile_registration_text"
ON_RETURN_TEXT = "on_return_text"
ON_START_TEXT = "on_start_text"

MESSAGE_KEYS = (
    (ON_HELP_TEXT, 'Сообщение "Что может этот бот?"'),
    (ON_ORG_REGISTRATION_END_TEXT, "Сообщение в конце регистрации организации"),
    (ON_PROFILE_REGISTRATION_END_TEXT, "Сообщение в конце регистрации профиля"),
    (ON_RETURN_TEXT, "Сообщение при возвращении пользователя"),
    (ON_START_TEXT, "Сообщение для нового пользователя"),
)

DEFAULT_MESSAGES = {
    ON_HELP_TEXT: "",
    ON_ORG_REGISTRATION_END_TEXT: "",
    ON_PROFILE_REGISTRATION_END_TEXT: "",
    ON_RETURN_TEXT: "",
    ON_START_TEXT: "",
}


ONBOARDING_MESSAGE = (
    "Привет!\n"
    "Это пилотная версия экобота Союза эковолонтерских "
    "организаций.\nЗдесь Вы сможете узнать об экологических "
    "мероприятиях и проектах, стать волонтёром или найти "
    "единомышленников.\n Сейчас бот работает с Ленинградской"
    " областью, но далее охватит другие регионы.\n"
    "Помогите улучшить бота: опробуйте весь функционал."
)

RETURN_MESSAGE = "С возвращением!"

HELP_MESSAGE = (
    "С помощью бота волонтеры могут получать персонализированные "
    "уведомления о мероприятиях и волонтерских вакансиях в своем "
    "районе, а экологически активные сообщества - найти волонтеров и"
    " привлечь участников на свои мероприятия и акции.\n\nБот может "
    "пригласить Вас в чат, где собрались экоактивисты из вашего "
    "района. Общайтесь, делитесь опытом, объединяйтесь для создания"
    " экособытий!\n\nСовсем скоро всем пользователям бота будет "
    "доступна справочная информация: адреса пунктов приема "
    "вторсырья, контакты движений и организаций.\n\n"
    "Пока работает пилотная версия, функционал будет расширяться."
)
