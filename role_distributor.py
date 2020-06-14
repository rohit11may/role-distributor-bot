from random import choice
from game import Game


def createMessage(text, ownerId=None, ownerNotif=None, roles=None):
    return dict(message=text, ownerId=ownerId, ownerNotif=ownerNotif, roles=roles)


elements = ["Hydrogen", "Helium", "Lithium", "Beryllium", "Boron", "Carbon", "Nitrogen", "Oxygen", "Fluorine", "Neon",
            "Sodium", "Magnesium", "Aluminum", "Silicon", "Phosphorus", "Sulfur", "Chlorine", "Argon", "Potassium",
            "Calcium", "Scandium", "Titanium", "Vanadium", "Chromium", "Manganese", "Iron", "Cobalt", "Nickel",
            "Copper", "Zinc", "Gallium", "Germanium", "Arsenic", "Selenium", "Bromine", "Krypton", "Rubidium",
            "Strontium", "Yttrium", "Zirconium", "Niobium", "Molybdenum", "Technetium", "Ruthenium", "Rhodium",
            "Palladium", "Silver", "Cadmium", "Indium", "Tin", "Antimony", "Tellurium", "Iodine", "Xenon", "Cesium",
            "Barium", "Lanthanum", "Cerium", "Praseodymium", "Neodymium", "Promethium", "Samarium", "Europium",
            "Gadolinium", "Terbium", "Dysprosium", "Holmium", "Erbium", "Thulium", "Ytterbium", "Lutetium", "Hafnium",
            "Tantalum", "Tungsten", "Rhenium", "Osmium", "Iridium", "Platinum", "Gold", "Mercury", "Thallium", "Lead",
            "Bismuth", "Polonium", "Astatine", "Radon", "Francium", "Radium", "Actinium", "Thorium", "Protactinium",
            "Uranium", "Neptunium", "Plutonium", "Americium", "Curium", "Berkelium", "Californium", "Einsteinium",
            "Fermium", "Mendelevium", "Nobelium", "Lawrencium", "Dubnium", "Seaborgium", "Bohrium",
            "Hassium", "Meitnerium", "Roentgenium", "Nihonium", "Flerovium", "Moscovium", "Livermorium",
            "Tennessine", "Oganesson", ]

defaultResponse = createMessage("To create a game: 'create game' \n "
                                "To join a game: 'join {insert game id} \n\n"
                                "If you are the owner: \n"
                                ""
                                "'")

errorResponse = createMessage("Sorry, I didn't understand your request.")


