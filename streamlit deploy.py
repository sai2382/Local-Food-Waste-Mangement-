import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector

# -----------------------------
# MySQL connection helpers
# -----------------------------
def get_connection():
    return mysql.connector.connect(
        host="database-3.cpkqo4u2gjbr.eu-north-1.rds.amazonaws.com",
        user="admin",
        password="Sai2002123",
        database="database3",
        port=3306

    )
def queries_dict():
    return {
        # --- Providers & Receivers ---
        "1. Food Providers per City": """
            SELECT City, COUNT(*) AS Num_Providers
            FROM providers
            GROUP BY City
            ORDER BY Num_Providers DESC;
            Limit 5;
        """,
        "2. Receivers per City": """
            SELECT City, COUNT(*) AS Num_Receivers
            FROM receivers
            GROUP BY City
            ORDER BY Num_Receivers DESC;
        """,
        "3. Top Provider Type by Contributions": """
            SELECT fl.Provider_Type, SUM(fl.Quantity) AS Total_Quantity
            FROM foodlistings fl
            GROUP BY fl.Provider_Type
            ORDER BY Total_Quantity DESC;
        """,
        "4. Contact Info of Providers in a City (input)": """
            SELECT Name, Contact, Address, City
            FROM providers
            WHERE City = %s;
        """,
        "5. Receivers with Most Food Claimed": """
            SELECT r.Name, SUM(fl.Quantity) AS Total_Claimed
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY r.Name
            ORDER BY Total_Claimed DESC;
        """,

        # --- Food Listings & Availability ---
        "6. Total Quantity of Food Available": """
            SELECT SUM(Quantity) AS Total_Available
            FROM foodlistings;
        """,
        "7. City with Highest Number of Food Listings": """
            SELECT Location, COUNT(*) AS Num_Listings
            FROM foodlistings
            GROUP BY Location
            ORDER BY Num_Listings DESC;
        """,
        "8. Most Commonly Available Food Types": """
            SELECT Food_Type, COUNT(*) AS Frequency
            FROM foodlistings
            GROUP BY Food_Type
            ORDER BY Frequency DESC;
        """,

        # --- Claims & Distribution ---
        "9. Number of Claims per Food Item": """
            SELECT fl.Food_Name, COUNT(c.Claim_ID) AS Num_Claims
            FROM foodlistings fl
            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID
            GROUP BY fl.Food_Name
            ORDER BY Num_Claims DESC;
        """,
        "10. Claims for a Specific Provider (input)": """
            SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM providers p
            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID
            JOIN claims c ON fl.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed' AND p.Name = %s
            GROUP BY p.Name;
        """,
        "11. Claim Status Distribution": """
            SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
            FROM claims
            GROUP BY Status;
        """,

        # --- Analysis & Insights ---
        "12. Average Quantity of Food Claimed per Receiver": """
            SELECT r.Name, AVG(fl.Quantity) AS Avg_Claimed
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY r.Name
            ORDER BY Avg_Claimed DESC;
        """,
        "13. Most Claimed Meal Type": """
            SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Num_Claims
            FROM foodlistings fl
            JOIN claims c ON fl.Food_ID = c.Food_ID
            WHERE c.Status IN ('Completed','Pending','Cancelled')
            GROUP BY fl.Meal_Type
            ORDER BY Num_Claims DESC;
        """,
        "14. Total Quantity Donated by Each Provider": """
            SELECT p.Name, SUM(fl.Quantity) AS Total_Donated
            FROM providers p
            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID
            GROUP BY p.Name
            ORDER BY Total_Donated DESC;
        """,
        "15. Highest Demand City by Claims": """
            SELECT r.City, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.City
            ORDER BY Total_Claims DESC;
        """
    }


