import streamlit as st

st.title("🎲 Post-n-Roll")
st.header("Performance Insights 🔎", divider="gray")

st.markdown("""
<style>
    button.step-up {display: none;}
    button.step-down {display: none;}
    div[data-baseweb] {border-radius: 4px;}
</style>""",
unsafe_allow_html=True)

annual_revenue = st.number_input("Revenu annuel (CA)", min_value=0.0, step=100.0, value=None)
avg_basket = st.number_input("Panier moyen", min_value=0.0, step=5.0, value=None)
number_customers_per_year = st.number_input("Nombre de clients par an (laisser vide pour calculer)", min_value=0, value=None)
scenario_adoption_rate = st.selectbox(
    "Sélectionnez le scénario d'adoption du système",
    ["low", "standard", "high"], index=None, placeholder=""
)

annual_revenue = None if annual_revenue == 0 else annual_revenue
avg_basket = None if avg_basket == 0 else avg_basket
number_customers_per_year = None if number_customers_per_year == 0 else number_customers_per_year

filled_values = sum(x is not None for x in [annual_revenue, avg_basket, number_customers_per_year])

# Calculs si au moins deux valeurs sont fournies
if filled_values >= 2:
    if annual_revenue is None and avg_basket is not None and number_customers_per_year is not None:
        annual_revenue = avg_basket * number_customers_per_year
    elif avg_basket is None and annual_revenue is not None and number_customers_per_year is not None:
        avg_basket = annual_revenue / number_customers_per_year
    elif number_customers_per_year is None and annual_revenue is not None and avg_basket is not None:
        number_customers_per_year = round(annual_revenue / avg_basket)
else:
    st.warning("⚠️ Veuillez renseigner au moins deux des trois valeurs : CA, panier moyen, ou nombre de clients.")
    st.stop()


st.markdown(
    f"""
    - **Revenu annuel (CA)** : {f"{annual_revenue:.2f} CHF" if annual_revenue is not None else ""}  
    - **Panier moyen** : {f"{avg_basket:.2f} CHF" if avg_basket is not None else ""}  
    - **Nombre de clients** : {f"{int(number_customers_per_year)}" if number_customers_per_year is not None else ""}
    """
)

scenarios = { # taux_loyal / all_client ; taux avis
    "low": (0.05, 0.40, 0.20, 0.40),
    "standard": (0.20, 0.50, 0.50, 0.50),
    "high": (0.50, 0.55, 0.80, 0.55),
}

rate_customers_pnr_loyal, rate_customers_pnr_loyal_leave_review, rate_customers_pnr_standard, rate_customers_pnr_standard_leave_review = scenarios.get(scenario_adoption_rate, (0, 0, 0, 0))


number_customers_pnr_loyal = number_customers_per_year * rate_customers_pnr_loyal
number_customers_pnr_loyal_leave_review = number_customers_pnr_loyal * rate_customers_pnr_loyal_leave_review
number_customers_pnr_loyal_not_leave_review = number_customers_pnr_loyal - number_customers_pnr_loyal_leave_review
number_customers_pnr_standard = ((number_customers_per_year * rate_customers_pnr_standard) - number_customers_pnr_loyal)
number_customers_pnr_standard_leave_review = number_customers_pnr_standard * rate_customers_pnr_standard_leave_review
number_customers_pnr_standard_not_leave_review = number_customers_pnr_standard - number_customers_pnr_standard_leave_review

number_customers_pnr = number_customers_pnr_loyal + number_customers_pnr_standard
number_customers_pnr_leave_review = number_customers_pnr_loyal_leave_review + number_customers_pnr_standard_leave_review
number_customers_pnr_not_leave_review = number_customers_pnr_loyal_not_leave_review + number_customers_pnr_standard_not_leave_review


st.markdown(f"""Le scénario sélectionné est : **{scenario_adoption_rate}**""")



st.subheader("**Clients**")
st.markdown(f"""Nombre de clients calculé pour le scénario choisi : """)
col1, col2, col3 = st.columns(3)
col1.metric("Clients Post-n-Roll", number_customers_pnr)
col2.metric("Clients laissant un avis", number_customers_pnr_leave_review)
col3.metric("Clients sans avis", number_customers_pnr_not_leave_review)

st.divider()

########### MAIN REWARD

chances_standard_game_2d20 = 1 / 400
value_max_reward_standard_game_allowed = 200
# Adjust Main Reward value (+10% and max 200)
avg_basket_adjusted = avg_basket * 1.1
value_reward_standard_game_2d20 = min(avg_basket_adjusted, value_max_reward_standard_game_allowed)



