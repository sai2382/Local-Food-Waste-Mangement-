#!/usr/bin/env python
# coding: utf-8

# In[41]:


import pandas as pd



# In[42]:


# Load data from CSV files
providers = pd.read_csv("https://drive.google.com/uc?id=1yPVKWWOL2X7xCmN3LjgT8lV4Rqi0Oxrf")
receivers = pd.read_csv("https://drive.google.com/uc?id=1RgZzTbYm2MHy056HfunOFXEhKauaVuub")
food_listings = pd.read_csv("https://drive.google.com/uc?id=1pVEDLBpXu9DxdavHYThCsUzM5zL-HIIj")
claims = pd.read_csv("https://drive.google.com/uc?id=1ko3Yb5wCn-CmygdII4g2eJYolEeABJjf")


# In[9]:


providers


# In[43]:




# In[54]:


import mysql.connector

conn =  mysql.connector.connect(
        host="database-3.cpkqo4u2gjbr.eu-north-1.rds.amazonaws.com",
        user="admin",
        password="Sai2002123",
        database="database3",
        port=3306
    )


cursor = conn.cursor()
cursor.execute("SHOW DATABASES;")

for db in cursor:
    print(db)


# In[55]:


cursor.execute("CREATE DATABASE IF NOT EXISTS database3")
print("MySQL database 'database3' created successfully!")


# In[56]:


cursor.execute("use database3")


# In[47]:


cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INT PRIMARY key,
        Name VARCHAR(255),
        Type VARCHAR(100),
        Address TEXT,
        City VARCHAR(100),
        Contact VARCHAR(50)
    )
""")


# In[57]:


cursor.execute("""
 CREATE TABLE IF NOT EXISTS  Receivers (
     Receiver_ID INT Primary Key,
     Name Varchar(255),
     Type Varchar(266),
     City Varchar(200),
     Contact varchar(50) 
    )
""")


# In[58]:


cursor.execute("""
    CREATE TABLE IF NOT EXISTS FoodListings (
    Food_ID INT PRIMARY KEY,
    Food_Name VARCHAR(255),
    Quantity INT,
    Expiry_Date DATE,
    Provider_ID INT,
    Provider_Type VARCHAR(255),
    Location VARCHAR(255),
    Food_Type VARCHAR(255),
    Meal_Type VARCHAR(255)
    )
