from django.urls import path

from .views import CreateRoomView, ChatRoomView, DeleteChatView, MyChatsListView

urlpatterns = [
    path('create/', CreateRoomView.as_view(), name='create_room'),
    path('my_rooms/', MyChatsListView.as_view(), name='my_rooms'),
    path('<int:pk>/', ChatRoomView.as_view(), name='chat_room'),
    path('<int:pk>/delete/', DeleteChatView.as_view(), name='del_room'),
]