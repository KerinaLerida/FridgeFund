import discord
from database import SimpleSQLiteDatabase

def create_embed(title, description, color):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

def check_role(name_role,msg):
    role_cheaking=discord.utils.get(msg.guild.roles, name=name_role)
    if role_cheaking in msg.author.roles:
        return True
    return False

def check_user_exit(id,mydatabase):
    return mydatabase.user_exist_by_id(id)

def check_item_exist(name,mydatabase):
    return mydatabase.item_exist_by_name(name)

def affiche_balance(id_author,id,mydatabase):
    s=""
    if(id==id_author):
        s="You have " + str(mydatabase.get_balance_by_id(id_author))
    else:
        s=str(mydatabase.get_user_name_by_id(id)) + " has "+ str(mydatabase.get_balance_by_id(id))
    return s+" NPC coins (ff)"

def achat(mydatabase,id_user,item_name,nb):  #achat => si quantity >=1 et balance >=price_item
    item_price=mydatabase.get_item_price(item_name)
    balance=mydatabase.get_balance_by_id(id_user)
    if mydatabase.get_item_quantity(item_name)>=nb and balance>=nb*item_price:
        mydatabase.update_quantity_by_name(item_name,-nb)
        mydatabase.update_balance_by_id(id_user,-nb*mydatabase.get_item_price(item_name))

def help_command(message,msg_bureau,msg_cotisant):
    s=""
    if check_role("Bureau",message):
        s=" ,or , "+msg_bureau
    return "Just try: "+msg_cotisant+s

# Send messages
async def send_message(message,user_message,mydatabase, is_private):
    try:
        response = handle_response(message,user_message,mydatabase)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = METTRE SON TOKEN
    client = discord.Client(intents=discord.Intents.all())
    mydatabase = SimpleSQLiteDatabase('my_database.db')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        #******************** DEBUG ********************
        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        id_user = str(message.author.id)

        # Debug printing
        print(f"{username} said: '{user_message}' ({channel})"+" [ id: "+id_user+" ]")
        #************************************************

        if message.channel.name == "🤖╿fridgefund":
            if check_role("Cotisant",message) : #Vérifie : Role Cotisant nécessaire
                # If the user message contains a '$' in front of the text, the bot will answer, else it wont
                if user_message[0] == '$':
                    user_message = user_message[1:]  # [1:] Removes the '?'
                    await send_message(message,user_message,mydatabase, is_private=False)
                else:
                    return

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)

