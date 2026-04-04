import streamlit as st


def show():
    if "step" not in st.session_state:
        st.session_state.step = 1

    st.markdown("""
    <style>
    .calc-hero { text-align: center; margin-bottom: 2.5rem; }
    .calc-hero h2 {
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 800;
        color: #f0f4ff; letter-spacing: -0.03em; margin: 0 0 0.45rem;
    }
    .calc-hero p { color: #94a3b8; font-size: 0.96rem; margin: 0; }

    .stepper {
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 2.5rem; max-width: 360px;
    }
    .s-node { display: flex; flex-direction: column; align-items: center; gap: 0.45rem; }
    .s-circle {
        width: 44px; height: 44px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-weight: 800; font-size: 0.95rem;
    }
    .s-circle.active { background: linear-gradient(135deg,#5b7cfa,#6a3de8); color:#fff; box-shadow:0 0 0 6px rgba(91,124,250,0.22); }
    .s-circle.done   { background: #10d9a0; color: #fff; }
    .s-circle.idle   { background: #111827; border: 1.5px solid #1f2f47; color: #4b6080; }
    .s-label { font-size: 0.76rem; color: #4b6080; font-weight: 600; letter-spacing: 0.05em; }
    .s-label.active { color: #8fa8ff; }
    .s-line { flex:1; height:2px; background:#1f2f47; margin:0 1rem 1.5rem; border-radius:2px; }
    .s-line.done { background: linear-gradient(90deg,#5b7cfa,#06d6c7); }

    .fcard {
        background: #111827; border: 1px solid #1f2f47;
        border-radius: 22px; padding: 1.4rem 1.8rem 0.6rem; margin-bottom: 1.2rem;
    }
    .fcard h3 { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:#f0f4ff; margin:0 0 0.2rem; }
    .fcard p  { color:#4b6080; font-size:0.84rem; margin:0 0 1rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="calc-hero">
        <h2>Loan Eligibility Calculator</h2>
        <p>Complete both steps to receive your personalised AI affordability report</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stepper ──
    step = st.session_state.step
    s1c = "active" if step == 1 else "done"
    s2c = "active" if step == 2 else "idle"
    lc  = "done"   if step == 2 else ""
    s1t = "✓"      if step > 1  else "1"
    s1l = "active" if step == 1 else ""
    s2l = "active" if step == 2 else ""

    st.markdown(f"""
    <div class="stepper">
        <div class="s-node">
            <div class="s-circle {s1c}">{s1t}</div>
            <span class="s-label {s1l}">Income</span>
        </div>
        <div class="s-line {lc}"></div>
        <div class="s-node">
            <div class="s-circle {s2c}">2</div>
            <span class="s-label {s2l}">Loan Details</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Centre the form with padding columns
    _, col, _ = st.columns([1, 2, 1])

    with col:
        # ── STEP 1 ──
        if step == 1:
            st.markdown("""
            <div class="fcard">
                <h3>💼 Income &amp; Expenses</h3>
                <p>Tell us your monthly financial picture</p>
            </div>
            """, unsafe_allow_html=True)

            income = st.number_input(
                "Monthly Income (₹)", min_value=0,
                value=int(st.session_state.form_data.get("income", 75000)), step=1000,
            )
            expenses = st.number_input(
                "Monthly Expenses (₹)", min_value=0,
                value=int(st.session_state.form_data.get("expenses", 25000)), step=1000,
            )
            existing_emi = st.number_input(
                "Existing EMIs / Debt (₹)", min_value=0,
                value=int(st.session_state.form_data.get("existing_emi", 5000)), step=500,
            )
            savings = st.number_input(
                "Monthly Savings (₹)", min_value=0,
                value=int(st.session_state.form_data.get("savings", 5000)), step=500,
            )
            st.markdown("---")
            credit_score = st.slider(
                "Credit Score (300 – 900)", 300, 900,
                value=st.session_state.form_data.get("credit_score", 700),
            )
            credit_history = st.number_input(
                "Credit History (years)", min_value=0, max_value=40,
                value=int(st.session_state.form_data.get("credit_history", 4)),
            )

            # Validation
            error_msg = ""
            if income > 0 and expenses >= income:
                error_msg = "⚠️ Monthly expenses cannot exceed or equal your income."
            elif income > 0 and (expenses + existing_emi) >= income:
                error_msg = "⚠️ Expenses + existing EMIs exceed your income. Please review."
            if error_msg:
                st.error(error_msg)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Continue to Loan Details →", use_container_width=True, type="primary"):
                if income == 0:
                    st.error("Please enter a valid monthly income.")
                elif error_msg:
                    st.error("Please fix the errors above before continuing.")
                else:
                    st.session_state.form_data.update({
                        "income": income, "expenses": expenses,
                        "existing_emi": existing_emi, "savings": savings,
                        "credit_score": credit_score, "credit_history": credit_history,
                    })
                    st.session_state.step = 2
                    st.rerun()

        # ── STEP 2 ──
        elif step == 2:
            st.markdown("""
            <div class="fcard">
                <h3>🏦 Loan Details</h3>
                <p>Define your desired loan parameters</p>
            </div>
            """, unsafe_allow_html=True)

            loan_amount = st.number_input(
                "Loan Amount (₹)", min_value=10000,
                value=int(st.session_state.form_data.get("loan_amount", 500000)), step=10000,
            )
            tenure = st.select_slider(
                "Tenure (months)",
                options=[12, 24, 36, 48, 60, 72, 84, 96, 120],
                value=st.session_state.form_data.get("tenure", 60),
            )
            interest_rate = st.number_input(
                "Interest Rate (% p.a.)", min_value=1.0, max_value=30.0,
                value=float(st.session_state.form_data.get("interest_rate", 10.5)), step=0.5,
            )
            loan_type = st.selectbox(
                "Loan Type",
                ["Personal Loan", "Home Loan", "Car Loan", "Education Loan"],
                index=["Personal Loan", "Home Loan", "Car Loan", "Education Loan"].index(
                    st.session_state.form_data.get("loan_type", "Personal Loan")
                ),
            )
            employment = st.selectbox(
                "Employment Type",
                ["Salaried", "Self-Employed", "Business Owner", "Freelancer"],
                index=["Salaried", "Self-Employed", "Business Owner", "Freelancer"].index(
                    st.session_state.form_data.get("employment", "Salaried")
                ),
            )

            st.markdown("<br>", unsafe_allow_html=True)
            cb, ca = st.columns(2)
            with cb:
                if st.button("← Back", use_container_width=True):
                    st.session_state.step = 1
                    st.rerun()
            with ca:
                if st.button("Analyze My Loan →", use_container_width=True, type="primary"):
                    st.session_state.form_data.update({
                        "loan_amount": loan_amount, "tenure": tenure,
                        "interest_rate": interest_rate, "loan_type": loan_type,
                        "employment": employment,
                    })
                    st.session_state.step = 1
                    st.session_state.page = "dashboard"
                    st.rerun()
