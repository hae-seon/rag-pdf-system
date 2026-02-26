import os
import streamlit as st
import streamlit.components.v1 as components
from main import RAGSystem
from pdf_utils import pdf_page_to_image


st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@300;400;500;600;700&family=Google+Sans+Display:wght@400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
    
    /* ════════════════════════════
       GEMINI DESIGN TOKENS
    ════════════════════════════ */
    :root {
        /* Gemini color palette */
        --bg-main:        #F0F4F8;
        --bg-sidebar:     #E9EEF6;
        --bg-white:       #FFFFFF;
        --bg-surface:     #F0F4FC;
        --bg-input:       #FFFFFF;
        --bg-chip:        #FFFFFF;

        /* Gemini blue accent */
        --blue-primary:   #1A73E8;
        --blue-mid:       #4285F4;
        --blue-light:     #8AB4F8;
        --blue-pale:      #E8F0FE;

        /* Gemini multicolor */
        --gem-blue:       #4285F4;
        --gem-red:        #EA4335;
        --gem-yellow:     #FBBC04;
        --gem-green:      #34A853;

        /* Text */
        --text-primary:   #1F1F1F;
        --text-secondary: #444746;
        --text-muted:     #74787C;
        --text-placeholder: #9AA0A6;
        --text-sidebar:   #1F1F1F;

        /* Border */
        --border-light:   #E8EAED;
        --border-mid:     #DADCE0;
        --border-focus:   #1A73E8;

        /* Shadow */
        --shadow-xs:      0 1px 2px rgba(60,64,67,0.05);
        --shadow-sm:      0 1px 6px rgba(60,64,67,0.08), 0 1px 2px rgba(60,64,67,0.06);
        --shadow-md:      0 2px 12px rgba(60,64,67,0.1), 0 1px 4px rgba(60,64,67,0.06);
        --shadow-lg:      0 4px 24px rgba(60,64,67,0.12), 0 2px 8px rgba(60,64,67,0.08);

        /* Radius */
        --r-xs:   4px;
        --r-sm:   8px;
        --r-md:   12px;
        --r-lg:   16px;
        --r-xl:   24px;
        --r-2xl:  28px;
        --r-full: 9999px;

        /* Font */
        --font-main:  'Noto Sans KR', 'Google Sans', sans-serif;
        --font-display: 'Google Sans Display', 'Noto Sans KR', sans-serif;
        --font-mono:  'DM Mono', monospace;
    }

    /* ════════════════════════════
       RESET & BASE — Gemini BG
    ════════════════════════════ */
    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    .stApp {
        background: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-main) !important;
        -webkit-font-smoothing: antialiased;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }

    .block-container {
        background: transparent !important;
        padding-top: 0 !important;
        padding-bottom: 6rem !important;
        max-width: 780px !important;
    }

    section { background: transparent !important; }

    /* ════════════════════════════
       SIDEBAR — Gemini left nav style
    ════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: none !important;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    /* Gemini logo area */
    .sb-gemini-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 1.4rem 1.2rem 1.2rem;
        margin-bottom: 0.5rem;
    }

    .sb-gemini-icon {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    /* Gemini diamond icon via CSS */
    .gem-diamond {
        width: 24px;
        height: 24px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .gem-diamond::before {
        content: '✦';
        font-size: 22px;
        background: linear-gradient(135deg, var(--gem-blue) 0%, #8B5CF6 40%, var(--gem-red) 70%, var(--gem-yellow) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 6px rgba(66,133,244,0.3));
    }

    .sb-gemini-title {
        font-size: 1.35rem;
        font-weight: 400;
        color: var(--text-primary) !important;
        font-family: var(--font-display) !important;
        letter-spacing: -0.01em;
    }

    /* New chat button */
    .sb-new-chat {
        display: flex;
        align-items: center;
        gap: 10px;
        background: transparent;
        border: none;
        border-radius: var(--r-full);
        padding: 0.6rem 1.2rem;
        margin: 0 0.4rem 1rem;
        cursor: pointer;
        transition: background 0.18s;
        color: var(--text-secondary);
        font-size: 0.875rem;
        width: calc(100% - 0.8rem);
    }

    .sb-new-chat:hover {
        background: rgba(0,0,0,0.06);
    }

    .sb-new-chat-icon {
        width: 34px;
        height: 34px;
        background: var(--bg-white);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: var(--shadow-sm);
        flex-shrink: 0;
    }

    /* Sidebar section labels */
    .sb-section-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-muted) !important;
        padding: 0.5rem 1.4rem 0.3rem;
        letter-spacing: 0.02em;
    }

    /* Sidebar nav items */
    .sb-nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.62rem 1rem;
        border-radius: var(--r-full);
        margin: 0 0.4rem;
        cursor: pointer;
        transition: background 0.15s;
        font-size: 0.9rem;
        color: var(--text-secondary);
    }

    .sb-nav-item:hover {
        background: rgba(0,0,0,0.06);
    }

    .sb-nav-item.active {
        background: rgba(26,115,232,0.12);
        color: var(--blue-primary);
        font-weight: 500;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-family: var(--font-mono) !important;
        font-weight: 500 !important;
        margin-bottom: 0.4rem !important;
    }

    section[data-testid="stSidebar"] hr {
        border: none !important;
        border-top: 1px solid rgba(0,0,0,0.08) !important;
        margin: 0.8rem 0 !important;
    }

    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.7) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--r-full) !important;
        font-size: 0.84rem !important;
        font-family: var(--font-main) !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.18s ease !important;
        box-shadow: var(--shadow-xs) !important;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.9) !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 0.8rem !important;
        border-radius: var(--r-full) !important;
        transition: all 0.15s !important;
    }

    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: rgba(26,115,232,0.1) !important;
        color: var(--blue-primary) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
        background: rgba(255,255,255,0.6) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-secondary) !important;
        font-size: 0.875rem !important;
    }

    /* ════════════════════════════
       HERO — Gemini center layout
    ════════════════════════════ */
    .hero-wrap {
        text-align: center;
        padding: 5.5rem 2rem 3rem;
        position: relative;
    }

    .hero-gemini-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.4rem;
        position: relative;
    }

    .hero-gem-star {
        font-size: 3.2rem;
        background: linear-gradient(135deg, var(--gem-blue) 0%, #8B5CF6 35%, var(--gem-red) 65%, var(--gem-yellow) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 16px rgba(66,133,244,0.25));
        animation: gemPulse 3s ease-in-out infinite;
        line-height: 1;
    }

    @keyframes gemPulse {
        0%, 100% { filter: drop-shadow(0 0 10px rgba(66,133,244,0.2)); }
        50%       { filter: drop-shadow(0 0 22px rgba(66,133,244,0.45)); }
    }

    .hero-greeting {
        font-size: 0.95rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0 0 0.35rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }

    .hero-greeting-name {
        font-weight: 500;
        color: var(--text-primary);
    }

    .hero-title {
        font-family: var(--font-display);
        font-size: 2.55rem;
        font-weight: 400;
        color: var(--text-primary);
        line-height: 1.18;
        margin: 0;
        letter-spacing: -0.02em;
    }

    /* ════════════════════════════
       SEARCH INPUT — Gemini pill style
    ════════════════════════════ */
    .search-container {
        position: relative;
        margin-top: 2.8rem;
    }

    div.stTextArea textarea {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: 28px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-main) !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        padding: 18px 100px 18px 24px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.2s ease !important;
        line-height: 1.55 !important;
        resize: none !important;
    }

    div.stTextArea textarea:focus {
        border-color: transparent !important;
        box-shadow: 0 0 0 2px var(--gem-blue), 0 2px 14px rgba(66,133,244,0.12) !important;
        outline: none !important;
    }

    div.stTextArea textarea::placeholder {
        color: var(--text-placeholder) !important;
        font-weight: 400;
    }

    div.stTextArea label {
        display: none !important;
    }

    /* ════════════════════════════
       BUTTONS
    ════════════════════════════ */
    .stButton button {
        font-family: var(--font-main) !important;
        font-weight: 500 !important;
        border-radius: var(--r-full) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0 !important;
    }

    .stButton button[kind="primary"] {
        background: var(--blue-primary) !important;
        color: #fff !important;
        border: none !important;
        padding: 0.72rem 2.2rem !important;
        font-size: 0.9rem !important;
        box-shadow: 0 2px 12px rgba(26,115,232,0.3) !important;
    }

    .stButton button[kind="primary"]:hover {
        background: #1557B0 !important;
        box-shadow: 0 4px 18px rgba(26,115,232,0.4) !important;
        transform: translateY(-1px) !important;
    }

    .stButton button[kind="secondary"] {
        background: var(--bg-white) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-mid) !important;
        padding: 0.62rem 1.4rem !important;
        font-size: 0.875rem !important;
        box-shadow: var(--shadow-xs) !important;
    }

    .stButton button[kind="secondary"]:hover {
        background: var(--bg-surface) !important;
        border-color: var(--blue-primary) !important;
        color: var(--blue-primary) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ════════════════════════════
       ANSWER CARD — Gemini response style
    ════════════════════════════ */
    /* ── 질문 버블 ── */
    .question-bubble {
        display: flex;
        justify-content: flex-end;
        margin: 2.4rem 0 0.8rem;
    }

    .question-bubble-inner {
        background: var(--blue-primary);
        color: #ffffff;
        border-radius: 20px 20px 4px 20px;
        padding: 0.75rem 1.2rem;
        max-width: 82%;
        font-size: 15px;
        line-height: 1.65;
        font-family: var(--font-main);
        box-shadow: 0 2px 10px rgba(26,115,232,0.25);
        word-break: break-word;
        white-space: pre-wrap;
    }

    .sec-div {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 1rem 0 1.2rem;
    }

    .sec-div::before, .sec-div::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border-light);
    }

    .sec-div span {
        font-size: 0.7rem;
        font-family: var(--font-mono);
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .answer-card {
        background: var(--bg-white);
        border: 1px solid var(--border-light);
        border-radius: var(--r-xl);
        overflow: hidden;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
        animation: fadeUp 0.35s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .answer-card-hd {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.9rem 1.4rem;
        border-bottom: 1px solid var(--border-light);
    }

    .answer-gem-icon {
        font-size: 1rem;
        background: linear-gradient(135deg, var(--gem-blue), #8B5CF6, var(--gem-red));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .answer-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--text-secondary);
        font-family: var(--font-main);
        letter-spacing: 0;
    }

    .answer-body {
        padding: 1.4rem 1.6rem;
        font-size: 15px;
        line-height: 1.9;
        color: var(--text-primary);
    }

    /* ════════════════════════════
       EXPANDER
    ════════════════════════════ */
    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--r-lg) !important;
        color: var(--text-secondary) !important;
        font-family: var(--font-main) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: all 0.15s !important;
        padding: 0.75rem 1rem !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: var(--bg-surface) !important;
        border-color: var(--blue-primary) !important;
        color: var(--blue-primary) !important;
    }

    [data-testid="stExpander"] {
        border: none !important;
        background: transparent !important;
    }

    /* ════════════════════════════
       MESSAGE BOXES
    ════════════════════════════ */
    .stSuccess {
        background: #E6F4EA !important;
        border: 1px solid #CEEAD6 !important;
        border-radius: var(--r-lg) !important;
        color: #137333 !important;
    }

    .stError {
        background: #FCE8E6 !important;
        border: 1px solid #F5C6C2 !important;
        border-radius: var(--r-lg) !important;
        color: #C5221F !important;
    }

    .stInfo {
        background: var(--blue-pale) !important;
        border: 1px solid #C5D9F8 !important;
        border-radius: var(--r-lg) !important;
        color: #1A73E8 !important;
    }

    .stWarning {
        background: #FEF9E7 !important;
        border: 1px solid #FDD663 !important;
        border-radius: var(--r-lg) !important;
        color: #856404 !important;
    }

    /* ════════════════════════════
       MISC
    ════════════════════════════ */
    .stSpinner > div { border-top-color: var(--blue-primary) !important; }

    h1, h2, h3 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
    }

    .stMarkdown h3 {
        border-bottom: 1px solid var(--border-light) !important;
        padding-bottom: 0.5rem !important;
    }

    hr {
        border: none !important;
        border-top: 1px solid var(--border-light) !important;
        margin: 1.5rem 0 !important;
    }

    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
    }

    input[type="text"] {
        background: var(--bg-white) !important;
        border: 1px solid var(--border-mid) !important;
        border-radius: var(--r-md) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-main) !important;
        padding: 0.7rem 1rem !important;
    }

    input[type="text"]:focus {
        border-color: var(--blue-primary) !important;
        box-shadow: 0 0 0 2px rgba(26,115,232,0.2) !important;
    }

    [data-testid="stFileUploader"] {
        background: var(--bg-white) !important;
        border: 1.5px dashed var(--border-mid) !important;
        border-radius: var(--r-lg) !important;
    }

    /* "Drag and drop files here · Limit 200MB" 숨김 */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span,
    [data-testid="stFileUploaderDropzoneInstructions"] > div > small {
        display: none !important;
    }

    /* "Browse files" → "파일추가" */
    [data-testid="stFileUploaderDropzone"] button {
        font-size: 0 !important;
        color: transparent !important;
    }
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "파일추가";
        font-size: 0.875rem;
        color: var(--blue-primary);
        font-family: var(--font-main);
        font-weight: 500;
    }

    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 4px; }

    /* ════════════════════════════
       COMPONENT HELPERS
    ════════════════════════════ */
    .src-path {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
    }

    .doc-preview {
        font-size: 0.84rem;
        color: var(--text-secondary);
        line-height: 1.7;
        font-family: var(--font-main);
        background: var(--bg-surface);
        border-radius: var(--r-md);
        padding: 0.8rem 1rem;
        border-left: 3px solid var(--blue-primary);
    }

    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        margin-top: 4rem;
        border-top: 1px solid var(--border-light);
    }

    .footer span {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
        letter-spacing: 0.08em;
    }

    /* Gemini-style status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--bg-white);
        border: 1px solid var(--border-mid);
        border-radius: var(--r-full);
        padding: 3px 10px;
        font-size: 0.68rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
        letter-spacing: 0.06em;
        box-shadow: var(--shadow-xs);
    }

    .status-dot {
        width: 6px; height: 6px;
        background: #34A853;
        border-radius: 50%;
        animation: blink 2.4s ease-in-out infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }

    /* User profile chip */
    .sb-profile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.7rem 1.2rem;
        border-radius: var(--r-full);
        margin: 0.5rem 0.4rem;
        cursor: pointer;
        transition: background 0.15s;
    }

    .sb-profile:hover {
        background: rgba(0,0,0,0.06);
    }

    .sb-avatar {
        width: 32px; height: 32px;
        background: linear-gradient(135deg, var(--gem-blue), #8B5CF6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        color: #fff;
        font-weight: 600;
        flex-shrink: 0;
    }

    .sb-profile-name {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary) !important;
    }

    .sb-profile-role {
        font-size: 0.72rem;
        color: var(--text-muted) !important;
        font-family: var(--font-mono);
    }

    /* ── 문서 관리 파일 리스트 ── */
    .sb-doc-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.9rem 1.2rem 0.5rem;
    }

    .sb-doc-title {
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-family: var(--font-mono);
    }

    .sb-doc-badge {
        font-size: 0.68rem;
        padding: 2px 9px;
        border-radius: var(--r-full);
        font-family: var(--font-mono);
        font-weight: 500;
    }

    .sb-doc-badge.loaded {
        background: #E6F4EA;
        color: #137333;
    }

    .sb-doc-badge.empty {
        background: #F1F3F4;
        color: #9AA0A6;
    }

    .sb-file-list {
        padding: 0 1.2rem 0.6rem;
        max-height: 140px;
        overflow-y: auto;
    }

    .sb-file-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.7rem;
        color: var(--text-muted);
        padding: 4px 0;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        font-family: var(--font-mono);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .sb-upload-hint {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-align: center;
        padding: 0.6rem 1.2rem 0.4rem;
    }

    /* Gemini bottom right upgrade btn */
    .upgrade-hint {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: linear-gradient(135deg, var(--gem-blue) 0%, #8B5CF6 100%);
        color: #fff !important;
        font-size: 0.78rem;
        font-weight: 500;
        padding: 5px 14px;
        border-radius: var(--r-full);
        box-shadow: 0 2px 10px rgba(66,133,244,0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────
#  RAG 시스템
# ─────────────────────────────────────
@st.cache_resource
def get_rag_system():
    return RAGSystem()

rag = get_rag_system()

if "index_loaded" not in st.session_state:
    st.session_state["index_loaded"] = False


# ══════════════════════════════════════
#  SIDEBAR — Gemini left nav
# ══════════════════════════════════════

st.sidebar.markdown("---")

# User profile
st.sidebar.markdown(
    """
    <div class="sb-profile">
        <div class="sb-avatar">홍</div>
        <div>
            <div class="sb-profile-name">홍길동</div>
            <div class="sb-profile-role">aid003 · 심사관</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 파일관리")

with st.sidebar.expander("📂  파일 업로드", expanded=False):
    uploaded_files = st.file_uploader(
        "파일을 업로드하세요",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader",
    )

    if st.button("📥  파일 추가", use_container_width=True, type="secondary", key="upload_btn"):
        if not uploaded_files:
            st.warning("먼저 PDF를 업로드해주세요.")
        else:
            try:
                upload_dir = os.path.join("data", "uploaded_pdfs")
                os.makedirs(upload_dir, exist_ok=True)
                ingested_files = set()
                if rag.vector_store.vectorstore is not None and hasattr(rag.vector_store.vectorstore, 'docstore'):
                    for doc in rag.vector_store.vectorstore.docstore._dict.values():
                        sf = doc.metadata.get("source_file")
                        if sf:
                            ingested_files.add(sf)

                all_chunks = []
                skipped = []
                for file in uploaded_files:
                    if file.name in ingested_files:
                        skipped.append(file.name)
                        continue
                    save_path = os.path.join(upload_dir, file.name)
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())
                    docs = rag.pdf_processor.process_pdf(save_path)
                    all_chunks.extend(docs)

                if all_chunks:
                    if rag.vector_store.vectorstore is None:
                        rag.vector_store.create_vectorstore(all_chunks)
                    else:
                        rag.vector_store.ingest_documents(all_chunks)
                    rag.vector_store.save_vectorstore()

                st.session_state["index_loaded"] = True
                st.success(f"✅ PDF {len(uploaded_files)}개 반영 완료")
            except Exception as e:
                st.error(f"오류: {e}")

db = rag.vector_store.vectorstore


# ══════════════════════════════════════
#  MAIN — Gemini center UI
# ══════════════════════════════════════

# Session state 초기화
if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = None

has_result = bool(st.session_state.get("last_answer"))

# HERO — 결과 없으면 큰 패딩으로 검색창이 화면 중앙에 위치
# HERO — 결과 없으면만 표시
if not has_result:
    hero_padding = "padding: 28vh 2rem 3rem"
    st.markdown(
        f"""
        <div class="hero-wrap" style="{hero_padding}">
            <div class="hero-title">무엇을 도와드릴까요?</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # 결과가 있을 때는 상단 여백만 살짝 (원하면 삭제 가능)
    st.markdown("<div style='height:1.0rem'></div>", unsafe_allow_html=True)

# ── 결과 영역 (검색창 위에 표시) ──
answer_container = st.container()

# 검색 후 입력창 초기화 (위젯 렌더링 전에 처리)
if st.session_state.pop("_clear_input", False):
    st.session_state["question_input"] = ""

# 검색창
question = st.text_area(
    label="검색어",
    label_visibility="collapsed",
    height=100,
    placeholder="🔍  궁금한 점을 검색해보세요",
    key="question_input",
)

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    search_clicked = st.button("검색하기", type="primary", key="run_search", use_container_width=True)

# Ctrl+Enter 단축키 — 부모 문서에 이벤트 리스너 주입
components.html(
    """
    <script>
    (function() {
        var p = window.parent;
        if (p.__ctrlEnterAdded) return;
        p.__ctrlEnterAdded = true;
        p.document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                var btns = p.document.querySelectorAll('button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].innerText.trim() === '검색하기') {
                        btns[i].click();
                        return;
                    }
                }
            }
        });
    })();
    </script>
    """,
    height=0,
)


def _render_answer(answer_text):
    import re

    def _to_html(text):
        """마크다운 표와 텍스트를 HTML로 변환 (단일 div 렌더링용)."""
        lines = text.split('\n')
        parts = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # 마크다운 표 감지 (다음 줄이 구분선인지 확인)
            if (re.match(r'^\s*\|', line) and
                    i + 1 < len(lines) and
                    re.match(r'^\s*\|[\s\-:|]+\|\s*$', lines[i + 1])):
                headers = [h.strip() for h in line.strip().strip('|').split('|')]
                tbl = ('<table style="width:100%;border-collapse:collapse;'
                       'font-size:14px;margin:0.6rem 0">')
                tbl += '<thead><tr>'
                for h in headers:
                    tbl += (f'<th style="background:#F0F4FC;border:1px solid #DADCE0;'
                            f'padding:8px 14px;text-align:left;font-weight:600;">{h}</th>')
                tbl += '</tr></thead><tbody>'
                i += 2  # 헤더 + 구분선 건너뜀
                row_idx = 0
                while i < len(lines) and re.match(r'^\s*\|', lines[i]):
                    cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                    bg = '#F8FAFC' if row_idx % 2 else 'white'
                    tbl += '<tr>'
                    for cell in cells:
                        tbl += (f'<td style="border:1px solid #E8EAED;'
                                f'padding:8px 14px;background:{bg};">{cell}</td>')
                    tbl += '</tr>'
                    i += 1
                    row_idx += 1
                tbl += '</tbody></table>'
                parts.append(tbl)
            else:
                parts.append(line if line.strip() else '<br>')
                i += 1
        return '<br>'.join(parts)

    body_html = _to_html(answer_text)

    # 질문 버블
    last_q = st.session_state.get("last_question", "")
    if last_q:
        st.markdown(
            f"""
            <div class="question-bubble">
                <div class="question-bubble-inner">{last_q.replace(chr(10), '<br>')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sec-div"><span>AI 답변 결과</span></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-card-hd">
                <span class="answer-gem-icon">✦</span>
                <span class="answer-label">AI 답변</span>
            </div>
            <div class="answer-body">{body_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if search_clicked:
    if not st.session_state.get("index_loaded") and rag.vector_store.vectorstore is None:
        with answer_container:
            st.warning("📂 PDF 파일을 업로드해주세요")
    elif not question.strip():
        with answer_container:
            st.warning("검색어를 입력해주세요.")
    else:
        with answer_container:
            with st.spinner("AI가 검색하고 있습니다..."):
                try:
                    import traceback

                    result = rag.query(question)

                    if isinstance(result, dict):
                        answer = result.get("answer") or result.get("result") or str(result)
                    else:
                        answer = str(result)

                    st.session_state["last_answer"] = answer
                    st.session_state["last_question"] = question
                    st.session_state["_clear_input"] = True
                    st.rerun()

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
                    st.code(traceback.format_exc())

if has_result and not search_clicked:
    with answer_container:
        _render_answer(st.session_state["last_answer"])


# FOOTER
st.markdown(
    """
    <div class="footer">
        <span>PHARMACEUTICAL AI SYSTEM · MFDS INTELLIGENCE PLATFORM · v2.0</span>
    </div>
    """,
    unsafe_allow_html=True,
)