def handle_response(message,strmessage,mydatabase):
    p_message = strmessage.lower()
    author = message.author #name
    id_author=author.id
    print("Message received.."+" [ id: "+str(id_author)+" ]")

    #Crée : un wallet si l'user n'en a pas
    name_author=str(author)
    if not check_user_exit(id_author,mydatabase):
        mydatabase.insert_user(id_author,name_author,name_author, 0)
        return "Your wallet has been created!"
    elif name_author!=mydatabase.get_user_name_by_id(id_author): #MAJ : name/pseudo user
        mydatabase.update_name_by_id(name_author,id_author)

    #Parsing commands and arguments
    args = p_message.split()

    command=args[0] #Command word
    if command=='hello' and len(args)==1:
        return 'Hey there!'

    if command=="help":
        if len(args)==1:
            command_summary = """
Commandes du bot FridgeFund:

$hello : Etre poli avec FridgeFund
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
        elif len(args)==2 and args[1]=="bureau" and check_role("Bureau",message):
            supremetie_bureau="""
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

    if command=="user" and check_user_exit(id_author,mydatabase):
        return "You already have a wallet.."

    if command=="wallet":
        if len(args)==1:
            return affiche_balance(None,id_author,mydatabase)
        elif len(args)==2 and check_role("Bureau",message) and check_user_exit(args[1],mydatabase):
            return affiche_balance(id_author,args[1],mydatabase)

        return help_command(message,"$wallet id_user","$wallet")

    if command=="items":
        if len(args)==1:
            data=mydatabase.get_all_items()
            s="Boissons et nourriture disponibles :\n\n"
            for item in data:
                name_,quantity_, price_ = item
                s+=f"{name_} | Quantité: {quantity_}, Prix: {price_} ff\n"
            return s
        return "Just try : $items , or, $item item_name"

    if command=="ff":
        if len(args)==1:
            data=mydatabase.get_all_users()
            s="Classement des ChadBotteurs :\n\n"
            for user in data:
                id_, name_,rname_, balance_ = user
                s+=f"Id: {id_} | Pseudo: {name_}, Prénom: {rname_}, Solde: {balance_} ff\n"
            return s
        return "Just try : /ff 15 , pour augmenter ton QI"

    if command=="info":
        if len(args)==1:
            return "My name is FridgeFund, some people prefer to call me as ChadBot. I can help you $help , to spend money in the fridge for drinks and food!"

    if command=="item":
        if len(args)==2 and mydatabase.item_exist_by_name(args[1]):
            name,quantity,price=mydatabase.get_item_by_name(args[1])
            return f"{name} | Quantité: {quantity}, Prix: {price} ff"
        return "Just try : $item item_name , or, $items ,to see all items"

    if command=="buy": #regarder si solde et quantité sont good ou pas
        p="Purchase made!"
        arg_1=args[1]
        if len(args)==2 and check_item_exist(arg_1,mydatabase):
            achat(mydatabase,id_author,arg_1,1)
            return p
        elif len(args)==3 and check_item_exist(arg_1,mydatabase):
            achat(mydatabase,id_author,arg_1,args[2])
            return p

        elif len(args)==4 and check_role("Bureau",message) and check_user_exit(args[3],mydatabase):
            achat(mydatabase,args[3],arg_1,args[2])
            return p

        #refaire msg bureau ou pas
        return help_command(message,"$buy item_name quantity_taken id_user","$buy item_name ,or , $buy item_name quantity_taken")

    #*************************************** Bureau suprématie *********************************************
    if command=="create" and check_role("Bureau",message):
        arg_2=args[2]
        if len(args)==5:
            arg_3=args[3]
            arg_4=args[4]
            if args[1]=="user" and not check_user_exit(arg_2,mydatabase):
                mydatabase.insert_user(int(arg_2),arg_3,arg_3, float(arg_4))
                return "You created the user : "+str(arg_3)
            elif args[1]=="item" and not check_item_exist(arg_2,mydatabase):
                mydatabase.insert_item(arg_2, arg_3, arg_4)
                return "You created the item : "+str(arg_2)
        return "Create: $create user id_user real_name balance ,or , $create item item_name quantity price"

    if command=="update" and check_role("Bureau",message):
        arg_1=args[1]
        if len(args)==4:
            arg_2=args[2]
            arg_3=args[3]

            if check_user_exit(arg_2,mydatabase):
                if arg_1=="balance" :
                    old_balance=mydatabase.get_balance_by_id(arg_1)
                    mydatabase.update_balance_by_id(arg_1,arg_3)
                    return "Update: "+affiche_balance(id_author, arg_1, mydatabase)+"(Old balance: "+str(old_balance)+" ) "
                elif arg_1=="name" :
                    old_realname=mydatabase.get_user_realname_by_id(arg_1)
                    mydatabase.get_user_realname_by_id(arg_2,arg_1)
                    return "Update: Real name changed from "+old_realname+" to "+str(arg_3)
                return "Try : $update balance id_user argent_ajouté ,or , $update name id_user new_name"
            elif check_item_exist(arg_2,mydatabase):
                if arg_1=="quantity":
                    old_quantity=str(mydatabase.get_item_quantity(arg_2))
                    mydatabase.update_quantity_by_name(int(arg_3),arg_2)
                    new_quantity=old_quantity+arg_3
                    return "Update: Quantity changed from "+old_quantity+" to "+str(new_quantity)
                elif arg_1=="price":
                    old_price=mydatabase.get_item_price(arg_2)
                    mydatabase.update_price_by_name(arg_2,arg_3)
                    return "Update: Price changed from "+str(old_price)+" to "+str(arg_3)
                return "Just try : $update quantity item_name new_quantity ,or , $update price item_name new_price"

    if command=="delete" and check_role("Bureau",message):
        arg_1=args[1]
        if len(args)==3:
            arg_2=args[2]
            if arg_1=="user"and check_user_exit(arg_2,mydatabase):
                name_delete_user=str(mydatabase.get_user_name_by_id(arg_2))
                mydatabase.delete_user_by_id(arg_2)
                return "You have deleted the following user: "+name_delete_user
            elif arg_1=="item" and check_item_exist(arg_2,mydatabase):
                mydatabase.delete_item_by_name(arg_2)
                return "You have deleted the following item: "+str(arg_2)
        return "/!\ Delete: $delete user id_user ,or , $delete item item_name"
