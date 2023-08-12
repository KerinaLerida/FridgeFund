import bot
import logging
import random


def achat(my_database, id_user, item_name, nb):  # achat => si quantity >=1 et balance >=price_item
    item_price = my_database.get_item_price(item_name)
    balance = my_database.get_balance_by_id(id_user)
    item_quantity = my_database.get_item_quantity(item_name)
    nb = int(nb)

    if item_quantity >= nb and nb!=0:
        if balance >= int(nb * item_price):
            my_database.update_quantity_by_name(item_quantity - nb, item_name)
            my_database.update_balance_by_id(-1 * (nb * item_price), id_user)
            return "Purchase made! [ " + str(nb) + " | " + item_name + " ]"
        else:
            return "Your wallet is very light, no " + item_name + " for you!"
    elif nb==0:
        return "Buying nothing it's stupid!"
    elif item_quantity==0:
        return "No more stock for this product :("
    else:
        return "Only "+str(item_quantity)+" left.."


def coin_flip(user_id, user_choice, bet, my_database):
    if float(my_database.get_balance_by_id(user_id)) >= bet:
        result = random.choice(["heads", "tails"])
        if result == user_choice:
            my_database.update_balance_by_id(float(bet), user_id)
            return f"Well done! It's {result}! You have won {bet} ff."
        else:
            my_database.update_balance_by_id(-1 * float(bet), user_id)
            return f"Too bad... It's {result}. You lost {bet} ff."
    else:
        return "Insufficient balance to bet.."


def help_command(message, msg_bureau, msg_cotisant): #msg de debug pour corriger sa commande
    s = ""
    if bot.check_role("Bureau", message):
        s = " ,or , " + msg_bureau
    return "Just try: " + msg_cotisant + s


