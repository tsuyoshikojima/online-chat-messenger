import secrets  # 機密を扱うために安全な乱数を生成
from typing import Any


# Exceptionを継承した独自例外
# 後々、ルーム作成に失敗した場合に、クライアントに対応するステータスコードを返す必要があるために
# エラーを明確にしておく。
class RoomAlreadyExistsError(Exception):
    """作成したいルーム名が既に存在するときに投げる例外"""
    pass


class RoomNotFoundError(Exception):
    """参加したいルームが存在しない場合に投げる例外"""
    pass


class InvalidRoomPasswordError(Exception):
    """パスワードが一致しない場合に投げる例外"""
    pass


class RoomManager:
    """ルームに関する情報と処理"""

    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, Any]] = {}    # RoomManagerのインスタンス生成時はルームが存在しないので空の辞書とする

    def create_room(
            self, 
            room_name: str, 
            user_name: str, 
            ip_address: str,
            password: str | None = None  # strまたはNoneを受け取る。初期値はNone
    ) -> str:

        if not user_name.strip():
            raise ValueError("ユーザ名がないです。")

        if room_name in self._rooms:
            raise RoomAlreadyExistsError("既に存在するルーム名です。")

        host_token = secrets.token_urlsafe(32)  # ルーム作成者はhostとして扱うためhost_tokenを生成

        self._rooms[room_name] = {
            "host_token" : host_token,      # ホストトークンとパスワードはホストが作成したものであるが、ルーム固有の情報として管理する
            "password" : password,

            "members" : {
                host_token : {      # UDPパケットのボディは room_name | token | message　のためトークンをキーとしてメンバーを管理する
                    "user_name" : user_name,
                    "ip_address" : ip_address,
                    "udp_address" : None        # UDPでは接続動作がないためクライアントごとにアドレスを把握しておく
                }                               # TCP接続を切断後にUDPを使用しtokenと一緒にmessageを送信してくるため、
            }                                   # tokenとUDPアドレスを紐付ける
        }

        return host_token  # クライアントにtokenを渡す必要があるため

    def join_room(
            self,
            room_name: str,
            user_name: str,
            ip_address: str,
            password: str | None
    ) -> str:
        
        if not user_name.strip():
            raise ValueError("ユーザー名がないです。")

        if room_name not in self._rooms:
            raise RoomNotFoundError("ルームが見つかりません。")

        room = self._rooms[room_name]

        # パスワードの確認
        if room["password"] is not None and room["password"] != password:
            raise InvalidRoomPasswordError("パスワードが一致しません。")

        user_token = secrets.token_urlsafe(32)

        room["members"][user_token] = {
            "user_name" : user_name,
            "ip_address" : ip_address,
            "udp_address" : None
        }

        return user_token