""")


# In[59]:


cursor.execute("""
    create table if not exists Claims(
    Claim_ID INT PRIMARY KEY,
    Food_ID INT,
    Receiver_ID INT,
    Status VARCHAR(255),
    Timestamp DATETIME)
    """
)


# In[53]:


# Insert data using iterrows()
for index, row in providers.iterrows():
    cursor.execute("""INSERT INTO providers (Provider_ID, Name, Type, Address, City, Contact)
        VALUES (%s, %s, %s, %s, %s, %s)""", tuple(row))


# In[41]:


for index, row in receivers.iterrows():
    cursor.execute("""
        INSERT INTO Receivers (Receiver_ID, Name, Type, City, Contact)
        VALUES (%s, %s, %s, %s, %s)""", tuple(row))


# In[52]:


# Fix date format
food_listings["Expiry_Date"] = pd.to_datetime(food_listings["Expiry_Date"]).dt.strftime('%Y-%m-%d')

# Insert row by row
for index, row in food_listings.iterrows():
    cursor.execute("""
        INSERT INTO FoodListings(Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()


# In[55]:


# Convert Timestamp to correct MySQL format
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"]).dt.strftime('%Y-%m-%d %H:%M:%S')

# Insert row by row
for index, row in claims.iterrows():
    cursor.execute("""
        INSERT INTO Claims (Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
        VALUES (%s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()


# In[ ]:


#SQL QUeries


# 📌 Which city has the highest number of food providers?

# In[60]:


# SQL query to get the city with the highest number of providers
query = """
    SELECT City, COUNT(*) AS Provider_Count
    FROM providers
    GROUP BY City
    ORDER BY Provider_Count DESC
    LIMIT 1;
"""

cursor.execute(query)
result = cursor.fetchall()

# Convert result into a DataFrame for better readability
df = pd.DataFrame(result, columns=["City", "Provider_Count"])
df



# In[ ]:




# In[79]:


#get_ipython().run_cell_magic('writefile', 'app2.py', 'import streamlit as st\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport mysql.connector\n\n# -----------------------------\n# MySQL connection helpers\n# -----------------------------\ndef get_connection():\n    return mysql.connector.connect(\n       host="database-1.cpkqo4u2gjbr.eu-north-1.rds.amazonaws.com",\n        user="admin",\n        password="Sai2002123",\n  port=3306,\n        database="database-1"   \n    )\ndef queries_dict():\n    return {\n        # --- Providers & Receivers ---\n        "1. Food Providers per City": """\n            SELECT City, COUNT(*) AS Num_Providers\n            FROM providers\n            GROUP BY City\n            ORDER BY Num_Providers DESC;\n            Limit 5;\n        """,\n        "2. Receivers per City": """\n            SELECT City, COUNT(*) AS Num_Receivers\n            FROM receivers\n            GROUP BY City\n            ORDER BY Num_Receivers DESC;\n        """,\n        "3. Top Provider Type by Contributions": """\n            SELECT fl.Provider_Type, SUM(fl.Quantity) AS Total_Quantity\n            FROM foodlistings fl\n            GROUP BY fl.Provider_Type\n            ORDER BY Total_Quantity DESC;\n        """,\n        "4. Contact Info of Providers in a City (input)": """\n            SELECT Name, Contact, Address, City\n            FROM providers\n            WHERE City = %s;\n        """,\n        "5. Receivers with Most Food Claimed": """\n            SELECT r.Name, SUM(fl.Quantity) AS Total_Claimed\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID\n            WHERE c.Status = \'Completed\'\n            GROUP BY r.Name\n            ORDER BY Total_Claimed DESC;\n        """,\n\n        # --- Food Listings & Availability ---\n        "6. Total Quantity of Food Available": """\n            SELECT SUM(Quantity) AS Total_Available\n            FROM foodlistings;\n        """,\n        "7. City with Highest Number of Food Listings": """\n            SELECT Location, COUNT(*) AS Num_Listings\n            FROM foodlistings\n            GROUP BY Location\n            ORDER BY Num_Listings DESC;\n        """,\n        "8. Most Commonly Available Food Types": """\n            SELECT Food_Type, COUNT(*) AS Frequency\n            FROM foodlistings\n            GROUP BY Food_Type\n            ORDER BY Frequency DESC;\n        """,\n\n        # --- Claims & Distribution ---\n        "9. Number of Claims per Food Item": """\n            SELECT fl.Food_Name, COUNT(c.Claim_ID) AS Num_Claims\n            FROM foodlistings fl\n            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID\n            GROUP BY fl.Food_Name\n            ORDER BY Num_Claims DESC;\n        """,\n        "10. Claims for a Specific Provider (input)": """\n            SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims\n            FROM providers p\n            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID\n            JOIN claims c ON fl.Food_ID = c.Food_ID\n            WHERE c.Status = \'Completed\' AND p.Name = %s\n            GROUP BY p.Name;\n        """,\n        "11. Claim Status Distribution": """\n            SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage\n            FROM claims\n            GROUP BY Status;\n        """,\n\n        # --- Analysis & Insights ---\n        "12. Average Quantity of Food Claimed per Receiver": """\n            SELECT r.Name, AVG(fl.Quantity) AS Avg_Claimed\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID\n            WHERE c.Status = \'Completed\'\n            GROUP BY r.Name\n            ORDER BY Avg_Claimed DESC;\n        """,\n        "13. Most Claimed Meal Type": """\n            SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Num_Claims\n            FROM foodlistings fl\n            JOIN claims c ON fl.Food_ID = c.Food_ID\n            WHERE c.Status IN (\'Completed\',\'Pending\',\'Cancelled\')\n            GROUP BY fl.Meal_Type\n            ORDER BY Num_Claims DESC;\n        """,\n        "14. Total Quantity Donated by Each Provider": """\n            SELECT p.Name, SUM(fl.Quantity) AS Total_Donated\n            FROM providers p\n            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID\n            GROUP BY p.Name\n            ORDER BY Total_Donated DESC;\n        """,\n        "15. Highest Demand City by Claims": """\n            SELECT r.City, COUNT(c.Claim_ID) AS Total_Claims\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            GROUP BY r.City\n            ORDER BY Total_Claims DESC;\n        """\n    }\n\n\ndef visualize_query(selected_query, df):\n    if df.empty:\n        st.warning("⚠️ No data available for this query.")\n        return\n\n    if selected_query == "1. Food Providers per City":\n        st.write("### 🏢 Providers per City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Num_Providers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "2. Receivers per City":\n        st.write("### 👥 Receivers per City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Num_Receivers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "3. Top Provider Type by Contributions":\n        st.write("### 🍴 Provider Type Contributions")\n        plt.figure(figsize=(7,4))\n        sns.barplot(data=df, x="Provider_Type", y="Total_Quantity")\n        st.pyplot(plt)\n\n    elif selected_query == "4. Contact Info of Providers in a City (input)":\n        st.info("Showing provider contact info table for selected city.")\n\n    elif selected_query == "5. Receivers with Most Food Claimed":\n        st.write("### 🏆 Top Receivers by Food Claimed")\n        plt.figure(figsize=(10,6))\n        top = df.head(15)\n        sns.barplot(data=top, x="Total_Claimed", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "6. Total Quantity of Food Available":\n        st.metric("Total Available Quantity", int(df["Total_Available"].iloc[0]))\n\n    elif selected_query == "7. City with Highest Number of Food Listings":\n        st.write("### 🏙️ Listings by City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="Location", y="Num_Listings")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "8. Most Commonly Available Food Types":\n        st.write("### 🥗 Food Type Breakdown")\n        plt.figure(figsize=(6,6))\n        plt.pie(df["Frequency"], labels=df["Food_Type"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    elif selected_query == "9. Number of Claims per Food Item":\n        st.write("### 📦 Claims per Food Item")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Num_Claims", y="Food_Name")\n        st.pyplot(plt)\n\n    elif selected_query == "10. Claims for a Specific Provider (input)":\n        st.write("### ✅ Successful Claims for Provider")\n        st.bar_chart(df.set_index(df.columns[0]))\n\n    elif selected_query == "11. Claim Status Distribution":\n        st.write("### 📊 Claim Status Distribution")\n        plt.figure(figsize=(6,6))\n        plt.pie(df["Percentage"], labels=df["Status"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    elif selected_query == "12. Average Quantity of Food Claimed per Receiver":\n        st.write("### 📈 Avg Claimed Quantity per Receiver")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Avg_Claimed", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "13. Most Claimed Meal Type":\n        st.write("### 🍽️ Most Claimed Meal Type")\n        plt.figure(figsize=(7,4))\n        sns.barplot(data=df, x="Meal_Type", y="Num_Claims")\n        st.pyplot(plt)\n\n    elif selected_query == "14. Total Quantity Donated by Each Provider":\n        st.write("### 🥘 Provider Contributions")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Total_Donated", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "15. Highest Demand City by Claims":\n        st.write("### 🏙️ Highest Demand Cities (Claims)")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Total_Claims")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n# -----------------------------\ndef get_data(query, params=()):\n    conn = get_connection()\n    df = pd.read_sql(query, conn, params=params)\n    conn.close()\n    return df\n\ndef execute_query(query, params=()):\n    conn = get_connection()\n    cur = conn.cursor()\n    cur.execute(query, params)\n    conn.commit()\n    cur.close()\n    conn.close()\n\n# -----------------------------\n# App config\n# -----------------------------\nst.set_page_config(page_title="Waste Food Management System", layout="wide")\n\n# -----------------------------\n# Sidebar\n# -----------------------------\nst.sidebar.title("Navigation")\npage = st.sidebar.radio(\n    "Go to",\n    ["Project Introduction", "CRUD Operations", "SQL Queries", "Waste Food Data Visualization", "Creator Info"]\n)\n\n# -----------------------------\n# Page 1: Introduction\n# -----------------------------\nif page == "Project Introduction":\n    st.title("Local Food Waste Management")\n    st.subheader("A Streamlit App for Exploring Local Waste Food Management Trends")\n    st.write(\n        """\nThis project analyzes food wastage and distribution. Restaurants and individuals can list surplus food; NGOs or individuals can claim it.\nData is stored in MySQL tables: `providers`, `receivers`, `food_listings`, `claims`.\n        """\n    )\n    st.markdown("**Database Used:** `food_database` (update in code if different)")\n\n# -----------------------------\n# Page 2: CRUD Operations\n# -----------------------------\nelif page == "CRUD Operations":\n\n    st.title("🔄 CRUD Operations")\n\n    tables = ["providers", "receivers", "food_listings", "claims"]\n    table = st.selectbox("Select Table", tables)\n\n    # Map primary key column names\n    id_map = {\n        "providers": "Provider_ID",\n        "receivers": "Receiver_ID",\n        "food_listings": "Food_ID",\n        "claims": "Claim_ID",\n    }\n    id_col = id_map[table]\n\n    # Load table\n    df = get_data(f"SELECT * FROM {table}")\n   \n\n    # ----- CREATE -----\n    st.subheader("➕ Create Record")\n    if df.shape[1] > 0:\n        with st.form(f"add_{table}"):\n            new_vals = {}\n            for col in df.columns:\n                if col == id_col:\n                    # Assume auto-increment; skip manual entry\n                    continue\n                new_vals[col] = st.text_input(f"Enter {col}")\n            submitted = st.form_submit_button("Add Record")\n            if submitted:\n                if len(new_vals) == 0:\n                    st.error("No columns to insert.")\n                else:\n                    cols = ", ".join(new_vals.keys())\n                    placeholders = ", ".join(["%s"] * len(new_vals))\n                    execute_query(\n                        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",\n                        tuple(new_vals.values())\n                    )\n                    st.success("✅ Record added successfully!")\n\n    # ----- UPDATE -----\n    if not df.empty:\n        st.subheader("✏️ Update Record")\n        record_id = st.selectbox("Select ID to Update", df[id_col].tolist())\n        with st.form(f"update_{table}"):\n            upd_vals = {}\n            for col in df.columns:\n                if col == id_col:\n                    continue\n                current_value = str(df.loc[df[id_col] == record_id, col].values[0])\n                upd_vals[col] = st.text_input(f"New {col}", value=current_value)\n            update_btn = st.form_submit_button("Update Record")\n            if update_btn:\n                set_clause = ", ".join([f"{col} = %s" for col in upd_vals.keys()])\n                params = tuple(upd_vals.values()) + (record_id,)\n                execute_query(\n                    f"UPDATE {table} SET {set_clause} WHERE {id_col} = %s",\n                    params\n                )\n                st.success("✅ Record updated successfully!")\n\n        # ----- DELETE -----\n        st.subheader("🗑️ Delete Record")\n        delete_id = st.selectbox("Select ID to Delete", df[id_col].tolist(), key=f"delete_{table}")\n        if st.button("Delete Record"):\n            execute_query(f"DELETE FROM {table} WHERE {id_col} = %s", (delete_id,))\n            st.success("✅ Record deleted successfully!")\n    else:\n        st.info("No records found in this table.")\n\n# -----------------------------\n# Shared: queries + visualizer\n# -----------------------------\n\n# Page 3: SQL Queries (table + viz)\nelif page == "SQL Queries":\n    st.title("SQL Query Results")\n    queries = queries_dict()\n    selected_query = st.selectbox("Choose a Query", list(queries.keys()))\n    params = ()\n\n    # Handle inputs\n    if selected_query == "4. Contact Info of Providers in a City (input)":\n        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()\n        city = st.selectbox("Select City", cities)\n        if city:\n            params = (city,)\n\n    if selected_query == "10. Claims for a Specific Provider (input)":\n        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()\n        provider = st.selectbox("Select Provider", providers)\n        if provider:\n            params = (provider,)\n\n    # Run\n    df = get_data(queries[selected_query], params)\n    st.write("### Query Result")\n    st.dataframe(df)\n\n\nelif page=="Waste Food Data Visualization":\n    st.title("📊 Waste Food Data Visualization")\n    queries = queries_dict()\n    selected_query = st.selectbox("Choose a Visualization Query", list(queries.keys()))\n    params = ()\n\n    if selected_query == "4. Contact Info of Providers in a City (input)":\n        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()\n        city = st.selectbox("Select City", cities)\n        if city:\n            params = (city,)\n\n    if selected_query == "10. Claims for a Specific Provider (input)":\n        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()\n        provider = st.selectbox("Select Provider", providers)\n        if provider:\n            params = (provider,)\n\n    df = get_data(queries[selected_query], params)\n    st.write("### Visualization")\n    visualize_query(selected_query, df)\n    \n# -----------------------------\n# Page 5: Creator Info\n# -----------------------------\nelif page == "Creator Info":\n    st.title("👩\u200d💻 Creator of this Project")\n    st.write(\n        """\n    **Developed by:** Saikiran Devunuri  \n    **Skills:** Python, SQL, Data Analysis, Streamlit, Pandas\n        """\n    )\n    st.image("https://via.placeholder.com/150", caption="Profile Picture", width=150)\n')

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

# In[ ]:


#get_ipython().system('streamlit run app2.py')





