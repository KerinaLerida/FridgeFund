import bot
import database
import logging


def achat(my_database, id_user, item_name, nb):  # achat => si quantity >=1 et balance >=price_item
    item_price = float(my_database.get_item_price(item_name))
    balance = float(my_database.get_balance_by_id(id_user))
    item_quantity = float(my_database.get_item_quantity(item_name))
    nb = float(nb)

    if item_quantity >= nb:
        if balance >= int(nb * item_price):
            my_database.update_quantity_by_name(item_quantity - nb, item_name)
            my_database.update_balance_by_id(-1 * (nb * item_price), id_user)
            return "" + str(nb) + " " + item_name + " vendu !"
        else:

            return "Ta besace est bien légére, pas de " + item_name + " pour toi !"
    else:
        return "Plus de stock pour ce produit :("

def help_command(message, msg_bureau, msg_cotisant):
    s = ""
    if bot.check_role("Bureau", message):
        s = " ,or , " + msg_bureau
    return "Just try: " + msg_cotisant + s

def handle_response(message, strmessage, my_database):
    p_message = strmessage.lower()
    author = message.author  # name
    id_author = author.id
    print("Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")
    logging.info("Message sent by " + str(message.author) + " : \"" + message.content + "\" [ id: " + str(id_author) + " ]")

    # Crée : un wallet si l'user n'en a pas
    name_author = str(author)
    if not check_user_exit(id_author, my_database):
        my_database.insert_user(id_author, name_author, name_author, 0)
        return "Your wallet has been created!"
    elif name_author != my_database.get_user_name_by_id(id_author):  # MAJ : name/pseudo user
        my_database.update_name_by_id(name_author, id_author)

    # Parsing commands and arguments
    args = p_message.split()

    command = args[0]  # Command word
    if command == 'hello' and len(args) == 1:
        return 'Hey there!'

    if command == "help":
        if len(args) == 1:
            command_summary = """
Commandes du bot FridgeFund:

$hello : Etre poli(e) avec FridgeFund
$info : Affiche des informations sur le bot
$ff : Affiche la liste des utilisateurs
$help : Affiche le message d'aide
$user : Vérifie la possetion d'un compte (wallet)
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
$update balance <id_utilisateur> <montant> : Met à jour le solde d'un utilisateur
$update name <id_utilisateur> <nouveau_nom> : Met à jour le nom réel d'un utilisateur
$update quantity <nom_item> <nouvelle_quantité> : Met à jour la quantité d'un item
$update price <nom_item> <nouveau_prix> : Met à jour le prix d'un item
$delete user <id_utilisateur> : Supprime un utilisateur
$delete item <nom_item> : Supprime un item
"""
            return supremetie_bureau

    if command == "user" and check_user_exit(id_author, my_database):
        return "You already have a wallet.."

    if command == "wallet":
        if len(args) == 1:
            return affiche_balance(None, id_author, my_database)
        elif len(args) == 2 and bot.check_role("Bureau", message) and check_user_exit(args[1], my_database):
            return affiche_balance(id_author, args[1], my_database)

        return help_command(message, "$wallet id_user", "$wallet")

    if command == "items":
        if len(args) == 1:
            data = my_database.get_all_items()
            s = "Boissons et nourriture disponibles :\n\n"
            for item in data:
                name_, quantity_, price_ = item
                s += f"{name_} | Quantité: {quantity_}, Prix: {price_} ff\n"
            return s
        return "Just try : $items , or, $item item_name"

    if command == "ff":
        if len(args) == 1:
            data = my_database.get_all_users()
            s = "Classement des Chamy_databaseotteurs :\n\n"
            for user in data:
                id_, name_, rname_, balance_ = user
                s += f"Id: {id_} | Pseudo: {name_}, Prénom: {rname_}, Solde: {balance_} ff\n"
            return s
        return "Just try : /ff 15 , pour augmenter ton QI"

    if command == "info":
        if len(args) == 1:
            return "My name is FridgeFund, some people prefer to call me as Chamy_databaseot. I can help you $help , to spend money in the fridge for drinks and food!"

    if command == "item":
        if len(args) == 2 and my_database.item_exist_by_name(args[1]):
            name, quantity, price = my_database.get_item_by_name(args[1])
            return f"{name} | Quantité: {quantity}, Prix: {price} ff"
        return "Just try : $item item_name , or, $items ,to see all items"

    if command == "buy":  # regarder si solde et quantité sont good ou pas
        arg_1 = args[1]
        if len(args) == 2 and check_item_exist(arg_1, my_database):
            return achat(my_database, id_author, arg_1, 1)
        elif len(args) == 3 and check_item_exist(arg_1, my_database):
            return achat(my_database, id_author, arg_1, args[2])
        elif len(args) == 4 and bot.check_role("Bureau", message) and check_user_exit(args[3], my_database):
            return achat(my_database, args[3], arg_1, args[2])
        # refaire msg bureau ou pas
        return help_command(message, "$buy item_name quantity_taken id_user",
                            "$buy item_name ,or , $buy item_name quantity_taken")



    # *************************************** Bureau suprématie *********************************************
    if command == "create" and bot.check_role("Bureau", message):
        arg_2 = args[2]
        if len(args) == 5:
            arg_3 = args[3]
            arg_4 = args[4]
            if args[1] == "user" and not check_user_exit(arg_2, my_database):
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

            if check_user_exit(arg_2, my_database):
                if arg_1 == "balance":
                    old_balance = my_database.get_balance_by_id(arg_1)
                    my_database.update_balance_by_id(arg_1, arg_3)
                    return "Update: " + affiche_balance(id_author, arg_1, my_database) + "(Old balance: " + str(
                        old_balance) + " ) "
                elif arg_1 == "name":
                    old_realname = my_database.get_user_realname_by_id(arg_1)
                    my_database.get_user_realname_by_id(arg_2, arg_1)
                    return "Update: Real name changed from " + old_realname + " to " + str(arg_3)
                return "Try : $update balance id_user argent_ajouté ,or , $update name id_user new_name"
            elif check_item_exist(arg_2, my_database):
                if arg_1 == "quantity":
                    old_quantity = int(my_database.get_item_quantity(arg_2))
                    my_database.update_quantity_by_name(int(arg_3), arg_2)
                    new_quantity = old_quantity + int(arg_3)
                    return "Update: Quantity changed from " + str(old_quantity) + " to " + str(new_quantity)
                elif arg_1 == "price":
                    old_price = my_database.get_item_price(arg_2)
                    my_database.update_price_by_name(arg_2, arg_3)
                    return "Update: Price changed from " + str(old_price) + " to " + str(arg_3)
                return "Just try : $update quantity item_name new_quantity ,or , $update price item_name new_price"
    if command == "delete" and bot.check_role("Bureau", message):
        arg_1 = args[1]
        if len(args) == 3:
            arg_2 = args[2]
            if arg_1 == "user" and check_user_exit(arg_2, my_database):
                name_delete_user = str(my_database.get_user_name_by_id(arg_2))
                my_database.delete_user_by_id(arg_2)
                return "You have deleted the following user: " + name_delete_user
            elif arg_1 == "item" and check_item_exist(arg_2, my_database):
                my_database.delete_item_by_name(arg_2)
                return "You have deleted the following item: " + str(arg_2)
        return "/!\ Delete: $delete user id_user ,or , $delete item item_name"


def check_user_exit(id, my_database):
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
