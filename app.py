from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# =================================================================
# ⚙️ ZONA DE CONFIGURACIÓN (FÁCIL DE EDITAR PARA OTRAS NACIONES)
# Formato: "ID_DEL_ROL_DE_DISCORD": "Nombre del Team en Roblox"
# Importante: Pon los roles de mayor rango arriba.
# =================================================================
ROLES_A_TEAMS = {
    "1555292991265054750": "Afiliado Nacional",
    # Para añadir más, solo sigue este formato:
    # "123456789012345678": "Fuerzas Armadas",
    # "987654321098765432": "Ministerio del Interior",
}
# =================================================================

# Credenciales que se configurarán en Render de forma segura
GUILD_ID = os.environ.get("GUILD_ID")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
BLOXLINK_KEY = os.environ.get("BLOXLINK_KEY")

@app.route('/obtener_equipo')
def obtener_equipo():
    roblox_id = request.args.get('robloxId')
    if not roblox_id:
        return jsonify({"team": "Invitado"}), 400

    try:
        # 1. Preguntar a Bloxlink cuál es el ID de Discord de este jugador
        url_bloxlink = f"https://api.blox.link/v4/public/guilds/{GUILD_ID}/roblox-to-discord/{roblox_id}"
        headers_blox = {"Authorization": BLOXLINK_KEY}
        resp_blox = requests.get(url_bloxlink, headers=headers_blox)
        
        if resp_blox.status_code != 200:
            return jsonify({"team": "Invitado"}) # No está verificado
            
        discord_id = resp_blox.json().get("discordID")

        # 2. Preguntar a Discord qué roles tiene este usuario en tu servidor
        url_discord = f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{discord_id}"
        headers_discord = {"Authorization": f"Bot {DISCORD_TOKEN}"}
        resp_discord = requests.get(url_discord, headers=headers_discord)
        
        if resp_discord.status_code != 200:
            return jsonify({"team": "Invitado"}) # No está en el servidor de Discord

        roles_del_usuario = resp_discord.json().get("roles", [])

        # 3. Asignar el equipo según la configuración de arriba
        for id_rol, nombre_equipo in ROLES_A_TEAMS.items():
            if id_rol in roles_del_usuario:
                return jsonify({"team": nombre_equipo})

        return jsonify({"team": "Invitado"}) # Está en el server pero no tiene roles asignados

    except Exception as e:
        return jsonify({"team": "Invitado"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))