class RoleDistributor(object):
    def __init__(self):
        self.games = {}  # Game id -> Game
        self.players = {}  # Member id -> Game id

    def handleMsg(self, msg):
        text = msg['message'].get('text').lower().split(' ')
        memberId = msg['sender']['id']

        keyword = text[0]
        if keyword == "create":
            return self.createGame(memberId)

        elif keyword == "join":
            if len(text) != 2:
                return errorResponse
            gameId = text[1]
            return self.joinGame(gameId, memberId)

        elif keyword == "leave":
            return self.leaveGame(memberId)

        elif keyword == "add":
            if len(text) < 3:
                return errorResponse
            quantity, role = text[1], " ".join(text[2::]).lower()
            return self.amendRoles(memberId, role, quantity, addRole=True)

        elif keyword == "remove":
            if len(text) < 3:
                return errorResponse
            quantity, role = text[1], " ".join(text[2::]).lower()
            return self.amendRoles(memberId, role, quantity, addRole=False)

        elif keyword == "clear":
            if len(text) != 1:
                return errorResponse
            return self.clearRoles(memberId)

        elif keyword == "start":
            if len(text) != 1:
                return errorResponse
            return self.startGame(memberId)

        elif keyword == "status":
            if len(text) != 1:
                return errorResponse

            return self.status(memberId)

        return defaultResponse

    def _memberIsOwner(self, memberId):
        if memberId in self.players:
            currentGameId = self.players[memberId]
            return currentGameId in self.games and self.games[currentGameId].owner == memberId
        return False

    def startGame(self, memberId):
        """

        :param memberId: owner of valid game trying to change the roles
        :return: message indicating the game has started, if invalid start condition then shows game state
        """
        if not self._memberIsOwner(memberId):
            return createMessage("You are not the owner of the game.")

        game = self.games[self.players[memberId]]
        if game.readyToStart():
            return createMessage("Starting game...", roles=game.distributeRoles(), ownerId=memberId)

        return createMessage(f"Players in lobby does not match number of roles. \n\n {game}")

    def amendRoles(self, memberId, role, quantity, addRole=True):
        """

        :param memberId: owner of valid game trying to change the roles
        :param role: role name the owner is adding
        :param quantity: number of people that can be this role in the game
        :param addRole: If true, add {quantity} many {role}s to the game, otherwise remove
        :return: message indicating success or fail (validates quantity and ownership)
        """
        if not quantity.isdigit():
            return createMessage("Invalid quantity!")

        quantity = int(quantity)
        if not self._memberIsOwner(memberId):
            return createMessage("You are not the owner of the game.")

        game = self.games[self.players[memberId]]
        if addRole:
            game.addRole(role, quantity)
            return createMessage(f"Roles added! Current game: \n\n "
                                 f"{game}")
        else:
            game.removeRole(role, quantity)
            return createMessage(f"Roles removed! Current game: \n\n"
                                 f"{game}")

    def leaveGame(self, memberId):
        """

        :param memberId: person trying to leave their game
        :return: message indicating success or fail
        """
        if memberId in self.players:
            gameId = self.players[memberId]
            if gameId in self.games:
                game = self.games[gameId]
                removed = game.removeMember(memberId)

                try:
                    del self.players[memberId]
                except KeyError:
                    pass

                text = "Unable to leave game!" if not removed else "Successfully left game!"
                if not game.owner:
                    text += "Game has been cleared of all members as there is no owner. Rejoin with same code, " \
                            "first joiner will be assigned ownership."

                return createMessage(text=text,
                                     ownerId=game.owner if game.owner else None,
                                     ownerNotif=f"({len(game.members)} in lobby)"
                                     )
        return createMessage("Unable to leave game!")

    def joinGame(self, gameId, memberId, isOwner=False):
        """

        :param isOwner: whether the joiner is the owner of the game
        :param gameId: gameId that ideally exists to join
        :param memberId: person trying to join game
        :return: message indicating success or fail
        """
        if gameId in self.games:
            game = self.games[gameId]
            game.addMember(memberId, isOwner)
            self.players[memberId] = gameId

            return createMessage(text=f"Successfully joined game! "
                                      f"({len(game.members)} in lobby)"
                                      f" Please wait for your role...",
                                 ownerId=game.owner,
                                 ownerNotif=f"({len(game.members)} in lobby)")
        else:
            return createMessage("Game does not exist. Try again?")

    def createGame(self, ownerId):
        """
        :param ownerId: person creating game
        :return: game id of new game
        """
        gameId = choice(elements) + choice(elements)
        self.players[ownerId] = gameId

        self.games[gameId.lower()] = Game()
        self.joinGame(gameId.lower(), ownerId, isOwner=True)
        return createMessage(f"Success! Your game id is {gameId}.")

    def clearRoles(self, memberId):
        """

        :param memberId: owner of the game trying to clear roles of the current game
        :return: message indicating roles were cleared if they were the owner of a valid game
        """
        if not self._memberIsOwner(memberId):
            return createMessage("You are not the owner of the game.")

        game = self.games[self.players[memberId]]
        game.clearRoles()
        return createMessage(f"Cleared the roles. \n\n {game}")

    def status(self, memberId):
        if memberId in self.players:
            gameId = self.players[memberId]
            if gameId in self.games:
                game = self.games[gameId]
                return createMessage(str(game))
            else:
                return createMessage("Game does not exist!")

        return createMessage("You have not joined any games yet!")


if __name__ == "__main__":
    rd = RoleDistributor()
    print(rd.handleMsg("create game"))