def visualize_query(selected_query, df):
    if df.empty:
        st.warning("⚠️ No data available for this query.")
        return

    if selected_query == "1. Food Providers per City":
        st.write("### 🏢 Providers per City")
        plt.figure(figsize=(9,5))
        sns.barplot(data=df, x="City", y="Num_Providers")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif selected_query == "2. Receivers per City":
        st.write("### 👥 Receivers per City")
        plt.figure(figsize=(9,5))
        sns.barplot(data=df, x="City", y="Num_Receivers")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif selected_query == "3. Top Provider Type by Contributions":
        st.write("### 🍴 Provider Type Contributions")
        plt.figure(figsize=(7,4))
        sns.barplot(data=df, x="Provider_Type", y="Total_Quantity")
        st.pyplot(plt)

    elif selected_query == "4. Contact Info of Providers in a City (input)":
        st.info("Showing provider contact info table for selected city.")

    elif selected_query == "5. Receivers with Most Food Claimed":
        st.write("### 🏆 Top Receivers by Food Claimed")
        plt.figure(figsize=(10,6))
        top = df.head(15)
        sns.barplot(data=top, x="Total_Claimed", y="Name")
        st.pyplot(plt)

    elif selected_query == "6. Total Quantity of Food Available":
        st.metric("Total Available Quantity", int(df["Total_Available"].iloc[0]))

    elif selected_query == "7. City with Highest Number of Food Listings":
        st.write("### 🏙️ Listings by City")
        plt.figure(figsize=(9,5))
        sns.barplot(data=df, x="Location", y="Num_Listings")
        plt.xticks(rotation=45)
        st.pyplot(plt)

    elif selected_query == "8. Most Commonly Available Food Types":
        st.write("### 🥗 Food Type Breakdown")
        plt.figure(figsize=(6,6))
        plt.pie(df["Frequency"], labels=df["Food_Type"], autopct="%1.1f%%")
        st.pyplot(plt)

    elif selected_query == "9. Number of Claims per Food Item":
        st.write("### 📦 Claims per Food Item")
        plt.figure(figsize=(10,6))
        top = df.head(20)
        sns.barplot(data=top, x="Num_Claims", y="Food_Name")
        st.pyplot(plt)

    elif selected_query == "10. Claims for a Specific Provider (input)":
        st.write("### ✅ Successful Claims for Provider")
        st.bar_chart(df.set_index(df.columns[0]))

    elif selected_query == "11. Claim Status Distribution":
        st.write("### 📊 Claim Status Distribution")
        plt.figure(figsize=(6,6))
        plt.pie(df["Percentage"], labels=df["Status"], autopct="%1.1f%%")
        st.pyplot(plt)

    elif selected_query == "12. Average Quantity of Food Claimed per Receiver":
        st.write("### 📈 Avg Claimed Quantity per Receiver")
        plt.figure(figsize=(10,6))
        top = df.head(20)
        sns.barplot(data=top, x="Avg_Claimed", y="Name")
        st.pyplot(plt)

    elif selected_query == "13. Most Claimed Meal Type":
        st.write("### 🍽️ Most Claimed Meal Type")
        plt.figure(figsize=(7,4))
        sns.barplot(data=df, x="Meal_Type", y="Num_Claims")
        st.pyplot(plt)

    elif selected_query == "14. Total Quantity Donated by Each Provider":
        st.write("### 🥘 Provider Contributions")
        plt.figure(figsize=(10,6))
        top = df.head(20)
        sns.barplot(data=top, x="Total_Donated", y="Name")
        st.pyplot(plt)

    elif selected_query == "15. Highest Demand City by Claims":
        st.write("### 🏙️ Highest Demand Cities (Claims)")
        plt.figure(figsize=(9,5))
        sns.barplot(data=df, x="City", y="Total_Claims")
        plt.xticks(rotation=45)
        st.pyplot(plt)
# -----------------------------
def get_data(query, params=()):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    cur.close()
    conn.close()

# -----------------------------
# App config
# -----------------------------
st.set_page_config(page_title="Waste Food Management System", layout="wide")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Project Introduction", "CRUD Operations", "SQL Queries", "Waste Food Data Visualization", "Creator Info"]
)

# -----------------------------
# Page 1: Introduction
# -----------------------------
if page == "Project Introduction":
    st.title("Local Food Waste Management")
    st.subheader("A Streamlit App for Exploring Local Waste Food Management Trends")
    st.write(
        """
This project analyzes food wastage and distribution. Restaurants and individuals can list surplus food; NGOs or individuals can claim it.
Data is stored in MySQL tables: `providers`, `receivers`, `food_listings`, `claims`.
        """
    )
    st.markdown("**Database Used:** `food_database` (update in code if different)")

