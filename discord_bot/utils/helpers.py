from typing import Union
import discord

def get_member(guild: discord.Guild, member_id: Union[int, str]) -> discord.Member:
    """Helper function to get member from guild"""
    try:
        return guild.get_member(int(member_id))
    except ValueError:
        return None

def format_message(message: str) -> str:
    """Helper function to format messages"""
    return message.strip()
