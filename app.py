def render_rich_content(content):
    emoji_map = {
        ":smile:": "😊", ":thinking:": "🤔", ":wave:": "👋", ":+1:": "👍", ":rocket:": "🚀",
        ":fire:": "🔥", ":star:": "⭐", ":heart:": "❤️", ":zap:": "⚡", ":bulb:": "💡",
        ":check_mark:": "✅", ":x_mark:": "❌", ":warning:": "⚠️", ":information_source:": "ℹ️",
        ":robot:": "🤖", ":brain:": "🧠", ":scroll:": "📜", ":book:": "📖", ":sparkles:": "✨",
        ":cat:": "🐱", ":dog:": "🐶", ":earth_americas:": "🌎", ":sun_with_face:": "🌞",
        ":cloud:": "☁️", ":hourglass:": "⌛", ":alarm_clock:": "⏰", ":calendar:": "📅",
        ":link:": "🔗", ":computer:": "💻", ":mobile_phone:": "📱", ":camera:": "📸",
        ":musical_note:": "🎵", ":art:": "🎨", ":pencil2:": "✏️", ":memo:": "📝",
        ":folder:": "📁", ":bar_chart:": "📊", ":money_bag:": "💰", ":gem:": "💎",
        ":key:": "🔑", ":lock:": "🔒", ":unlock:": "🔓", ":shield:": "🛡️",
        ":exclamation:": "❗", ":question:": "❓", ":arrow_up:": "⬆️", ":arrow_down:": "⬇️",
        ":speech_balloon:": "💬", ":eyes:": "👀", ":fist:": "✊", ":clap:": "👏",
        ":pray:": "🙏", ":handshake:": "🤝", ":muscle:": "💪", ":walking:": "🚶",
        ":running:": "🏃", ":dancer:": "💃", ":family:": "👪", ":kiss:": "💋",
        ":rose:": "🌹", ":tulip:": "🌷", ":cherry_blossom:": "🌸", ":blossom:": "🌼",
        ":ocean:": "🌊", ":droplet:": "💧", ":snowflake:": "❄️", ":boom:": "💥",
        ":zzz:": "💤"
    }
    for code, emoji in emoji_map.items():
        content = content.replace(code, emoji)
    
    # Existing image rendering logic
    if content.startswith("<img>"):
        return f'<img src="{content[5:]}" alt="Image">'
    return content