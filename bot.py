import os
import requests
import discord
from discord import app_commands
from discord.ext import commands

# 1. Chargement sécurisé des clés d'API depuis l'environnement
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ZEFAME_API_KEY = os.getenv("ZEFAME_API_KEY")
HIKER_API_KEY = os.getenv("HIKER_API_KEY")

ZEFAME_URL = "https://zefame.com/api/v2"
HIKER_URL = "https://api.hikerapi.com/v2"

# 2. Initialisation du Bot Discord
class ZefameHikerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Synchronisation automatique des commandes slash avec Discord
        await self.tree.sync()
        print("[INFO] Commandes slash synchronisées avec succès.")

bot = ZefameHikerBot()

@bot.event
async def on_ready():
    print(f"[INFO] Bot connecté en tant que {bot.user.name} (ID: {bot.user.id})")

# ==========================================
# COMMANDES ZEFAME (SMM & SERVICES GRATUITS)
# ==========================================

@bot.tree.command(name="solde", description="Vérifie votre solde actuel sur Zefame")
async def solde(interaction: discord.Interaction):
    payload = {'key': ZEFAME_API_KEY, 'action': 'balance'}
    await interaction.response.defer(ephemeral=True)

    try:
        response = requests.post(ZEFAME_URL, data=payload, timeout=10).json()
        if 'balance' in response:
            await interaction.followup.send(f"💰 **Solde Zefame** : {response['balance']} {response.get('currency', 'USD')}")
        else:
            await interaction.followup.send("❌ Erreur : Impossible de récupérer le solde. Vérifiez votre clé API.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erreur technique : {e}")

@bot.tree.command(name="gratuits", description="Affiche la liste des services gratuits (Rate = 0)")
async def gratuits(interaction: discord.Interaction):
    payload = {'key': ZEFAME_API_KEY, 'action': 'services'}
    await interaction.response.defer()

    try:
        response = requests.post(ZEFAME_URL, data=payload, timeout=15).json()
        free_services = []

        if isinstance(response, list):
            for service in response:
                try:
                    rate = float(service.get('rate', 1))
                    name = service.get('name', '').lower()
                    if rate == 0.0 or 'free' in name:
                        free_services.append(
                            f"• **ID {service['service']}** : {service['name']} (Min: {service['min']} / Max: {service['max']})"
                        )
                except (ValueError, TypeError):
                    continue

        if free_services:
            # On limite l'affichage aux 10 premiers pour éviter de saturer le message Discord
            message = "🎁 **Services Gratuits / Free détectés :**\n" + "\n".join(free_services[:10])
            await interaction.followup.send(message)
        else:
            await interaction.followup.send("ℹ️ Aucun service gratuit trouvé via l'API pour le moment.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erreur lors de la récupération des services : {e}")

@bot.tree.command(name="commander", description="Passe une commande (payante ou gratuite via ID de service)")
@app_commands.describe(service_id="ID du service", lien="Lien cible (ex: URL de la vidéo)", quantite="Quantité")
async def commander(interaction: discord.Interaction, service_id: int, lien: str, quantite: int):
    payload = {
        'key': ZEFAME_API_KEY,
        'action': 'add',
        'service': service_id,
        'link': lien,
        'quantity': quantite
    }
    await interaction.response.defer()

    try:
        response = requests.post(ZEFAME_URL, data=payload, timeout=10).json()
        
        if 'order' in response:
            await interaction.followup.send(f"✅ Commande validée avec succès ! ID de commande : **{response['order']}**")
        elif 'error' in response:
            error_msg = response['error']
            if "not enough balance" in error_msg.lower():
                await interaction.followup.send("❌ **Solde insuffisant**. Utilisez la commande `/gratuits` pour trouver des options sans frais.")
            else:
                await interaction.followup.send(f"❌ Échec de la commande : {error_msg}")
        else:
            await interaction.followup.send("⚠️ Réponse inattendue de l'API Zefame.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erreur de communication avec l'API : {e}")

# ==========================================
# COMMANDE HIKERAPI
# ==========================================

@bot.tree.command(name="hiker_user", description="Récupère les informations d'un utilisateur via son ID HikerAPI")
@app_commands.describe(user_id="Identifiant numérique de l'utilisateur")
async def hiker_user(interaction: discord.Interaction, user_id: str):
    headers = {
        'accept': 'application/json',
        'x-access-key': HIKER_API_KEY
    }
    params = {'id': user_id}
    await interaction.response.defer()

    try:
        response = requests.get(f"{HIKER_URL}/user/by/id", headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            username = data.get('username', 'Inconnu')
            full_name = data.get('full_name', 'Non renseigné')
            await interaction.followup.send(f"👤 **Utilisateur HikerAPI trouvé** :\n- Pseudo : `{username}`\n- Nom complet : `{full_name}`")
        else:
            await interaction.followup.send(f"❌ Erreur HikerAPI (Code HTTP: {response.status_code})")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erreur de connexion à HikerAPI : {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("[ERREUR CRITIQUE] La variable d'environnement 'DISCORD_TOKEN' est manquante.")
    else:
        bot.run(DISCORD_TOKEN)
