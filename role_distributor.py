from random_word import RandomWords

defaultResponse = {'message': "Hello! \n "
                              "To create a game: 'create game' \n "
                              "To join a game: 'join {insert game id}'"
                   }

whitelist = {'create', 'join', 'leave'}


def createMessage(text, ownerId=None, ownerNotif=None):
    return {'message': text, 'ownerId': ownerId, 'ownerNotif': ownerNotif}


class RoleDistributor(object):
    words = RandomWords()

    def __init__(self):
        self.games = {}

    def handleMsg(self, msg):
        text = msg['message'].get('text')
        memberId = msg['sender']['id']

        keyword = text.lower().split(' ')[0]
        if keyword in whitelist:
            if keyword == "create":
                return self.createGame(memberId)
            elif keyword == "join":
                gameId = text.lower().split(' ')[1]
                return self.joinGame(gameId, memberId)

        return defaultResponse

    def joinGame(self, gameId, memberId, isOwner=False):
        """

        :param isOwner: whether the joiner is the owner of the game
        :param gameId: gameId that ideally exists to join
        :param memberId: person trying to join game
        :return: message indicating success or fail
        """
        if gameId in self.games:

            self.games[gameId.lower()].add((memberId, isOwner))
            ownerId = ""
            for player, ownership in list(self.games[gameId.lower()]):
                if ownership:
                    ownerId = player

            return createMessage(text=f"Successfully joined game! "
                                      f"({len(self.games[gameId.lower()])} in lobby)"
                                      f" Please wait for your role...",
                                 ownerId=ownerId,
                                 ownerNotif=f"({len(self.games[gameId.lower()])} in lobby)")
        else:
            return createMessage("Game does not exist. Try again?")

    def createGame(self, ownerId):
        """
        :param ownerId: person creating game
        :return: game id of new game
        """
        gameId = self.words.get_random_word(maxLength=5).title() + \
                 self.words.get_random_word(maxLength=5).title()

        self.games[gameId.lower()] = set()
        self.joinGame(gameId.lower(), ownerId, isOwner=True)
        return createMessage(f"Success! Your game id is {gameId}.")


if __name__ == "__main__":
    rd = RoleDistributor()
    print(rd.handleMsg("hello whats up"))
