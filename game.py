from random import shuffle


class Game(object):
    def __init__(self):
        self.members = set()  # set of member ids
        self.roles = dict()  # role -> quantity
        self.owner = ""  # current owner of game

    def __repr__(self):
        role_summary = ""
        for role, quantity in self.roles.items():
            role_summary += f"{quantity} {role.upper()}{'s' if quantity > 1 else ''} \n"

        return f"{len(self.members)} in lobby.\n\n" \
               f"{role_summary}"

    def addMember(self, member, isOwner=False):
        self.members.add(member)
        if isOwner or len(self.members) == 0:
            self.owner = member

    def removeMember(self, member):
        if member in self.members:
            self.members.remove(member)

            if member == self.owner:
                self.clearMembers()
                self.owner = ""

            return True
        else:
            return False

    def clearMembers(self):
        self.members = set()

    def addRole(self, role, quantity):
        if role in self.roles:
            self.roles[role] += quantity
        else:
            self.roles[role] = quantity

    def removeRole(self, role, quantity):
        if role in self.roles:
            self.roles[role] = max(0, self.roles[role] - quantity)
            if self.roles[role] == 0:
                del self.roles[role]

            return True

        return False

    def clearRoles(self):
        self.roles = dict()

    def readyToStart(self):
        return sum(self.roles.values()) == len(self.members)

    def distributeRoles(self):
        members = list(self.members)

        roles = []
        for role, quantity in self.roles.items():
            for _ in range(quantity):
                roles.append(role.upper())

        shuffle(roles)
        shuffle(members)

        return list(zip(members, roles))


if __name__ == "__main__":
    g = Game()
    g.addMember('rohit', True)
    g.addMember('sid')
    g.addMember('sayali')
    g.addMember('lol')
    g.addMember('janay')
    g.addMember('haresh')
    g.addMember('podness')

    g.addRole("Bomber", 3)
    g.addRole("Red Hostage", 2)
    g.addRole("Blue Hostage", 2)
    g.removeRole("Blue Hostage", 1)
    g.addRole("Red Hostage", 1)
    print(g)
    print(g.readyToStart())
    g.distributeRoles()