def handle_response(message, strmessage, my_database):
    p_message = strmessage.lower()
    author = message.author  #name
    id_author = author.id
    print("Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")
    logging.info(
        "Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")

    # Crée : un wallet si l'user n'en a pas
    name_author = str(author)
    if not check_user_exist(id_author, my_database):
        my_database.insert_user(id_author, name_author, name_author, 0)
        return "Your wallet has been created!"
    elif name_author != my_database.get_user_name_by_id(id_author):  # MAJ : name/pseudo user
        my_database.update_name_by_id(name_author, id_author)

    # Parsing commands and arguments
    args = p_message.split()

    command = args[0]  # Command word
    if command == 'hello' and len(args) == 1:
        return 'Hey there!'

    if command == "coinflip" and len(args) == 3:
        if args[1] == "heads" or args[1] == "tails":
            return coin_flip(id_author, args[1], int(args[2]), my_database)
        else:
            return "Just try : $coinflip <heads or tails> <amount_bet_ff"

    if command == "help":
        if len(args) == 1:
            command_summary = """
Commandes du bot FridgeFund:

$hello : Etre poli(e) avec FridgeFund
$info : Affiche des informations sur le bot
$ff : Affiche la liste des utilisateurs
$help : Affiche le message d'aide
$user : Vérifie la possession d'un compte (wallet)
$items : Liste tous les items disponibles
$item <nom_item> : Affiche les détails d'un item spécifique
$wallet : Affiche le solde de votre portefeuille
$buy <nom_item> <quantité> : Achète des items
$buy <nom_item> : Achète un item
"""
            return command_summary
        elif len(args) == 2 and args[1] == "bureau" and bot.check_role("Bureau", message):
            supremetie_bureau = """
Commandes du bot FridgeFund nécessitant le rôle "Bureau":

$help bureau
$wallet <id_utilisateur>
$buy <nom_item> <quantité> <id_utilisateur>: Achat d'items par l'id utilisateur donné
$create user <id_utilisateur> <nom_réel> <solde_initial> : Crée un nouvel utilisateur
$create item <nom_item> <quantité> <prix> : Crée un nouvel item
$update balance <id_utilisateur> <montant> : Met à jour le solde d'un utilisateur (ajout du montant au solde)
$update name <id_utilisateur> <nouveau_nom> : Met à jour le nom réel d'un utilisateur
$update quantity <nom_item> <nouvelle_quantité> : Met à jour la quantité d'un item
$update price <nom_item> <nouveau_prix> : Met à jour le prix d'un item
$delete user <id_utilisateur> : Supprime un utilisateur
$delete item <nom_item> : Supprime un item
"""
            return supremetie_bureau

    if command == "user" and check_user_exist(id_author, my_database):
        return "You already have a wallet.."

    if command == "wallet":
        if len(args) == 1:
            return affiche_balance(id_author, id_author, my_database)
        elif len(args) == 2 and bot.check_role("Bureau", message) and check_user_exist(args[1], my_database):
            return affiche_balance(id_author, int(args[1]), my_database)

        return help_command(message, "$wallet id_user", "$wallet")

    if command == "items":
        if len(args) == 1:
            data = my_database.get_all_items()
            if not data:
                return "No drinks or food are available.."
            s = "Drinks and food available :\n\n"
            for item in data:
                name_, quantity_, price_ = item
                s += f"{name_} | Quantity: {quantity_}, Price: {price_} ff\n"
            return s
        return "Just try : $items , or, $item item_name"

    if command == "ff":
        if len(args) == 1:
            data = my_database.get_all_users()
            if not data:
                return "No user is in the database.."
            s = "Ranking of FridgeFunders :\n\n"
            for user in data:
                id_, name_, rname_, balance_ = user
                s += f"Id: {id_} | Pseudo: {name_}, First name: {rname_}, Balance: {balance_} ff\n"
            return s
        return "Just try : /ff 15 , to increase your IQ.."

    if command == "info":
        if len(args) == 1:
            return "My name is FridgeFund, some people prefer to call me as ChadBot. I can help you $help , to spend money in the fridge for drinks and food!"

    if command == "item":
        if len(args) == 2 and my_database.item_exist_by_name(args[1]):
            name, quantity, price = my_database.get_item_by_name(args[1])
            return f"{name} | Quantity: {quantity}, Price: {price} ff"
        return "Just try : $item item_name , or, $items ,to see all items"

    if command == "buy":
        arg_1 = args[1]
        if len(args) == 2 and check_item_exist(arg_1, my_database):
            return achat(my_database, id_author, arg_1, 1)

        elif len(args) == 3 and check_item_exist(arg_1, my_database):
            return achat(my_database, id_author, arg_1, args[2])

        elif len(args) == 4 and bot.check_role("Bureau", message) and check_user_exist(args[3], my_database):
            return achat(my_database, args[3], arg_1, args[2])

        return help_command(message, "$buy item_name quantity_taken id_user",
                            "$buy item_name ,or , $buy item_name quantity_taken")

    # *************************************** Bureau Suprématie *********************************************
    if command == "create" and bot.check_role("Bureau", message):
        arg_2 = args[2]
        if len(args) == 5:
            arg_3 = args[3]
            arg_4 = args[4]
            if args[1] == "user" and not check_user_exist(arg_2, my_database):
                my_database.insert_user(int(arg_2), arg_3, arg_3, float(arg_4))
                return "You created the user : " + str(arg_3)

            elif args[1] == "item" and not check_item_exist(arg_2, my_database):
                my_database.insert_item(arg_2, arg_3, arg_4)
                return "You created the item : " + str(arg_2)

        return "Create: $create user id_user real_name balance ,or , $create item item_name quantity price"

    if command == "update" and bot.check_role("Bureau", message):
        arg_1 = args[1]
        if len(args) == 4:
            arg_2 = args[2]
            arg_3 = args[3]

            if check_user_exist(arg_2, my_database):
                if arg_1 == "balance":
                    old_balance = my_database.get_balance_by_id(arg_2)
                    my_database.update_balance_by_id(arg_3, arg_2)
                    return "Update: " + affiche_balance(int(id_author), int(arg_2), my_database) + " [ Old balance: " + str(
                        old_balance) + " ff ]"
                elif arg_1 == "name":
                    old_realname = my_database.get_user_realname_by_id(arg_2)
                    my_database.update_realname_by_id(arg_3, arg_2)
                    return "Update: Real name changed from " + old_realname + " to " + str(arg_3)
                return "Try : $update balance id_user money_added ,or , $update name id_user new_name"
            elif check_item_exist(arg_2, my_database):
                if arg_1 == "quantity" and int(args[3])>=0:
                    old_quantity = int(my_database.get_item_quantity(arg_2))
                    my_database.update_quantity_by_name(int(arg_3), arg_2)
                    new_quantity = int(arg_3)
                    return "Update: Quantity changed from " + str(old_quantity) + " to " + str(new_quantity)
                elif arg_1 == "price" and float(args[3])>=0.0:
                    old_price = my_database.get_item_price(arg_2)
                    my_database.update_price_by_name(arg_2, arg_3)
                    return "Update: Price changed from " + str(old_price) + " ff to " + str(arg_3)+" ff"
                return "Just try : $update quantity item_name new_quantity ,or , $update price item_name new_price"
    if command == "delete" and bot.check_role("Bureau", message):
        arg_1 = args[1]
        if len(args) == 3:
            arg_2 = args[2]
            if arg_1 == "user" and check_user_exist(arg_2, my_database):
                name_delete_user = str(my_database.get_user_name_by_id(arg_2))
                my_database.delete_user_by_id(arg_2)
                return "You have deleted the following user: " + name_delete_user
            elif arg_1 == "item" and check_item_exist(arg_2, my_database):
                my_database.delete_item_by_name(arg_2)
                return "You have deleted the following item: " + str(arg_2)
        return "/!\ Delete: $delete user id_user ,or , $delete item item_name"


def check_user_exist(id, my_database):
    return my_database.user_exist_by_id(id)


def check_item_exist(name, my_database):
    return my_database.item_exist_by_name(name)


def affiche_balance(id_author, id, my_database):
    s = ""
    if id == id_author:
        s = "You have " + str(my_database.get_balance_by_id(id_author))
    else:
        s = str(my_database.get_user_name_by_id(id)) + " has " + str(my_database.get_balance_by_id(id))
    return s + " NPC coins (ff)"
