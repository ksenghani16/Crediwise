import streamlit as st

def show():
    if "step" not in st.session_state:
        st.session_state.step = 1

    # Step indicator
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:1rem; margin-bottom:2rem;'>
        <div style='display:flex; align-items:center; gap:0.5rem;'>
            <div style='width:32px; height:32px; border-radius:50%; background:{"#1a1a1a" if st.session_state.step >= 1 else "#e5e7eb"}; color:white; display:flex; align-items:center; justify-content:center; font-weight:600; font-size:14px;'>1</div>
            <span style='font-weight:{"600" if st.session_state.step == 1 else "400"}; color:{"#1a1a1a" if st.session_state.step == 1 else "#9ca3af"};'>Income & Expenses</span>
        </div>
        <div style='flex:1; height:2px; background:{"#1a1a1a" if st.session_state.step == 2 else "#e5e7eb"};'></div>
        <div style='display:flex; align-items:center; gap:0.5rem;'>
            <div style='width:32px; height:32px; border-radius:50%; background:{"#1a1a1a" if st.session_state.step >= 2 else "#e5e7eb"}; color:{"white" if st.session_state.step >= 2 else "#9ca3af"}; display:flex; align-items:center; justify-content:center; font-weight:600; font-size:14px;'>2</div>
            <span style='font-weight:{"600" if st.session_state.step == 2 else "400"}; color:{"#1a1a1a" if st.session_state.step == 2 else "#9ca3af"};'>Loan Details</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        if st.session_state.step == 1:
            st.markdown("""
            <div style='background:white; border-radius:16px; padding:2rem; border:1px solid #e8e4df;'>
                <h3 style='margin:0 0 0.5rem; color:#1a1a1a;'>Income & Expenses</h3>
                <p style='color:#6b7280; font-size:0.9rem; margin:0 0 1.5rem;'>Tell us about your current financial situation to calculate your affordability.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div style='background:white; border-radius:16px; padding:2rem; border:1px solid #e8e4df; margin-top:-1rem;'>", unsafe_allow_html=True)
                
                income = st.number_input("Monthly Income ₹ *", min_value=0, value=st.session_state.form_data.get("income", 50000), step=1000)
                expenses = st.number_input("Monthly Expenses ₹ *", min_value=0, value=st.session_state.form_data.get("expenses", 20000), step=1000)
                existing_emi = st.number_input("Existing EMIs / Debt Payments ₹ *", min_value=0, value=st.session_state.form_data.get("existing_emi", 5000), step=500)
                savings = st.number_input("Monthly Savings ₹ (optional)", min_value=0, value=st.session_state.form_data.get("savings", 1000), step=500)
                credit_score = st.number_input("Credit Score (300–900)", min_value=300, max_value=900, value=st.session_state.form_data.get("credit_score", 690))
                credit_history = st.number_input("Credit History (years)", min_value=0, max_value=40, value=st.session_state.form_data.get("credit_history", 4))
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Continue to Loan Details →", use_container_width=True):
                    st.session_state.form_data.update({
                        "income": income, "expenses": expenses, 
                        "existing_emi": existing_emi, "savings": savings,
                        "credit_score": credit_score, "credit_history": credit_history
                    })
                    st.session_state.step = 2
                    st.rerun()

        elif st.session_state.step == 2:
            with st.container():
                st.markdown("<div style='background:white; border-radius:16px; padding:2rem; border:1px solid #e8e4df;'>", unsafe_allow_html=True)
                st.markdown("### Loan Details")
                st.markdown("<p style='color:#6b7280; font-size:0.9rem;'>Enter your desired loan parameters.</p>", unsafe_allow_html=True)
                
                loan_amount = st.number_input("Loan Amount ₹ *", min_value=10000, value=st.session_state.form_data.get("loan_amount", 500000), step=10000)
                tenure = st.selectbox("Tenure (months)", [12, 24, 36, 48, 60, 72, 84, 96, 120], index=4)
                interest_rate = st.number_input("Interest Rate (% p.a.)", min_value=1.0, max_value=30.0, value=st.session_state.form_data.get("interest_rate", 10.5), step=0.5)
                loan_type = st.selectbox("Loan Type", ["Personal Loan", "Home Loan", "Car Loan", "Education Loan"])
                employment = st.selectbox("Employment Type", ["Salaried", "Self-Employed", "Business Owner", "Freelancer"])
                
                st.markdown("</div>", unsafe_allow_html=True)

                col_back, col_analyze = st.columns(2)
                with col_back:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.step = 1
                        st.rerun()
                with col_analyze:
                    if st.button("Analyze My Loan →", use_container_width=True):
                        st.session_state.form_data.update({
                            "loan_amount": loan_amount, "tenure": tenure,
                            "interest_rate": interest_rate, "loan_type": loan_type,
                            "employment": employment
                        })
                        st.session_state.step = 1
                        st.session_state.page = "dashboard"
                        st.rerun()

    with col_right:
        if st.session_state.form_data:
            st.markdown("""
            <div style='background:white; border-radius:16px; padding:1.5rem; border:1px solid #e8e4df;'>
                <h4 style='margin:0 0 1rem; color:#1a1a1a;'>📋 Summary</h4>
            """, unsafe_allow_html=True)
            
            data = st.session_state.form_data
            if data.get("income"):
                st.markdown(f"**Income:** ₹{data.get('income', 0):,}")
                st.markdown(f"**Expenses:** ₹{data.get('expenses', 0):,}")
                st.markdown(f"**Existing EMI:** ₹{data.get('existing_emi', 0):,}")
                disposable = data.get('income', 0) - data.get('expenses', 0) - data.get('existing_emi', 0)
                st.markdown(f"**Disposable:** ₹{disposable:,}")
            if data.get("loan_amount"):
                st.markdown("---")
                st.markdown(f"**Loan Amount:** ₹{data.get('loan_amount', 0):,}")
                st.markdown(f"**Tenure:** {data.get('tenure', 0)} months")
                st.markdown(f"**Interest Rate:** {data.get('interest_rate', 0)}%")
            
            st.markdown("</div>", unsafe_allow_html=True)
