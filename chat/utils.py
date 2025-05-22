# chat/utils.py
from .models import ChatRoom, User

def get_or_create_private_chat(user1, user2):
    """
    Get or create a private chat room between two users.
    """
    # Sort usernames to ensure consistency
    usernames = sorted([user1.username, user2.username])
    room_name = f"private_{usernames[0]}_{usernames[1]}"

    # Check if a private chat room already exists
    room = ChatRoom.objects.filter(name=room_name, is_private=True).first()

    if not room:
        # Create a new private chat room
        room = ChatRoom.objects.create(name=room_name, is_private=True)
        room.participants.add(user1, user2)

    return room