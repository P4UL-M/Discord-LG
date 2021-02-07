import os
import sys
import asyncio
import time
import random
import discord
from discord.ext import commands


TOKEN = ""


client = commands.Bot(command_prefix='LG_')

# variable basic
joueurs = list()
game = None
mort = None

EMOJI = {
    1: '1\N{COMBINING ENCLOSING KEYCAP}',
    2: '2\N{COMBINING ENCLOSING KEYCAP}',
    3: '3\N{COMBINING ENCLOSING KEYCAP}',
    4: '4\N{COMBINING ENCLOSING KEYCAP}',
    5: '5\N{COMBINING ENCLOSING KEYCAP}',
    6: '6\N{COMBINING ENCLOSING KEYCAP}',
    7: '7\N{COMBINING ENCLOSING KEYCAP}',
    8: '8\N{COMBINING ENCLOSING KEYCAP}',
    9: '9\N{COMBINING ENCLOSING KEYCAP}',
    0: '0\N{COMBINING ENCLOSING KEYCAP}',
    "check": u"\u2611",
    "pass": u"\u274C",
    "kill": u"\U0001F5E1",
    "shield": u"\U0001F6E1"
}


class Role():
    def __init__(self, role):
        self.name = role
        self.couleur = self.getCOLOR(role)
        self.lien = self.getLIEN(role)
        self.description = self.getDESCRIPTION(role)

    def getCOLOR(self, role):
        COLOR = {
            "Loup": discord.Colour.red(),
            "Voyante": discord.Colour.dark_gold(),
            "Sorcière": discord.Colour.gold(),
            "Chasseur": discord.Colour.dark_green(),
            "Villageois": discord.Colour.blue()
        }
        return COLOR[role]

    def getLIEN(self, role):
        LIEN = {
            "Loup": 'https://www.loups-garous-en-ligne.com/jeu/assets/images/carte2.png',
            "Voyante": 'https://www.loups-garous-en-ligne.com/jeu/assets/images/carte3.png',
            "Sorcière": 'https://www.loups-garous-en-ligne.com/jeu/assets/images/carte5.png',
            "Chasseur": 'https://www.loups-garous-en-ligne.com/jeu/assets/images/carte6.png',
            "Villageois": 'https://www.loups-garous-en-ligne.com/jeu/assets/images/carte1.png'
        }
        return LIEN[role]

    def getDESCRIPTION(self, role):
        global game
        liste = ""
        for loup in game.LGs:
            liste += "- " + str(loup.name) + "\n"

        DESCRIPTION = {
            "Loup": f'Vous êtes un loup garou, vous vous réunissez la nuit pour choisir qui vous voulez tuer. \n Les loups garous sont : \n {liste}',
            "Voyante": "Vous pouvez découvrir la carte d'un joueur chaque nuit.",
            "Sorcière": "Vous disposer de deux potion : une pour guérir, une autre pour tuer. (vous ne pouvez utiliser qu'une seule potion durant votre tour).",
            "Chasseur": "Avant de mourrir vous pouvez tuer quelqu'un de votre choix, le reste du temps vous êtes un villageois.",
            "Villageois": 'Vous assister au conseil la journée puis dormer la nuit.'
        }
        return DESCRIPTION[role]