# -----------------------------
# Page 2: CRUD Operations
# -----------------------------
elif page == "CRUD Operations":

    st.title("🔄 CRUD Operations")

    tables = ["providers", "receivers", "food_listings", "claims"]
    table = st.selectbox("Select Table", tables)

    # Map primary key column names
    id_map = {
        "providers": "Provider_ID",
        "receivers": "Receiver_ID",
        "food_listings": "Food_ID",
        "claims": "Claim_ID",
    }
    id_col = id_map[table]

    # Load table
    df = get_data(f"SELECT * FROM {table}")
   

    # ----- CREATE -----
    st.subheader("➕ Create Record")
    if df.shape[1] > 0:
        with st.form(f"add_{table}"):
            new_vals = {}
            for col in df.columns:
                if col == id_col:
                    # Assume auto-increment; skip manual entry
                    continue
                new_vals[col] = st.text_input(f"Enter {col}")
            submitted = st.form_submit_button("Add Record")
            if submitted:
                if len(new_vals) == 0:
                    st.error("No columns to insert.")
                else:
                    cols = ", ".join(new_vals.keys())
                    placeholders = ", ".join(["%s"] * len(new_vals))
                    execute_query(
                        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                        tuple(new_vals.values())
                    )
                    st.success("✅ Record added successfully!")

    # ----- UPDATE -----
    if not df.empty:
        st.subheader("✏️ Update Record")
        record_id = st.selectbox("Select ID to Update", df[id_col].tolist())
        with st.form(f"update_{table}"):
            upd_vals = {}
            for col in df.columns:
                if col == id_col:
                    continue
                current_value = str(df.loc[df[id_col] == record_id, col].values[0])
                upd_vals[col] = st.text_input(f"New {col}", value=current_value)
            update_btn = st.form_submit_button("Update Record")
            if update_btn:
                set_clause = ", ".join([f"{col} = %s" for col in upd_vals.keys()])
                params = tuple(upd_vals.values()) + (record_id,)
                execute_query(
                    f"UPDATE {table} SET {set_clause} WHERE {id_col} = %s",
                    params
                )
                st.success("✅ Record updated successfully!")

        # ----- DELETE -----
        st.subheader("🗑️ Delete Record")
        delete_id = st.selectbox("Select ID to Delete", df[id_col].tolist(), key=f"delete_{table}")
        if st.button("Delete Record"):
            execute_query(f"DELETE FROM {table} WHERE {id_col} = %s", (delete_id,))
            st.success("✅ Record deleted successfully!")
    else:
        st.info("No records found in this table.")

# -----------------------------
# Shared: queries + visualizer
# -----------------------------

# Page 3: SQL Queries (table + viz)
elif page == "SQL Queries":
    st.title("SQL Query Results")
    queries = queries_dict()
    selected_query = st.selectbox("Choose a Query", list(queries.keys()))
    params = ()

    # Handle inputs
    if selected_query == "4. Contact Info of Providers in a City (input)":
        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()
        city = st.selectbox("Select City", cities)
        if city:
            params = (city,)

    if selected_query == "10. Claims for a Specific Provider (input)":
        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()
        provider = st.selectbox("Select Provider", providers)
        if provider:
            params = (provider,)

    # Run
    df = get_data(queries[selected_query], params)
    st.write("### Query Result")
    st.dataframe(df)


elif page=="Waste Food Data Visualization":
    st.title("📊 Waste Food Data Visualization")
    queries = queries_dict()
    selected_query = st.selectbox("Choose a Visualization Query", list(queries.keys()))
    params = ()

    if selected_query == "4. Contact Info of Providers in a City (input)":
        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()
        city = st.selectbox("Select City", cities)
        if city:
            params = (city,)

    if selected_query == "10. Claims for a Specific Provider (input)":
        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()
        provider = st.selectbox("Select Provider", providers)
        if provider:
            params = (provider,)

    df = get_data(queries[selected_query], params)
    st.write("### Visualization")
    visualize_query(selected_query, df)
    
# -----------------------------
# Page 5: Creator Info
# -----------------------------
elif page == "Creator Info":
    st.title("👩‍💻 Creator of this Project")
    st.write(
        """
    **Developed by:** Saikiran Devunuri  
    **Skills:** Python, SQL, Data Analysis, Streamlit, Pandas
        """
    )
    st.image("https://via.placeholder.com/150", caption="Profile Picture", width=150)
