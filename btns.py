from telegram import InlineKeyboardButton


def getButtonsE(playerId: str) -> list:
    """
    Crea los botones para el ranking de un jugador específico.

    :param playerId: ID del jugador.
    :return: Lista de listas con los botones.
    """
    return [
        [
            InlineKeyboardButton("Rangos", callback_data='ignore'),
        ],
        [
            InlineKeyboardButton("⚪️", callback_data=f'rank0_{playerId}'),
            InlineKeyboardButton("🟢", callback_data=f'rank1_{playerId}'),
            InlineKeyboardButton("🔵", callback_data=f'rank2_{playerId}'),
            InlineKeyboardButton("🟣", callback_data=f'rank3_{playerId}'),
            InlineKeyboardButton("🔴", callback_data=f'rank4_{playerId}'),
            InlineKeyboardButton("🟠", callback_data=f'rank5_{playerId}'),
        ],
        [
            InlineKeyboardButton("Entrenamientos", callback_data='ignore'),
        ],
        [
            InlineKeyboardButton("5", callback_data=f'level5_{playerId}'),
            InlineKeyboardButton("10", callback_data=f'level10_{playerId}'),
            InlineKeyboardButton("15", callback_data=f'level15_{playerId}'),
            InlineKeyboardButton("20", callback_data=f'level20_{playerId}'),
            InlineKeyboardButton("25", callback_data=f'level25_{playerId}'),
            InlineKeyboardButton("30", callback_data=f'level30_{playerId}'),
        ],
        [
            InlineKeyboardButton("Habilidades", callback_data=f'skillUnlock_{playerId}'),
        ],
        [
            InlineKeyboardButton("Reiniciar", callback_data=f'resetAll_{playerId}'),
        ]


    ]

def getButtonsH(playerId: str) -> list:
    """ Crea los botones para las habilidades de un jugador específico.
    :param playerId: ID del jugador.
    :return: Lista de listas con los botones.
    """
    return [
        [
            InlineKeyboardButton("Habilidades", callback_data='ignore'),
        ],
        [
            InlineKeyboardButton("Habilidad 1", callback_data=f'skill1_{playerId}'),
            InlineKeyboardButton("Habilidad 2", callback_data=f'skill2_{playerId}'),
            InlineKeyboardButton("Habilidad 3", callback_data=f'skill3_{playerId}'),
            InlineKeyboardButton("Habilidad 4", callback_data=f'skill4_{playerId}'),
            InlineKeyboardButton("Habilidad 5", callback_data=f'skill5_{playerId}'),
        ],
        [
            InlineKeyboardButton("Volver", callback_data='backToMainMenu')
        ]
    ]