########### PERLES
number_pearls_generated_with_reviews = ((number_customers_pnr_loyal_leave_review * 10) + (number_customers_pnr_standard_leave_review * 5))
number_pearls_generated_without_reviews = ((number_customers_pnr_loyal_not_leave_review * 2) + (number_customers_pnr_standard_not_leave_review * 1))
number_pearls_generated = number_pearls_generated_with_reviews + number_pearls_generated_without_reviews


# Perls Exchange Conversion Rate
rate_customers_exchange_pearls_for_luckybonus = 0.40
rate_customers_exchange_pearls_for_coupons = 0.50
rate_customers_exchange_pearls_for_donations = 0.05
rate_customers_lose_pearls_for_inactivity = 0.05

# Perls Exchange Rules
value_reduction_of_coupon = 10
number_pearls_needed_exchange_luckybonus = 50
chances_win_luckybonus = 1 / 20  
rate_tax_refund_for_donations = 0.20 

number_luckybonus_played = (number_pearls_generated * rate_customers_exchange_pearls_for_luckybonus) / number_pearls_needed_exchange_luckybonus


########### SUBSCRIPTION

#Coût de l abonnement PNR
cost_subscription_pnr_for_partners_per_month = 99.99


########### GLOBAL COSTS

## Subscription
cost_subscription_pnr_for_partners_per_year = cost_subscription_pnr_for_partners_per_month * 12

## Main Reward (2d20)
number_standard_game_2d20_played = (number_customers_pnr_loyal_leave_review + number_customers_pnr_standard_leave_review) - number_luckybonus_played
cost_standard_game_2d20_per_year = value_reward_standard_game_2d20 * chances_standard_game_2d20 * number_standard_game_2d20_played

## Coupon
number_coupons_generated = (number_pearls_generated * rate_customers_exchange_pearls_for_coupons) / 100
cost_coupons_per_year = number_coupons_generated * value_reduction_of_coupon

## Lucky bonus 1d20
cost_luckybonus_per_year = number_luckybonus_played * chances_win_luckybonus * value_reward_standard_game_2d20

## Donations
cost_donations_per_year = (number_pearls_generated * rate_customers_exchange_pearls_for_donations * 0.10) * (1 - rate_tax_refund_for_donations)
value_earned_for_associations = number_pearls_generated * rate_customers_exchange_pearls_for_donations * 0.10

# Calcul des coûts totaux
cost_total_per_month = cost_subscription_pnr_for_partners_per_month + (cost_standard_game_2d20_per_year / 12) + (cost_coupons_per_year / 12) + (cost_donations_per_year / 12) + (cost_luckybonus_per_year / 12)
cost_total_per_year = cost_total_per_month * 12
cost_total_vs_annual_revenue = (cost_total_per_year / annual_revenue) * 100 if annual_revenue > 0 else 0


########### ESTIMATION ROI - scénarios pessimiste, réaliste et optimiste

rate_new_customers_gained_roi_pessimistic = 0.02
rate_new_customers_gained_roi_realistic = 0.05
rate_new_customers_gained_roi_optimistic = 0.10

# Calcul du nombre de nouveaux clients et du ROI pour chaque scénario
number_new_customers_gained_roi_pessimistic = number_customers_per_year * rate_new_customers_gained_roi_pessimistic
number_new_customers_gained_roi_realistic = number_customers_per_year * rate_new_customers_gained_roi_realistic
number_new_customers_gained_roi_optimistic = number_customers_per_year * rate_new_customers_gained_roi_optimistic

revenue_generated_with_new_customers_gained_roi_pessimistic = number_new_customers_gained_roi_pessimistic * avg_basket
revenue_generated_with_new_customers_gained_roi_realistic = number_new_customers_gained_roi_realistic * avg_basket
revenue_generated_with_new_customers_gained_roi_optimistic = number_new_customers_gained_roi_optimistic * avg_basket

roi_pessimistic = ((revenue_generated_with_new_customers_gained_roi_pessimistic - cost_total_per_year) / cost_total_per_year) * 100 if cost_total_per_year > 0 else 0
roi_realistic = ((revenue_generated_with_new_customers_gained_roi_realistic - cost_total_per_year) / cost_total_per_year) * 100 if cost_total_per_year > 0 else 0
roi_optimistic = ((revenue_generated_with_new_customers_gained_roi_optimistic - cost_total_per_year) / cost_total_per_year) * 100 if cost_total_per_year > 0 else 0

