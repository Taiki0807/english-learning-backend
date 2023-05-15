from typing import List

import jwt
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from rest_framework import generics, permissions, response, status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt import exceptions as jwt_exp, views as jwt_views

from .models import Account
from .serializers import AccountSerializer


class TokenObtainView(jwt_views.TokenObtainPairView):
    """
    JWTをCookieにセットして送る
    """

    def post(self, request, *args, **kwargs):
        # シリアライザーでバリデーションを行う．
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except jwt_exp.TokenError as e:
            raise jwt_exp.InvalidToken(e.args[0])

        # レスポンスオブジェクトの作成
        res = response.Response(
            data={
                "success": 1,
            },
            status=status.HTTP_200_OK,
        )

        # Cookieの設定
        res.set_cookie(
            key="access_token",
            value=serializer.validated_data["access"],
            # max_age=60 * 60 * 24,
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
        )
        res.set_cookie(
            key="refresh_token",
            value=serializer.validated_data["refresh"],
            # max_age=60 * 60 * 24 * 30,
            expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
        )

        # csrftokenを設定
        get_token(request)
        return res


def refresh_get(request):
    """
    リフレッシュトークンを返す
    """
    try:
        rt = request.COOKIES["refresh_token"]
        return JsonResponse({"refresh": rt}, safe=False)
    except Exception as e:
        print(e)
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(jwt_views.TokenRefreshView):
    """
    リフレッシュトークンを使って新しいアクセストークンを作成する
    """

    def post(self, request, *args, **kwargs):
        # シリアライザーによるバリデーション
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except jwt_exp.TokenError as e:
            raise jwt_exp.InvalidToken(e.args[0])

        # レスポンスオブジェクトの作成
        res = response.Response(status=status.HTTP_200_OK)
        res.set_cookie(
            key="access_token",
            value=serializer.validated_data["access"],
            # max_age=60 * 24 * 24 * 30,
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
        )
        return res


class TokenDeleteView(APIView):
    """
    Cookieに保存しているTokenを削除する
    """

    permission_classes: List[type] = [permissions.AllowAny]
    authentication_classes: List[type] = []

    def get(self, request, *args, **kwargs):
        res = response.Response(status=status.HTTP_200_OK)
        res.delete_cookie("access_token")
        res.delete_cookie("refresh_token")
        return res


class AccountRegister(generics.CreateAPIView):
    """
    アカウント登録を行う
    """

    permission_classes: List[type] = [permissions.AllowAny]
    authentication_classes: List[type] = []
    serializer_class = AccountSerializer
    queryset = Account.objects.all()

    def perform_create(self, serializer):
        queryset = Account.objects.filter(username=self.request.data["username"])
        if queryset.exists():
            raise ValidationError("This username has already used")

        queryset = Account.objects.filter(email=self.request.data["email"])
        if queryset.exists():
            raise ValidationError("This email has already used")
        serializer.save()


class GetAccountInfo(APIView):
    """
    アカウント情報を取得する
    """

    permission_classes: List[type] = [permissions.AllowAny]

    def get(self, request):
        jwt_token = request.COOKIES.get("access_token")
        if not jwt_token:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
            loginuser = Account.objects.get(id=payload["user_id"])
            # アクティブチェック
            if loginuser.is_active:
                response = AccountSerializer(loginuser)
                return Response(response.data, status=status.HTTP_200_OK)
            return Response({"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.DecodeError:
            return Response({"error": "Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
        except Account.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)


class GetAccountStatus(APIView):
    permission_classes: List[type] = [permissions.AllowAny]

    def get(self, request):
        # 認証に成功した場合は、ユーザーオブジェクトがrequest.userに設定される
        if "access_token" in request.COOKIES:
            if request.user is not None:
                return Response({"status": 1}, status=status.HTTP_200_OK)
            else:
                return Response({"status": 0}, status=status.HTTP_200_OK)
        else:
            return Response({"status": 0}, status=status.HTTP_200_OK)


class UserView(ListAPIView):
    queryset = Account.objects.all().order_by("username")
    serializer_class = AccountSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        excludeUsersArr: List[type] = []
        try:
            excludeUsers = self.request.query_params.get("exclude")
            if excludeUsers:
                userIds = excludeUsers.split(",")
                for userId in userIds:
                    excludeUsersArr.append(int(userId))
        except ValueError:
            return []
        return super().get_queryset().exclude(id__in=excludeUsersArr)


class ImageRegisterAPIView(APIView):
    parser_classes: List[type] = [FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        upload_file = request.data["image"]
        file_name = default_storage.save(upload_file.name, upload_file)
        object_url = f"{default_storage.url(file_name)}"
        return Response({"success": 1, "file": {"url": object_url}}, status.HTTP_201_CREATED)
