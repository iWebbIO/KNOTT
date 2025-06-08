# KnoTT Bot - Advanced Discord Leveling System
## 🚀 A comprehensive leveling bot with achievements, rank roles, and advanced features

<div align="center">

[![Install to Discord](https://img.shields.io/badge/Discord-Bot-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=1005165227723214988&permissions=134294528&scope=applications.commands%20bot)
[![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 🌟 Features Overview

KnoTT Bot is a feature-rich Discord leveling system that transforms your server into an engaging community with:

### 🏆 **Achievement System**
- **14 Default Achievements** with automatic tracking
- **Bonus XP Rewards** for achievement completion
- **Progress-based Unlocks** for messages and levels
- **Beautiful Notifications** when achievements are earned

### 🎭 **Rank Roles System**
- **Automatic Role Assignment** based on user levels
- **Flexible Configuration** - set roles for any level
- **Bulk Synchronization** for existing members
- **Admin-friendly Management** with easy commands

### 📊 **Advanced Leveling**
- **Global & Server-specific** leaderboards
- **Customizable XP multipliers** (0.1x - 5.0x)
- **78+ Unique Rank Titles** from "New Member" to "Discord God"
- **Anti-spam Protection** with configurable cooldowns

### ⚙️ **Server Customization**
- **Dedicated Level-up Channels** for announcements
- **Toggle Notifications** on/off per server
- **Independent Settings** for each server
- **Comprehensive Admin Controls**

---

## 🎯 Quick Start

### 1. **Invite the Bot**
[**Click here to add KnoTT to your server**](https://discord.com/api/oauth2/authorize?client_id=1005165227723214988&permissions=134294528&scope=applications.commands%20bot)

### 2. **Start Chatting**
Users automatically gain XP by sending messages (1 XP per message by default)

### 3. **Configure Your Server**
Use admin commands to customize XP rates, set up rank roles, and configure announcements

---

## 📋 Commands Reference

### 📊 **Level Commands**
| Command | Description | Usage |
|---------|-------------|-------|
| `klevel` | View your current level, XP, and rank | `klevel` |
| `kboard` | Display server or global leaderboard | `kboard` |
| `krank [user]` | Check rank position | `krank @user` |

### 🏆 **Achievement Commands**
| Command | Description | Usage |
|---------|-------------|-------|
| `kachievements [user]` | View earned achievements | `kachievements @user` |
| `kachievementlist` | See all available achievements | `kachievementlist` |

### 🎭 **Rank Role Commands** *(Admin Only)*
| Command | Description | Usage |
|---------|-------------|-------|
| `kaddrankrole <level> <@role>` | Add rank role for specific level | `kaddrankrole 10 @Member` |
| `kremoverankrole <level>` | Remove rank role | `kremoverankrole 10` |
| `krankroles` | View configured rank roles | `krankroles` |
| `ksyncranks` | Sync all user roles | `ksyncranks` |

### ⚙️ **Server Admin Commands** *(Admin Only)*
| Command | Description | Usage |
|---------|-------------|-------|
| `ksetxp <multiplier>` | Set XP multiplier (0.1x - 5.0x) | `ksetxp 1.5` |
| `klevelchannel [#channel]` | Set level-up announcement channel | `klevelchannel #levels` |
| `ktoggleannouncements` | Toggle level-up announcements | `ktoggleannouncements` |
| `kserverconfig` | View server settings | `kserverconfig` |

### ℹ️ **Info Commands**
| Command | Description | Usage |
|---------|-------------|-------|
| `kmany` | Check server count | `kmany` |
| `kwhat` | Show help information | `kwhat` |

---

## 🏆 Achievement System

### **Message-based Achievements**
- **First Steps** - Send your first message (+10 XP)
- **Chatterbox** - Send 100 messages (+50 XP)
- **Conversationalist** - Send 500 messages (+100 XP)
- **Social Butterfly** - Send 1,000 messages (+200 XP)
- **Community Leader** - Send 5,000 messages (+500 XP)
- **Legend** - Send 10,000 messages (+1,000 XP)

### **Level-based Achievements**
- **Getting Started** - Reach level 5 (+25 XP)
- **Rising Star** - Reach level 10 (+50 XP)
- **Experienced** - Reach level 25 (+100 XP)
- **Veteran** - Reach level 50 (+250 XP)
- **Elite** - Reach level 100 (+500 XP)
- **Master** - Reach level 200 (+1,000 XP)
- **Grandmaster** - Reach level 300 (+2,000 XP)
- **Legendary** - Reach level 375 (+5,000 XP)

---

## 🎭 Rank Roles Setup

### **Quick Setup Example**
```
kaddrankrole 5 @Newcomer
kaddrankrole 10 @Regular
kaddrankrole 25 @Veteran
kaddrankrole 50 @Elite
kaddrankrole 100 @Legend
```

### **Features**
- ✅ **Automatic Assignment** - Roles given instantly on level up
- ✅ **Retroactive Sync** - Apply roles to existing members
- ✅ **Multiple Roles** - Users can have multiple rank roles
- ✅ **Easy Management** - Simple commands for configuration

---

## 🔧 Technical Details

### **Database Structure**
- **SQLite Database** with async operations
- **Optimized Queries** for fast performance
- **Data Integrity** with proper relationships
- **Automatic Migrations** for updates

### **Performance Features**
- **XP Cooldown System** prevents spam (60s default)
- **Efficient Caching** for guild settings
- **Batch Operations** for role synchronization
- **Error Handling** with comprehensive logging

### **Security & Privacy**
- **No Data Collection** beyond necessary bot functions
- **Server-isolated Data** - each server's data is separate
- **Secure Token Handling** with environment variables
- **Rate Limiting** to prevent abuse

---

## 🚀 Self-Hosting Setup

### **Prerequisites**
- Python 3.8 or higher
- Discord Bot Token
- Basic command line knowledge

### **Installation Steps**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/iWebbIO/KNOTT.git
   cd KNOTT
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and settings
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

### **Environment Configuration**
```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_NAME=KnoTT
OWNER_ID=your_discord_id

# XP System Settings
XP_PER_MESSAGE=1
XP_COOLDOWN=60
LEVEL_UP_BASE=50
COMMAND_PREFIX=k

# Database
DATABASE_NAME=knott.db
```

---

## 📁 Project Structure

```
KNOTT/
├── main.py                 # Main bot file
├── database.py            # Database management
├── getrank.py            # Rank title system
├── botsettings.py        # Configuration loader
├── commands/             # Command modules
│   ├── admin.py         # Admin commands
│   ├── achievements.py  # Achievement system
│   └── roles.py         # Rank roles system
├── requirements.txt      # Dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch** (`git checkout -b feature/amazing-feature`)
3. **Commit Changes** (`git commit -m 'Add amazing feature'`)
4. **Push to Branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test your changes thoroughly
- Update documentation as needed

---

## 📊 Statistics & Analytics

### **Tracking Features**
- **Message Count** - Total messages per user
- **Level Progression** - Track user advancement
- **Achievement Progress** - Monitor completion rates
- **Server Activity** - Leaderboard rankings
- **Role Distribution** - Rank role statistics

---

## 🛠️ Advanced Configuration

### **XP Multiplier Examples**
- `ksetxp 0.5` - Slower progression (50% XP)
- `ksetxp 1.0` - Default rate (100% XP)
- `ksetxp 2.0` - Double XP events (200% XP)
- `ksetxp 5.0` - Maximum boost (500% XP)

### **Channel Configuration**
- Set dedicated level-up channels for cleaner chat
- Toggle announcements for quieter servers
- Configure per-server settings independently

---

## 🔍 Troubleshooting

### **Common Issues**

**Bot not responding?**
- Check bot permissions (Send Messages, Embed Links)
- Verify bot is online and properly configured
- Ensure correct command prefix

**Roles not being assigned?**
- Check bot role hierarchy (bot role must be above assigned roles)
- Verify "Manage Roles" permission
- Run `ksyncranks` to fix existing users

**Achievements not working?**
- Database may need initialization
- Check for error messages in console
- Restart bot if necessary

---

## 📞 Support & Community

### **Get Help**
- **GitHub Issues** - Report bugs and request features
- **Discord Support** - Join our support server
- **Documentation** - Check this README for detailed info

### **Links**
- [Bot Invitation](https://discord.com/api/oauth2/authorize?client_id=1005165227723214988&permissions=134294528&scope=applications.commands%20bot)
- [GitHub Repository](https://github.com/iWebbIO/KNOTT)
- [Issue Tracker](https://github.com/iWebbIO/KNOTT/issues)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Discord.py** - The amazing Python library for Discord bots
- **SQLite** - Reliable database engine
- **Contributors** - Everyone who helped improve KnoTT Bot
- **Community** - Users who provide feedback and suggestions

---

<div align="center">

**KnoTT Bot - Making Discord communities more engaging, one level at a time!** 🎮

*Built with ❤️ by the KnoTT Team*

</div>
