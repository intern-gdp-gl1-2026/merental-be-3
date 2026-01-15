from rest_framework.views import APIView

class UserListCreateView(APIView):
    def post(self, request):
        # urutan eksekusi
        # 1. validasi dengan serializer
        # 2. buat menjadi dto
        # 3. Data dari dto dimasukkan ke dalam usecase.execute
        # 4. response denan serializer
        pass