"""
Google OAuth para Streamlit.
Localmente: lê credenciais de client_secret_streamlit.json
Streamlit Cloud: lê de st.secrets (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI)
Restringe acesso a @gocase.com e @gobeaute.com.
"""
import json
import base64
import urllib.parse
import streamlit as st
import httpx
from pathlib import Path

ALLOWED_DOMAINS = {"gocase.com", "gobeaute.com", "gobeaute.com.br"}
_CREDS_FILE = Path(__file__).parent / "client_secret_streamlit.json"


def _get_creds() -> tuple[str, str, str]:
    """Retorna (client_id, client_secret, redirect_uri). Tenta st.secrets primeiro."""
    # ── Streamlit Cloud ──────────────────────────────────────────────────────
    try:
        client_id     = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        redirect_uri  = st.secrets["REDIRECT_URI"]
        return client_id, client_secret, redirect_uri
    except Exception:
        pass

    # ── Desenvolvimento local (JSON) ─────────────────────────────────────────
    if _CREDS_FILE.exists():
        data = json.loads(_CREDS_FILE.read_text(encoding="utf-8"))
        web  = data["web"]
        return web["client_id"], web["client_secret"], "http://localhost:8501"

    raise RuntimeError(
        "Credenciais Google não encontradas.\n"
        "Local: adicione client_secret_streamlit.json\n"
        "Cloud: configure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET e REDIRECT_URI em st.secrets"
    )


# ── Ponto de entrada ──────────────────────────────────────────────────────────
def login_required() -> None:
    """
    Coloque logo após st.set_page_config() no app.py.
    Para a execução e exibe login se o usuário não estiver autenticado.
    """
    if st.session_state.get("authenticated"):
        _render_user_badge()
        return

    params = st.query_params
    if "code" in params:
        _, _, redirect_uri = _get_creds()
        email = _exchange_code(params["code"], redirect_uri)
        if not email:
            _show_error("Falha na autenticação Google. Tente novamente.")
            return

        domain = email.split("@")[-1].lower()
        if domain in ALLOWED_DOMAINS:
            st.session_state["authenticated"] = True
            st.session_state["user_email"]    = email
            st.session_state["user_name"]     = email.split("@")[0].replace(".", " ").title()
            st.query_params.clear()
            st.rerun()
        else:
            _show_error(
                f"Acesso negado para **{email}**.\n\n"
                "Apenas contas @gocase.com e @gobeaute.com têm acesso."
            )
        return

    _render_login_page()
    st.stop()


# ── UI: tela de login ──────────────────────────────────────────────────────────
def _render_login_page() -> None:
    client_id, _, redirect_uri = _get_creds()
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id":     client_id,
            "redirect_uri":  redirect_uri,
            "response_type": "code",
            "scope":         "openid email profile",
            "access_type":   "offline",
            "prompt":        "select_account",
        })
    )

    st.markdown("""
    <style>
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center">
            <div style="font-size:3rem">🌸</div>
            <h1 style="color:#B42828;font-size:1.8rem;margin:8px 0 4px 0">Kokeshi</h1>
            <p style="color:#666;font-size:0.88rem;margin-bottom:40px">
                Google Ads Intelligence Dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center">
            <a href="{auth_url}" style="
                display:inline-block;
                background:#B42828;color:#fff;
                padding:13px 36px;border-radius:8px;
                font-weight:700;font-size:0.95rem;
                text-decoration:none;
                box-shadow:0 2px 10px rgba(180,40,40,0.35);
                letter-spacing:0.2px">
                🔐 &nbsp;Entrar com Google
            </a>
            <p style="color:#aaa;font-size:0.72rem;margin-top:14px">
                Acesso restrito · @gocase.com · @gobeaute.com
            </p>
        </div>
        """, unsafe_allow_html=True)


def _show_error(msg: str) -> None:
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.error(msg)
    st.stop()


# ── UI: badge do usuário logado ───────────────────────────────────────────────
def _render_user_badge() -> None:
    with st.sidebar:
        name  = st.session_state.get("user_name", "")
        email = st.session_state.get("user_email", "")
        st.markdown(f"""
        <div style="padding:8px 0 12px 0;border-bottom:1px solid #eee;margin-bottom:8px">
            <div style="font-size:0.80rem;font-weight:700">{name}</div>
            <div style="font-size:0.70rem;color:#888">{email}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sair", use_container_width=True, key="_logout"):
            st.session_state.clear()
            st.rerun()


# ── OAuth: troca code → email ────────────────────────────────────────────────
def _exchange_code(code: str, redirect_uri: str) -> str | None:
    try:
        client_id, client_secret, _ = _get_creds()
        resp = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          code,
                "client_id":     client_id,
                "client_secret": client_secret,
                "redirect_uri":  redirect_uri,
                "grant_type":    "authorization_code",
            },
            timeout=10,
        )
        id_token = resp.json().get("id_token", "")
        if not id_token:
            return None
        payload_b64 = id_token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        return payload.get("email")
    except Exception:
        return None
