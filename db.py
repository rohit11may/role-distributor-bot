from game import Game
import json


def gameFromJson(s):
    d = json.loads(s)
    newG = Game()

    newG.members = set(d["members"])
    newG.roles = d["roles"]
    newG.owner = d["owner"]
    return newG


class RedisDict(object):
    def __init__(self, rd):
        self.rd = rd

    def __delitem__(self, k: str) -> bool:
        return self.rd.delete(k)

    def has_key(self, k: str) -> bool:
        return self.rd.exists(k)

    def __contains__(self, k: str) -> bool:
        return self.rd.exists(k)


class Games(RedisDict):
    def __init__(self, rd):
        super().__init__(rd)

    def __setitem__(self, game_id: str, game: Game) -> bool:
        return self.rd.mset({game_id: game.toJson()})

    def __getitem__(self, game_id: str) -> Game:
        return gameFromJson(self.rd.mget(game_id)[0])


class Players(RedisDict):
    def __init__(self, rd):
        super().__init__(rd)

    def __setitem__(self, player_id: str, game_id: str) -> bool:
        return self.rd.mset({player_id: game_id})

    def __getitem__(self, player_id: str) -> str:
        return self.rd.mget(player_id)[0]


if __name__ == "__main__":
    import redis, os

    r = redis.from_url(os.environ["REDIS_URL"])
    g = Games(r)
    newGame = Game()
    newGame.addRole("Bomber", 3)
    g["HelloWorld"] = newGame
    receiveGame = g["HelloWorld"]
    print(receiveGame)
    print("HelloWorlds" in g)
    # del g["HelloWorld"]