class partie():
    def __init__(self, channel, nbjoueurs):
        self.channel = channel
        self.nbjoueurs = int(nbjoueurs)
        self.isPlaying = False
        self.tour = 0

        prédéfinis = {
            5: {"Loup": 1, "Villageois": 3, "Voyante": 1},
            6: {"Loup": 2, "Villageois": 2, "Voyante": 1, "Sorcière": 1},
            7: {"Loup": 2, "Villageois": 3, "Voyante": 1, "Sorcière": 1},
            8: {"Loup": 2, "Villageois": 4, "Voyante": 1, "Sorcière": 1},
            9: {"Loup": 3, "Villageois": 3, "Voyante": 1, "Sorcière": 1, "Chasseur": 1},
            10: {"Loup": 3, "Villageois": 4, "Voyante": 1, "Sorcière": 1, "Chasseur": 1}
        }

        self.prédefini = prédéfinis[self.nbjoueurs]
        self.LGs = list()
        self.village = list()

        self.isTourLG = False
        self.isTourVillage = False
        self.isTourVovo = False
        self.isTourSoso = False
        self.isFinish = False

    def getRole(self):
        role = random.choices(list(self.prédefini.keys()),
                              weights=list(self.prédefini.values()), k=1)[0]
        self.prédefini[role] -= 1
        if self.prédefini[role] == 0:
            del self.prédefini[role]
        return role

    def Equipe(self, joueurs):
        for player in joueurs:
            if player.role.name == "Loup":
                self.LGs.append(player)
            else:
                self.village.append(player)

    def finVote(self, votants):
        votes = dict()
        for player in votants:
            if player.asVote != None:
                if player.asVote in votes:
                    votes[player.asVote] += 1
                else:
                    votes[player.asVote] = 1
            player.asVote = None
        n = None
        g = list()
        for key, value in votes.items():
            if n == None:
                n = value
                g = [key]
            elif value > n:
                n = value
                g = [key]
            elif value == n:
                g.append(key)
        if len(g) != 0:
            return random.choice(g)
        else:
            return None

    async def waitTimeout(self):
        while self.isFinish == False:
            await asyncio.sleep(1)

    async def removeJoueur(self, joueurs, mort):
        if mort != None:
            if mort.role.name == "Chasseur":
                liste = ""
                for player in joueurs:
                    if player.role.name != "Chasseur":
                        liste += str(player.emoji) + " - " + \
                            str(player.name) + "\n"
                message = discord.Embed(
                    title="Qui voulez vous tuer ?",
                    description=liste,
                    colour=mort.role.couleur
                )
                message.set_thumbnail(url=mort.role.lien)

                message = await self.channel.send(f"Chasseur tour {game.tour}", embed=message)
                for player in joueurs:
                    if player.role.name != "Sorcière" and player != mort:
                        await message.add_reaction(player.emoji)

                self.isFinish = False
                try:
                    await asyncio.wait_for(self.waitTimeout, 20)
                except TimeoutError:
                    pass
            del joueurs[joueurs.index(mort)]
            if mort in game.village:
                del self.village[game.village.index(mort)]
            else:
                del self.LGs[game.LGs.index(mort)]
            if self.isTourVillage:
                await self.channel.send(f"{mort.name} à été pendu sur la place public, il était {mort.role.name}.")
            else:
                await self.channel.send(f"{mort.name} est mort cette nuit, il était {mort.role.name}.")
        else:
            if self.isTourVillage:
                await self.channel.send("personne est mort ce matin.")
            else:
                await self.channel.send("Personne n'est mort cette nuit.")


class Joueur():
    def __init__(self, user, role, numéro):
        self.name = user.name
        self.user = user
        self.role = Role(role=role)
        self.emoji = EMOJI[numéro]
        self.isKnow = False
        self.asVote = None
        if self.role.name == "Sorcière":
            self.potionVie = True
            self.potionMort = True
        elif self.role.name == "Voyante":
            self.isKnow = True

    async def AnnonceRole(self, partie):
        if self.role.name == "Loup":
            self.role.description = self.role.getDESCRIPTION(self.role.name)
        message = discord.Embed(
            title=f'Vous êtes {self.role.name}',
            description=self.role.description,
            colour=self.role.couleur)

        message.set_thumbnail(url=self.role.lien)
        await self.user.send(embed=message)


