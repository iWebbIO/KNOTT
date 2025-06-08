import discord
from discord.ext import commands
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DatabaseManager()
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addrankrole(self, ctx, level: int, role: discord.Role):
        try:
            await self.db_manager.add_rank_role(ctx.guild.id, level, role.id)
            
            embed = discord.Embed(
                title="Rank Role Added",
                description=f"Users who reach level {level} will now receive the {role.mention} role!",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in addrankrole command: {e}")
            await ctx.send("An error occurred while adding the rank role.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removerankrole(self, ctx, level: int):
        try:
            await self.db_manager.remove_rank_role(ctx.guild.id, level)
            
            embed = discord.Embed(
                title="Rank Role Removed",
                description=f"Rank role for level {level} has been removed.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in removerankrole command: {e}")
            await ctx.send("An error occurred while removing the rank role.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rankroles(self, ctx):
        try:
            rank_roles = await self.db_manager.get_rank_roles(ctx.guild.id)
            
            if not rank_roles:
                embed = discord.Embed(
                    title="No Rank Roles Configured",
                    description="Use `kaddrankrole <level> <@role>` to add rank roles.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="Configured Rank Roles",
                description="Users automatically receive these roles when reaching the specified levels:",
                color=discord.Color.blue()
            )
            
            role_list = []
            for level, role_id in rank_roles:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_list.append(f"Level {level}: {role.mention}")
                else:
                    role_list.append(f"Level {level}: Role not found (ID: {role_id})")
            
            embed.add_field(
                name="Rank Roles",
                value="\n".join(role_list),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in rankroles command: {e}")
            await ctx.send("An error occurred while retrieving rank roles.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def syncranks(self, ctx):
        try:
            rank_roles = await self.db_manager.get_rank_roles(ctx.guild.id)
            if not rank_roles:
                await ctx.send("No rank roles configured for this server.")
                return
            
            leaderboard = await self.db_manager.get_leaderboard(ctx.guild.id, limit=1000)
            
            synced_count = 0
            for user_id, level, xp, total_messages in leaderboard:
                member = ctx.guild.get_member(user_id)
                if not member:
                    continue
                
                earned_roles = []
                for role_level, role_id in rank_roles:
                    if level >= role_level:
                        role = ctx.guild.get_role(role_id)
                        if role:
                            earned_roles.append(role)
                
                for role in earned_roles:
                    if role not in member.roles:
                        try:
                            await member.add_roles(role, reason="Rank role sync")
                            synced_count += 1
                        except discord.Forbidden:
                            logger.warning(f"Cannot add role {role.name} to {member.display_name}")
                        except Exception as e:
                            logger.error(f"Error adding role to {member.display_name}: {e}")
            
            embed = discord.Embed(
                title="Rank Sync Complete",
                description=f"Synced roles for {synced_count} users based on their current levels.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in syncranks command: {e}")
            await ctx.send("An error occurred while syncing ranks.")

async def setup(bot):
    await bot.add_cog(RoleCommands(bot))
