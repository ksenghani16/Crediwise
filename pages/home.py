import streamlit as st

def show():
    st.markdown("""
    <div style='text-align:center; padding: 5rem 2rem 3rem;'>
        <h1 style='font-size:3rem; font-weight:700; line-height:1.2; color:#1a1a1a;'>
            Loan Affordability<br>Smart Assistant
        </h1>
        <p style='font-size:1.1rem; color:#6b7280; margin-top:1rem; max-width:500px; margin-left:auto; margin-right:auto;'>
            Predict borrowing risk, explain why, and recommend<br>safer loan options using AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started →", use_container_width=True):
            st.session_state.page = "calculator"
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Feature highlights
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:1.5rem; border:1px solid #e8e4df; text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>🧠</div>
            <h4 style='margin:0; color:#1a1a1a;'>AI Risk Prediction</h4>
            <p style='color:#6b7280; font-size:0.9rem; margin-top:0.5rem;'>ML model predicts your loan risk with 85%+ accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:1.5rem; border:1px solid #e8e4df; text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>💡</div>
            <h4 style='margin:0; color:#1a1a1a;'>Explainable AI</h4>
            <p style='color:#6b7280; font-size:0.9rem; margin-top:0.5rem;'>Understand exactly why you're risky — not just a number</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:1.5rem; border:1px solid #e8e4df; text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>📊</div>
            <h4 style='margin:0; color:#1a1a1a;'>Smart Recommendations</h4>
            <p style='color:#6b7280; font-size:0.9rem; margin-top:0.5rem;'>Get the best loan plan automatically negotiated for you</p>
        </div>
        """, unsafe_allow_html=True)