# Gains ou pertes annuelles et mensuelles pour chaque scénario
value_roi_pessimistic_per_year = revenue_generated_with_new_customers_gained_roi_pessimistic - cost_total_per_year
value_roi_realistic_per_year = revenue_generated_with_new_customers_gained_roi_realistic - cost_total_per_year
value_roi_optimistic_per_year = revenue_generated_with_new_customers_gained_roi_optimistic - cost_total_per_year

value_roi_pessimistic_per_month = value_roi_pessimistic_per_year / 12
value_roi_realistic_per_month = value_roi_realistic_per_year / 12
value_roi_optimistic_per_month = value_roi_optimistic_per_year / 12

# Calculs supplémentaires pour le coût moyen par avis et par client

# Nombre de clients par mois
number_new_customers_generated_per_month = round(number_customers_per_year / 12)

# Nombre d'avis laissés (déjà calculé comme $number_customers_pnr_leave_review)
# Calcul du prix moyen par avis et par clien
avg_cost_per_review = cost_total_per_year / number_customers_pnr_leave_review if number_customers_pnr_leave_review > 0 else 0
avg_cost_per_customer = cost_total_per_year / number_customers_per_year if number_customers_per_year > 0 else 0



########## 
st.markdown(
    f"""
    ### 📊 Statistiques Globales
    - **Nombre annuel de clients** : {number_customers_per_year} clients
    - **Total des perles générées** : {number_pearls_generated} perles
    - **Total des perles pour avis** : {number_pearls_generated_with_reviews} perles
    - **Total des perles sans avis** : {number_pearls_generated_without_reviews} perles
    """
)


st.markdown(
    f"""
    ### 💸 Répartition des coûts
    - **Coût mensuel de l'abonnement PNR** : {cost_subscription_pnr_for_partners_per_month:.2f} CHF
    - **Nombre de parties 2d20 jouées** : {number_standard_game_2d20_played}
    - **Coût annuel des récompenses (2d20)** : {cost_standard_game_2d20_per_year:.2f} CHF
    - **Nombre de coupons utilisés** : {number_coupons_generated:.0f}
    - **Coût annuel des coupons** : {cost_coupons_per_year:.2f} CHF
    - **Montant pour les associations** : {value_earned_for_associations:.2f} CHF
    - **Coût annuel des dons (déduction fiscale)** : {cost_donations_per_year:.2f} CHF
    - **Nombre de Lucky Bonus générés** : {number_luckybonus_played:.0f}
    - **Coût annuel des Lucky Bonus** : {cost_luckybonus_per_year:.2f} CHF
    - **Coût total mensuel (toutes composantes)** : {cost_total_per_month:.2f} CHF
    - **Coût total annuel (toutes composantes)** : {cost_total_per_year:.2f} CHF
    """
)


st.markdown(
    f"""
    ### 📝 Coûts par Avis et par Client
    - **Nombre d'avis obtenus après 1 an** : {number_customers_pnr_leave_review} avis
    - **Coût moyen par avis** : {avg_cost_per_review:.2f} CHF
    - **Coût moyen par client** : {avg_cost_per_customer:.2f} CHF
    """
)

st.markdown(
    f"""
    ### 📈 Estimation du ROI avec Gains/Pertes

    **Scénario Pessimiste (+2% de nouveaux clients par an)**  
    - ROI : {roi_pessimistic:.2f}%  
    - Nouveaux clients mensuels : {round((number_customers_per_year * 1.02 - number_customers_per_year) / 12)}
    - Gain/Pertes mensuelles : {value_roi_pessimistic_per_month:.2f} CHF
    - Gain/Pertes annuelles : {value_roi_pessimistic_per_year:.2f} CHF


    **Scénario Réaliste (+5% de nouveaux clients par an)**  
    - ROI : {roi_realistic:.2f}%  
    - Nouveaux clients mensuels : {round((number_customers_per_year * 1.05 - number_customers_per_year) / 12)}
    - Gain/Pertes mensuelles : {value_roi_realistic_per_month:.2f} CHF
    - Gain/Pertes annuelles : {value_roi_realistic_per_year:.2f} CHF


    **Scénario Optimiste (+10% de nouveaux clients par an)**  
    - ROI : {roi_optimistic:.2f}%  
    - Nouveaux clients mensuels : {round((number_customers_per_year * 1.10 - number_customers_per_year) / 12)}
    - Gain/Pertes mensuelles : {value_roi_optimistic_per_month:.2f} CHF
    - Gain/Pertes annuelles : {value_roi_optimistic_per_year:.2f} CHF
    """
)






