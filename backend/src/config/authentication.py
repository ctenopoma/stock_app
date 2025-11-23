"""
カスタム認証クラス
開発環境用のCSRF免除SessionAuthentication
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    CSRF検証を行わないSessionAuthentication
    開発環境でクロスオリジンリクエストをテストする際に使用
    
    注意: 本番環境では使用しないでください
    """
    def authenticate(self, request):
        """セッション認証を実行"""
        print(f"[DEBUG] CsrfExemptSessionAuthentication.authenticate called")
        print(f"[DEBUG] session_key: {request.session.session_key}")
        print(f"[DEBUG] cookies: {request.COOKIES.keys()}")
        # request.userにアクセスすると無限再帰するので削除
        
        result = super().authenticate(request)
        print(f"[DEBUG] authenticate result: {result}")
        return result
    
    def enforce_csrf(self, request):
        """CSRF検証をスキップ"""
        print(f"[DEBUG] CsrfExemptSessionAuthentication.enforce_csrf - skipped")
        return  # CSRF検証をスキップ