async def GameplayManager(game, joueurs):
    tempNuit = 30
    tempJour = 90
    global mort
    while len(game.village) != 0 and len(game.LGs) != 0:
        # voyante turn
        voyante = None
        for player in game.village:
            if player.role.name == "Voyante":
                voyante = player
        if voyante != None:
            game.isTourVovo = True
            message = discord.Embed(
                title='Tour de la Voyante',
                description="La voyante regarde sa boule de cristal.",
                color=discord.Color.dark_gold())

            message.set_thumbnail(
                url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte3.png')

            await game.channel.send(embed=message)
            liste = ""
            for player in joueurs:
                if player.isKnow == True:
                    liste += str(EMOJI["check"]) + " - " + str(player.name) + \
                        " (" + str(player.role.name) + "). \n"
                else:
                    liste += str(player.emoji) + " - " + \
                        str(player.name) + ".\n"
            message = discord.Embed(
                title="Qui voulez espioner avec votre boule de cristal ?",
                description=liste,
                colour=voyante.role.couleur
            )
            message.set_thumbnail(url=voyante.role.lien)

            message = await voyante.user.send(f"Voyante tour {game.tour}", embed=message)
            for player in joueurs:
                if player.isKnow == False:
                    await message.add_reaction(player.emoji)

            game.isFinish = False
            try:
                await asyncio.wait_for(game.waitTimeout(), timeout=tempNuit)
            except asyncio.TimeoutError:
                pass
        # end voyante turn

        # LG turn
        game.isTourLG = True
        message = discord.Embed(
            title='Tour des LG',
            description="Les loups garous vont choisir qui dévorer cette nuit.",
            color=discord.Color.red())

        message.set_thumbnail(
            url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte2.png')

        await game.channel.send(embed=message)
        for player in game.LGs:
            liste = ""
            for cibles in game.village:
                liste += str(cibles.emoji) + " - " + str(cibles.name) + "\n"

            message = discord.Embed(
                title='Qui voulez vous manger ?',
                description=liste,
                color=discord.Color.red())

            message.set_thumbnail(
                url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte2.png')

            message = await player.user.send(f"LG tour {game.tour}", embed=message)

            for cibles in game.village:
                await message.add_reaction(cibles.emoji)

        await asyncio.sleep(tempNuit)
        game.isTourLG = False
        # End LG turn

        # choix du mort
        mort = game.finVote(game.LGs)
        if mort == None:
            mort = random.choice(game.village)
        # end

        # sorcière turn
        sorcière = None
        for player in game.village:
            if player.role.name == "Sorcière":
                sorcière = player
        if sorcière != None:
            if sorcière.potionVie == True or sorcière.potionMort == True:
                game.isTourSoso = True
                message = discord.Embed(
                    title='Tour de la Sorcière',
                    description="La sorcière se réveille.",
                    color=discord.Color.gold())

                message.set_thumbnail(
                    url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte5.png')

                await game.channel.send(embed=message)
                message = discord.Embed(
                    title=f"{mort.name} va mourrir cette nuit !",
                    description="{} - voulez vous le sauver ?\n{} - en tuer un autre ?\n{} - ne rien faire".format(
                        EMOJI["shield"], EMOJI["kill"], EMOJI["pass"]),
                    colour=sorcière.role.couleur
                )
                message.set_thumbnail(url=sorcière.role.lien)

                message = await sorcière.user.send(f"Sorcière tour {game.tour}", embed=message)
                if sorcière.potionVie == True:
                    await message.add_reaction(emoji=EMOJI["shield"])
                if sorcière.potionMort == True:
                    await message.add_reaction(emoji=EMOJI["kill"])
                await message.add_reaction(emoji=EMOJI["pass"])

                game.isFinish = False
                try:
                    await asyncio.wait_for(game.waitTimeout(), timeout=tempNuit)
                except asyncio.TimeoutError:
                    pass
        # end sorcière turn

        # délibération de la nuit
        game.removeJoueur(joueurs, mort)
        # end délibération

        # test de fin
        if len(game.LGs) == 0 or len(game.village) == 0:
            break
        # end test

        # villageois turn
        game.isTourVillage = True
        message = discord.Embed(
            title='Vote du village',
            description="Vous aller décider qui pendre aujourd'hui.",
            color=discord.Color.blue())

        message.set_thumbnail(
            url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte1.png')

        await game.channel.send(embed=message)
        liste = ""
        for player in joueurs:
            liste += str(player.emoji) + " - " + str(player.name) + "\n"
        message = discord.Embed(
            title='VOTE',
            description=liste,
            color=discord.Color.blue())

        message.set_thumbnail(
            url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte1.png')

        message = await game.channel.send(f"Vote {game.tour}", embed=message)
        for player in joueurs:
            await message.add_reaction(emoji=player.emoji)
        await asyncio.sleep(tempJour)
        mort = game.finVote(joueurs)
        game.removeJoueur(joueurs, mort)
        game.isTourLG = False
        # End villageois turn

        game.tour += 1
    if len(game.village) == 0:
        await game.channel.send("Les loup garou ont gagner !")
    else:
        await game.channel.send("Le village à gagner !")
    await game.channel.send("fin de la partie !")


# nouvelle partie crée
@client.command()
async def launch(ctx, nbjoueur):
    global game
    if game == None:
        game = partie(channel=ctx.channel, nbjoueurs=nbjoueur)

        # message de lancement
        message = discord.Embed(
            title='Loup Garou',
            description='Partie de loup garou de {} joueur(s) lancée !'.format(
                nbjoueur),
            colour=discord.Colour.blue())

        message.set_thumbnail(
            url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte2.png')

        # envoie des message
        réponse = await ctx.send('launch \n', embed=message)
        await réponse.add_reaction(emoji=EMOJI["check"])
        await client.change_presence(activity=discord.Game(status=discord.Status.online, name="partie lancé"))
    else:
        await ctx.send("Une partie est déjà en cour, vous pouvez la stopper avec ``LG_stop``.")

# stop la partie partie en cour
@client.command()
async def stop(ctx):
    os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)

# joueur s'ajoute à la partie
@client.event
async def on_reaction_add(reaction, user):
    # verification que la reaction n'est pas a ignorer
    if user != client.user:
        global game
        global joueurs
        joueur = None
        # recherche du joueur
        if game.isPlaying:
            for player in joueurs:
                if player.user == user:
                    joueur = player
        # rejoint la partie
        if all([game != None, game.isPlaying == False, reaction.message.author == client.user, reaction.emoji == EMOJI["check"]]):
            joueurs.append(Joueur(user=user,
                                  role=game.getRole(), numéro=len(joueurs)))
            await game.channel.send(f"{joueurs[-1].name} à été ajouté à la partie.")
            # si lancement
            if len(joueurs) == game.nbjoueurs:
                game.isPlaying = True

                liste = str()
                for player in joueurs:
                    liste += " - " + str(player.name) + "\n"

                message = discord.Embed(
                    title='La partie commence',
                    description=f'Vous venez de lancer une partie de loup-garou à {game.nbjoueurs} avec : \n' + str(
                        liste),
                    colour=discord.Colour.blue())

                message.set_thumbnail(
                    url='https://www.loups-garous-en-ligne.com/jeu/assets/images/carte2.png')

                await game.channel.send(embed=message)

                game.Equipe(joueurs=joueurs)
                for player in joueurs:
                    await player.AnnonceRole(partie=game)

                await GameplayManager(game=game, joueurs=joueurs)
        # vote des Loup Garou
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == f"LG tour {game.tour}", game.isTourLG == True]):
            if joueur.asVote == None:
                for player in joueurs:
                    if player.emoji == reaction.emoji:
                        joueur.asVote = player
                        for loup in game.LGs:
                            await loup.user.send(
                                f'{user.name} à voter pour {player.name}, {player.emoji}.')
            else:
                await joueur.user.send(
                    "Dévoter tout le monde avant de pourvoir revoter quelqu'un.")
        # vote du village
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == f"Vote {game.tour}", joueur != None, game.isTourVillage == True]):
            if joueur.asVote == None:
                for player in joueurs:
                    if player.emoji == reaction.emoji:
                        joueur.asVote = player
                        await game.channel.send(f'{user.name} à voter pour {player.name}, {player.emoji}.')
        # vote voyante
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == f"Voyante tour {game.tour}", joueur != None, game.isTourVovo == True, game.isFinish == False]):
            for player in joueurs:
                if player.emoji == reaction.emoji:
                    await joueur.user.send(f"{player.name} est {player.role.name}")
                    joueurs[joueurs.index(player)].isKnow = True
                    game.isFinish = True
        # vote sorcière
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == f"Sorcière tour {game.tour}", joueur != None, game.isTourSoso == True, game.isFinish == False]):
            global mort
            if reaction.emoji == EMOJI["shield"]:
                mort = None
                joueur.potionVie = False
                game.isFinish = True
            elif reaction.emoji == EMOJI["kill"]:
                liste = ""
                for player in joueurs:
                    if player.role.name != "Sorcière" and player != mort:
                        liste += str(player.emoji) + " - " + \
                            str(player.name) + "\n"
                message = discord.Embed(
                    title="Qui voulez vous tuer ?",
                    description=liste,
                    colour=joueur.role.couleur
                )
                message.set_thumbnail(url=joueur.role.lien)

                message = await joueur.user.send(f"Sorcière tour {game.tour}", embed=message)
                for player in joueurs:
                    if player.role.name != "Sorcière" and player != mort:
                        await message.add_reaction(player.emoji)
            elif reaction.emoji == EMOJI["pass"]:
                game.isFinish = True
            else:
                for player in joueurs:
                    if reaction.emoji == player.emoji:
                        game.removeJoueur(joueurs, player)
                        joueur.potionMort = False
                        game.isFinish = True
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == f"Chasseur tour {game.tour}", joueur != None, game.isFinish == False, joueur.role.name == "Chasseur", joueur in joueurs]):
            for player in joueurs:
                if player.emoji == reaction.emoji:
                    game.removeJoueur(joueurs, player)
                    game.isFinish == True


# joueur se retire de la partie
@client.event
async def on_reaction_remove(reaction, user):
    # verification que la reaction n'est pas a ignorer
    if user != client.user:
        global game
        global joueurs
        joueur = None
        # recherche du joueur
        if game.isPlaying:
            for player in joueurs:
                if player.user == user:
                    joueur = player
        if all([game != None, game.isPlaying == False, reaction.message.author == client.user, reaction.emoji == EMOJI["check"]]):
            for i in joueurs:
                if i.user == user:
                    if i.Role in game.prédefini:
                        game.prédefini[i.Role] += 1
                    else:
                        game.prédefini[i.Role] = 1
                    del joueurs[joueurs.index(i)]
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == "LG tour", joueur.asVote != None]):
            if reaction.emoji == joueur.asVote.emoji:
                joueur.asVote = None
        elif all([game.isPlaying == True, reaction.message.author == client.user, reaction.message.content == "Vote", joueur != None, game.isTourVillage == True]):
            if joueur.asVote == None:
                if reaction.emoji == joueur.asVote.emoji:
                    joueur.asVote = None

# initialisation du bot
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    await client.change_presence(activity=discord.Game(status=discord.Status.online, name="en attente de partie"))

client.run(TOKEN)
