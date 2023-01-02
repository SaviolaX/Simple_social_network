from django.urls import reverse, resolve

from chat.views import (ChatRoomView, MyChatsListView, DeleteChatView, CreateRoomView)

def test_chat_room_url():
    assert resolve(reverse('chat_room',
                           kwargs={'pk':
                                   1})).func.view_class == ChatRoomView
    
def test_my_chats_list_url():
    assert resolve(reverse('my_rooms')).func.view_class == MyChatsListView
    
def test_delete_chat_room_url():
    assert resolve(reverse('del_room',
                           kwargs={'pk':
                                   1})).func.view_class == DeleteChatView
    
def test_create_room_url():
    assert resolve(reverse('create_room')).func.view_class == CreateRoomView

