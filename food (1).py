#!/usr/bin/env python
# coding: utf-8

# In[41]:


import pandas as pd
import sqlite3


# In[42]:


# Load data from CSV files
providers = pd.read_csv("providers_data.csv")
receivers = pd.read_csv("receivers_data.csv")
food_listings = pd.read_csv("food_listings_data.csv")
claims = pd.read_csv("claims_data.csv")


# In[9]:


providers


# In[43]:


import mysql.connector as p
print("Connector works!")


# In[54]:


import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",

)

cursor = conn.cursor()
cursor.execute("SHOW DATABASES;")

for db in cursor:
    print(db)


# In[55]:


cursor.execute("CREATE DATABASE IF NOT EXISTS food_data")
print("MySQL database 'food_data' created successfully!")


# In[56]:


cursor.execute("use food_data")


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


get_ipython().run_cell_magic('writefile', 'app.py', 'import streamlit as st\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\ndef get_data(query, params=None):  \n    conn = mysql.connector.connect(\n    host="localhost",\n    user="root",\n    password="12345",\n\n) \n    if params:\n        df = pd.read_sql_query(query, conn, params=params)\n    else:\n        df = pd.read_sql_query(query, conn)\n    conn.close()\n    return df\n\n# Streamlit App Title\nst.set_page_config(page_title="waste food management system", layout="wide")\n\n# Sidebar for navigation\nst.sidebar.title("Navigation")\npage = st.sidebar.radio("Go to", ["Project Introduction","CRUD operations" "SQL Queries", "Waste Food Data Visualization", "Creator Info"])\n\n# -------------------------------- PAGE 1: Introduction --------------------------------\nif page == "Project Introduction":\n    st.title("LOcal Food Waste Management")\n    st.subheader("A Streamlit App for Exploring Local waste Food Mangement Trends")\n    st.write("""\n    This project analyzes Food wastage is a significant issue, with many households \n    and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where:\n        Restaurants and individuals can list surplus food.\n        NGOs or individuals in need can claim the food.\n        SQL stores available food details and locations.\n\n    **Database Used:** `Food_database.SQL`\n    """)\n# -------------------------------- PAGE 2: Crud operations --------------------------------\nelif page == "CRUD Operations":\n    def get_data(query, params=()):     \n        conn = mysql.connector.connect(\n        host="localhost",\n        user="root",\n        password="12345",\n    )\n        df = pd.read_sql_query(query, conn, params=params)\n        conn.close()\n        return df\n\n# --- Execute Query ---\ndef execute_query(query, params=()):\n    conn = mysql.connector.connect(\n    host="localhost",\n    user="root",\n    password="12345",\n\n)\n    conn = get_connection()\n    cur = conn.cursor()\n    cur.execute(query, params)\n    conn.commit()\n    conn.close()\n\n# --- CRUD Operations Page ---\ndef crud_operations():\n    st.title("🔄 CRUD Operations")\n\n    tables = ["providers", "receivers", "food_listings", "claims"]\n    table = st.selectbox("Select Table", tables)\n\n    df = get_data(f"SELECT * FROM {table}")\n    st.write(f"### Current Data in {table}", df)\n\n    st.subheader("➕ Create Record")\n    with st.form(f"add_{table}"):\n        new_data = {}\n        for col in df.columns[1:]:  # skip ID (auto-increment usually)\n            new_data[col] = st.text_input(f"Enter {col}")\n        submitted = st.form_submit_button("Add Record")\n        if submitted:\n            cols = ", ".join(new_data.keys())\n            placeholders = ", ".join(["?"] * len(new_data))\n            execute_query(\n                f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",\n                tuple(new_data.values())\n            )\n            st.success("✅ Record added successfully!")\n\n    st.subheader("✏️ Update Record")\n    record_id = st.selectbox("Select ID to Update", df.iloc[:, 0])\n    with st.form(f"update_{table}"):\n        updated_data = {}\n        for col in df.columns[1:]:\n            updated_data[col] = st.text_input(f"New {col}", value=str(\n                df.loc[df.iloc[:, 0] == record_id, col].values[0]\n            ))\n        update_btn = st.form_submit_button("Update Record")\n        if update_btn:\n            set_clause = ", ".join([f"{col} = ?" for col in updated_data.keys()])\n            execute_query(\n                f"UPDATE {table} SET {set_clause} WHERE {df.columns[0]} = ?",\n                tuple(updated_data.values()) + (record_id,)\n            )\n            st.success("✅ Record updated successfully!")\n\n    st.subheader("🗑️ Delete Record")\n    delete_id = st.selectbox("Select ID to Delete", df.iloc[:, 0], key=f"delete_{table}")\n    if st.button("Delete Record"):\n        execute_query(f"DELETE FROM {table} WHERE {df.columns[0]} = ?", (delete_id,))\n        st.success("✅ Record deleted successfully!")\ncrud_operations()\n# -------------------------------- PAGE 3: SQL Queries --------------------------------\n\n# Handle queries needing user input\nif selected_query == "4. Contact Info of Providers in a City":\n    city = st.text_input("Enter City")\n    if city:\n        params = (city,)\n\n# Run query\nif params:\n    query_result = get_data(queries[selected_query], params=params)\nelse:\n    query_result = get_data(queries[selected_query])\n\nst.write("### Query Result:")\nst.dataframe(query_result)\n\n# -------------------------------- PAGE 4: SQL --------------------------------\n\nelif page == "Waste Food Data Visualization":\n    st.title("📊 Waste Food Data Visualization")\n        def get_data(query, params=()):\n    conn = mysql.connector.connect(\n    host="localhost",\n    user="root",\n    password="12345",\n)\n    df = pd.read_sql_query(query, conn, params=params)\n    conn.close()\n    return df\n\n# --- Execute Query ---\n\n# --- CRUD Operations Page ---\nqueries = {\n    "1. Food Providers per City": """\n        SELECT Location AS City, COUNT(*) AS Num_Providers\n        FROM providers\n        GROUP BY Location\n        ORDER BY Num_Providers DESC;\n    """,\n\n    "2. Receivers per City": """\n        SELECT Location AS City, COUNT(*) AS Num_Receivers\n        FROM receivers\n        GROUP BY Location\n        ORDER BY Num_Receivers DESC;\n    """,\n\n    "3. Top Provider Type by Contributions": """\n        SELECT Provider_Type, SUM(f.Quantity) AS Total_Quantity\n        FROM providers p\n        JOIN food f ON p.Provider_ID = f.Provider_ID\n        GROUP BY Provider_Type\n        ORDER BY Total_Quantity DESC;\n    """,\n\n    "4. Contact Info of Providers in a City": """\n        SELECT Name, Phone, Email, Location\n        FROM providers\n        WHERE Location = %s;   -- pass city dynamically\n    """,\n\n    "5. Receivers with Most Food Claimed": """\n        SELECT r.Name, SUM(c.Quantity) AS Total_Claimed\n        FROM receivers r\n        JOIN claims c ON r.Receiver_ID = c.Receiver_ID\n        GROUP BY r.Name\n        ORDER BY Total_Claimed DESC\n        LIMIT 10;\n    """,\n\n    "6. Total Quantity of Food Available": """\n        SELECT SUM(Quantity) AS Total_Available\n        FROM food\n        WHERE Status = \'Available\';\n    """,\n\n    "7. City with Highest Number of Food Listings": """\n        SELECT f.Location, COUNT(*) AS Num_Listings\n        FROM food f\n        GROUP BY f.Location\n        ORDER BY Num_Listings DESC;\n    """,\n\n    "8. Most Commonly Available Food Types": """\n        SELECT Food_Type, COUNT(*) AS Frequency\n        FROM food\n        GROUP BY Food_Type\n        ORDER BY Frequency DESC;\n    """,\n\n    "9. Number of Claims per Food Item": """\n        SELECT f.Food_Name, COUNT(c.Claim_ID) AS Num_Claims\n        FROM food f\n        LEFT JOIN claims c ON f.Food_ID = c.Food_ID\n        GROUP BY f.Food_Name\n        ORDER BY Num_Claims DESC;\n    """,\n\n    "10. Provider with Highest Successful Claims": """\n        SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims\n        FROM providers p\n        JOIN food f ON p.Provider_ID = f.Provider_ID\n        JOIN claims c ON f.Food_ID = c.Food_ID\n        WHERE c.Status = \'Approved\'\n        GROUP BY p.Name\n        ORDER BY Successful_Claims DESC\n        LIMIT 10;\n    """,\n\n    "11. Claim Status Distribution": """\n        SELECT Status,\n               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage\n        FROM claims\n        GROUP BY Status;\n    """,\n\n    "12. Average Quantity of Food Claimed per Receiver": """\n        SELECT r.Name, ROUND(AVG(c.Quantity), 2) AS Avg_Claimed\n        FROM receivers r\n        JOIN claims c ON r.Receiver_ID = c.Receiver_ID\n        GROUP BY r.Name\n        ORDER BY Avg_Claimed DESC\n        LIMIT 10;\n    """,\n\n    "13. Most Claimed Meal Type": """\n        SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Num_Claims\n        FROM food f\n        JOIN claims c ON f.Food_ID = c.Food_ID\n        GROUP BY f.Meal_Type\n        ORDER BY Num_Claims DESC;\n    """,\n\n    "14. Total Quantity Donated by Each Provider": """\n        SELECT p.Name, SUM(f.Quantity) AS Total_Donated\n        FROM providers p\n        JOIN food f ON p.Provider_ID = f.Provider_ID\n        GROUP BY p.Name\n        ORDER BY Total_Donated DESC\n        LIMIT 10;\n    """,\n\n    "15. Highest Demand City by Claims": """\n        SELECT r.Location AS City, COUNT(c.Claim_ID) AS Total_Claims\n        FROM receivers r\n        JOIN claims c ON r.Receiver_ID = c.Receiver_ID\n        GROUP BY r.Location\n        ORDER BY Total_Claims DESC\n        LIMIT 10;\n    """\n}\n\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\ndef visualize_query(selected_query, query_result):\n    if query_result.empty:\n        st.warning("⚠️ No data available for this query.")\n        return\n\n    # 1. Food Providers per City\n    if selected_query == "1. Food Providers per City":\n        st.write("### 🏢 Food Providers per City")\n        plt.figure(figsize=(8,5))\n        sns.barplot(data=query_result, x="City", y="Num_Providers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    # 2. Receivers per City\n    elif selected_query == "2. Receivers per City":\n        st.write("### 👥 Receivers per City")\n        plt.figure(figsize=(8,5))\n        sns.barplot(data=query_result, x="City", y="Num_Receivers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    # 3. Top Provider Type by Contributions\n    elif selected_query == "3. Top Provider Type by Contributions":\n        st.write("### 🍴 Provider Type Contributions")\n        plt.figure(figsize=(6,4))\n        sns.barplot(data=query_result, x="Provider_Type", y="Total_Quantity")\n        st.pyplot(plt)\n\n    # 4. Contact Info (table only, no chart)\n    elif selected_query == "4. Contact Info of Providers in a City":\n        st.write("📞 Provider Contact Info (Table Only)")\n\n    # 5. Receivers with Most Food Claimed\n    elif selected_query == "5. Receivers with Most Food Claimed":\n        st.write("### 🏆 Top Receivers by Food Claimed")\n        plt.figure(figsize=(10,6))\n        sns.barplot(data=query_result.head(10), x="Total_Claimed", y="Name")\n        st.pyplot(plt)\n\n    # 6. Total Quantity of Food Available\n    elif selected_query == "6. Total Quantity of Food Available":\n        st.write("### 📦 Total Food Available")\n        st.metric("Total Available Quantity", int(query_result["Total_Available"].iloc[0]))\n\n    # 7. City with Highest Number of Food Listings\n    elif selected_query == "7. City with Highest Number of Food Listings":\n        st.write("### 🏙️ Top City by Food Listings")\n        plt.figure(figsize=(6,4))\n        sns.barplot(data=query_result, x="Location", y="Num_Listings")\n        st.pyplot(plt)\n\n    # 8. Most Commonly Available Food Types\n    elif selected_query == "8. Most Commonly Available Food Types":\n        st.write("### 🥗 Food Type Breakdown")\n        plt.figure(figsize=(6,6))\n        plt.pie(query_result["Frequency"], labels=query_result["Food_Type"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    # 9. Number of Claims per Food Item\n    elif selected_query == "9. Number of Claims per Food Item":\n        st.write("### 📊 Claims per Food Item")\n        plt.figure(figsize=(10,6))\n        sns.barplot(data=query_result.head(15), x="Num_Claims", y="Food_Name")\n        st.pyplot(plt)\n\n    # 10. Provider with Highest Successful Claims\n    elif selected_query == "10. Provider with Highest Successful Claims":\n        st.write("### 🥘 Top Provider by Successful Claims")\n        plt.figure(figsize=(8,5))\n        sns.barplot(data=query_result, x="Successful_Claims", y="Name")\n        st.pyplot(plt)\n\n    # 11. Claim Status Distribution\n    elif selected_query == "11. Claim Status Distribution":\n        st.write("### ✅ Claim Status Distribution")\n        plt.figure(figsize=(6,6))\n        plt.pie(query_result["Percentage"], labels=query_result["Status"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    # 12. Average Quantity Claimed per Receiver\n    elif selected_query == "12. Average Quantity of Food Claimed per Receiver":\n        st.write("### 📈 Average Claimed Quantity per Receiver")\n        plt.figure(figsize=(10,6))\n        sns.barplot(data=query_result.head(15), x="Avg_Claimed", y="Name")\n        st.pyplot(plt)\n\n    # 13. Most Claimed Meal Type\n    elif selected_query == "13. Most Claimed Meal Type":\n        st.write("### 🍽️ Most Claimed Meal Type")\n        plt.figure(figsize=(6,4))\n        sns.barplot(data=query_result, x="Meal_Type", y="Num_Claims")\n        st.pyplot(plt)\n\n    # 14. Total Quantity Donated by Each Provider\n    elif selected_query == "14. Total Quantity Donated by Each Provider":\n        st.write("### 🥘 Provider Contributions")\n        plt.figure(figsize=(10,6))\n        sns.barplot(data=query_result.head(15), x="Total_Donated", y="Name")\n        st.pyplot(plt)\n\n    # 15. Highest Demand City by Claims\n    elif selected_query == "15. Highest Demand City by Claims":\n        st.write("### 🏙️ Highest Demand City (Claims)")\n        plt.figure(figsize=(8,5))\n        sns.barplot(data=query_result, x="City", y="Total_Claims")\n        st.pyplot(plt)\nselected_query = st.selectbox("Choose a Query", list(queries.keys()))\nquery_text = queries[selected_query]\nquery_result = get_data(query_text)\n\nst.write("### Query Result (Table)")\nst.dataframe(query_result)\n\n# Call visualization function\nvisualize_query(selected_query, query_result)\n# -------------------------------- PAGE 4: Creator Info --------------------------------\nelif page == "Creator Info":\n    st.title("👩\u200d💻 Creator of this Project")\n    st.write("""\n    **Developed by:** Saikiran Devunuri  \n    **Skills:** Python, SQL, Data Analysis,Streamlit, Pandas    \n    """)\n    st.image("https://via.placeholder.com/150", caption="Your Profile Picture", width=150)\n')


# In[79]:


get_ipython().run_cell_magic('writefile', 'app2.py', 'import streamlit as st\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport mysql.connector\n\n# -----------------------------\n# MySQL connection helpers\n# -----------------------------\ndef get_connection():\n    return mysql.connector.connect(\n        host="localhost",\n        user="root",\n        password="12345",\n        database="food_data"   \n    )\ndef queries_dict():\n    return {\n        # --- Providers & Receivers ---\n        "1. Food Providers per City": """\n            SELECT City, COUNT(*) AS Num_Providers\n            FROM providers\n            GROUP BY City\n            ORDER BY Num_Providers DESC;\n            Limit 5;\n        """,\n        "2. Receivers per City": """\n            SELECT City, COUNT(*) AS Num_Receivers\n            FROM receivers\n            GROUP BY City\n            ORDER BY Num_Receivers DESC;\n        """,\n        "3. Top Provider Type by Contributions": """\n            SELECT fl.Provider_Type, SUM(fl.Quantity) AS Total_Quantity\n            FROM foodlistings fl\n            GROUP BY fl.Provider_Type\n            ORDER BY Total_Quantity DESC;\n        """,\n        "4. Contact Info of Providers in a City (input)": """\n            SELECT Name, Contact, Address, City\n            FROM providers\n            WHERE City = %s;\n        """,\n        "5. Receivers with Most Food Claimed": """\n            SELECT r.Name, SUM(fl.Quantity) AS Total_Claimed\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID\n            WHERE c.Status = \'Completed\'\n            GROUP BY r.Name\n            ORDER BY Total_Claimed DESC;\n        """,\n\n        # --- Food Listings & Availability ---\n        "6. Total Quantity of Food Available": """\n            SELECT SUM(Quantity) AS Total_Available\n            FROM foodlistings;\n        """,\n        "7. City with Highest Number of Food Listings": """\n            SELECT Location, COUNT(*) AS Num_Listings\n            FROM foodlistings\n            GROUP BY Location\n            ORDER BY Num_Listings DESC;\n        """,\n        "8. Most Commonly Available Food Types": """\n            SELECT Food_Type, COUNT(*) AS Frequency\n            FROM foodlistings\n            GROUP BY Food_Type\n            ORDER BY Frequency DESC;\n        """,\n\n        # --- Claims & Distribution ---\n        "9. Number of Claims per Food Item": """\n            SELECT fl.Food_Name, COUNT(c.Claim_ID) AS Num_Claims\n            FROM foodlistings fl\n            LEFT JOIN claims c ON fl.Food_ID = c.Food_ID\n            GROUP BY fl.Food_Name\n            ORDER BY Num_Claims DESC;\n        """,\n        "10. Claims for a Specific Provider (input)": """\n            SELECT p.Name, COUNT(c.Claim_ID) AS Successful_Claims\n            FROM providers p\n            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID\n            JOIN claims c ON fl.Food_ID = c.Food_ID\n            WHERE c.Status = \'Completed\' AND p.Name = %s\n            GROUP BY p.Name;\n        """,\n        "11. Claim Status Distribution": """\n            SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage\n            FROM claims\n            GROUP BY Status;\n        """,\n\n        # --- Analysis & Insights ---\n        "12. Average Quantity of Food Claimed per Receiver": """\n            SELECT r.Name, AVG(fl.Quantity) AS Avg_Claimed\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            JOIN foodlistings fl ON c.Food_ID = fl.Food_ID\n            WHERE c.Status = \'Completed\'\n            GROUP BY r.Name\n            ORDER BY Avg_Claimed DESC;\n        """,\n        "13. Most Claimed Meal Type": """\n            SELECT fl.Meal_Type, COUNT(c.Claim_ID) AS Num_Claims\n            FROM foodlistings fl\n            JOIN claims c ON fl.Food_ID = c.Food_ID\n            WHERE c.Status IN (\'Completed\',\'Pending\',\'Cancelled\')\n            GROUP BY fl.Meal_Type\n            ORDER BY Num_Claims DESC;\n        """,\n        "14. Total Quantity Donated by Each Provider": """\n            SELECT p.Name, SUM(fl.Quantity) AS Total_Donated\n            FROM providers p\n            JOIN foodlistings fl ON p.Provider_ID = fl.Provider_ID\n            GROUP BY p.Name\n            ORDER BY Total_Donated DESC;\n        """,\n        "15. Highest Demand City by Claims": """\n            SELECT r.City, COUNT(c.Claim_ID) AS Total_Claims\n            FROM claims c\n            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID\n            GROUP BY r.City\n            ORDER BY Total_Claims DESC;\n        """\n    }\n\n\ndef visualize_query(selected_query, df):\n    if df.empty:\n        st.warning("⚠️ No data available for this query.")\n        return\n\n    if selected_query == "1. Food Providers per City":\n        st.write("### 🏢 Providers per City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Num_Providers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "2. Receivers per City":\n        st.write("### 👥 Receivers per City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Num_Receivers")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "3. Top Provider Type by Contributions":\n        st.write("### 🍴 Provider Type Contributions")\n        plt.figure(figsize=(7,4))\n        sns.barplot(data=df, x="Provider_Type", y="Total_Quantity")\n        st.pyplot(plt)\n\n    elif selected_query == "4. Contact Info of Providers in a City (input)":\n        st.info("Showing provider contact info table for selected city.")\n\n    elif selected_query == "5. Receivers with Most Food Claimed":\n        st.write("### 🏆 Top Receivers by Food Claimed")\n        plt.figure(figsize=(10,6))\n        top = df.head(15)\n        sns.barplot(data=top, x="Total_Claimed", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "6. Total Quantity of Food Available":\n        st.metric("Total Available Quantity", int(df["Total_Available"].iloc[0]))\n\n    elif selected_query == "7. City with Highest Number of Food Listings":\n        st.write("### 🏙️ Listings by City")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="Location", y="Num_Listings")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n\n    elif selected_query == "8. Most Commonly Available Food Types":\n        st.write("### 🥗 Food Type Breakdown")\n        plt.figure(figsize=(6,6))\n        plt.pie(df["Frequency"], labels=df["Food_Type"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    elif selected_query == "9. Number of Claims per Food Item":\n        st.write("### 📦 Claims per Food Item")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Num_Claims", y="Food_Name")\n        st.pyplot(plt)\n\n    elif selected_query == "10. Claims for a Specific Provider (input)":\n        st.write("### ✅ Successful Claims for Provider")\n        st.bar_chart(df.set_index(df.columns[0]))\n\n    elif selected_query == "11. Claim Status Distribution":\n        st.write("### 📊 Claim Status Distribution")\n        plt.figure(figsize=(6,6))\n        plt.pie(df["Percentage"], labels=df["Status"], autopct="%1.1f%%")\n        st.pyplot(plt)\n\n    elif selected_query == "12. Average Quantity of Food Claimed per Receiver":\n        st.write("### 📈 Avg Claimed Quantity per Receiver")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Avg_Claimed", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "13. Most Claimed Meal Type":\n        st.write("### 🍽️ Most Claimed Meal Type")\n        plt.figure(figsize=(7,4))\n        sns.barplot(data=df, x="Meal_Type", y="Num_Claims")\n        st.pyplot(plt)\n\n    elif selected_query == "14. Total Quantity Donated by Each Provider":\n        st.write("### 🥘 Provider Contributions")\n        plt.figure(figsize=(10,6))\n        top = df.head(20)\n        sns.barplot(data=top, x="Total_Donated", y="Name")\n        st.pyplot(plt)\n\n    elif selected_query == "15. Highest Demand City by Claims":\n        st.write("### 🏙️ Highest Demand Cities (Claims)")\n        plt.figure(figsize=(9,5))\n        sns.barplot(data=df, x="City", y="Total_Claims")\n        plt.xticks(rotation=45)\n        st.pyplot(plt)\n# -----------------------------\ndef get_data(query, params=()):\n    conn = get_connection()\n    df = pd.read_sql(query, conn, params=params)\n    conn.close()\n    return df\n\ndef execute_query(query, params=()):\n    conn = get_connection()\n    cur = conn.cursor()\n    cur.execute(query, params)\n    conn.commit()\n    cur.close()\n    conn.close()\n\n# -----------------------------\n# App config\n# -----------------------------\nst.set_page_config(page_title="Waste Food Management System", layout="wide")\n\n# -----------------------------\n# Sidebar\n# -----------------------------\nst.sidebar.title("Navigation")\npage = st.sidebar.radio(\n    "Go to",\n    ["Project Introduction", "CRUD Operations", "SQL Queries", "Waste Food Data Visualization", "Creator Info"]\n)\n\n# -----------------------------\n# Page 1: Introduction\n# -----------------------------\nif page == "Project Introduction":\n    st.title("Local Food Waste Management")\n    st.subheader("A Streamlit App for Exploring Local Waste Food Management Trends")\n    st.write(\n        """\nThis project analyzes food wastage and distribution. Restaurants and individuals can list surplus food; NGOs or individuals can claim it.\nData is stored in MySQL tables: `providers`, `receivers`, `food_listings`, `claims`.\n        """\n    )\n    st.markdown("**Database Used:** `food_database` (update in code if different)")\n\n# -----------------------------\n# Page 2: CRUD Operations\n# -----------------------------\nelif page == "CRUD Operations":\n\n    st.title("🔄 CRUD Operations")\n\n    tables = ["providers", "receivers", "food_listings", "claims"]\n    table = st.selectbox("Select Table", tables)\n\n    # Map primary key column names\n    id_map = {\n        "providers": "Provider_ID",\n        "receivers": "Receiver_ID",\n        "food_listings": "Food_ID",\n        "claims": "Claim_ID",\n    }\n    id_col = id_map[table]\n\n    # Load table\n    df = get_data(f"SELECT * FROM {table}")\n   \n\n    # ----- CREATE -----\n    st.subheader("➕ Create Record")\n    if df.shape[1] > 0:\n        with st.form(f"add_{table}"):\n            new_vals = {}\n            for col in df.columns:\n                if col == id_col:\n                    # Assume auto-increment; skip manual entry\n                    continue\n                new_vals[col] = st.text_input(f"Enter {col}")\n            submitted = st.form_submit_button("Add Record")\n            if submitted:\n                if len(new_vals) == 0:\n                    st.error("No columns to insert.")\n                else:\n                    cols = ", ".join(new_vals.keys())\n                    placeholders = ", ".join(["%s"] * len(new_vals))\n                    execute_query(\n                        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",\n                        tuple(new_vals.values())\n                    )\n                    st.success("✅ Record added successfully!")\n\n    # ----- UPDATE -----\n    if not df.empty:\n        st.subheader("✏️ Update Record")\n        record_id = st.selectbox("Select ID to Update", df[id_col].tolist())\n        with st.form(f"update_{table}"):\n            upd_vals = {}\n            for col in df.columns:\n                if col == id_col:\n                    continue\n                current_value = str(df.loc[df[id_col] == record_id, col].values[0])\n                upd_vals[col] = st.text_input(f"New {col}", value=current_value)\n            update_btn = st.form_submit_button("Update Record")\n            if update_btn:\n                set_clause = ", ".join([f"{col} = %s" for col in upd_vals.keys()])\n                params = tuple(upd_vals.values()) + (record_id,)\n                execute_query(\n                    f"UPDATE {table} SET {set_clause} WHERE {id_col} = %s",\n                    params\n                )\n                st.success("✅ Record updated successfully!")\n\n        # ----- DELETE -----\n        st.subheader("🗑️ Delete Record")\n        delete_id = st.selectbox("Select ID to Delete", df[id_col].tolist(), key=f"delete_{table}")\n        if st.button("Delete Record"):\n            execute_query(f"DELETE FROM {table} WHERE {id_col} = %s", (delete_id,))\n            st.success("✅ Record deleted successfully!")\n    else:\n        st.info("No records found in this table.")\n\n# -----------------------------\n# Shared: queries + visualizer\n# -----------------------------\n\n# Page 3: SQL Queries (table + viz)\nelif page == "SQL Queries":\n    st.title("SQL Query Results")\n    queries = queries_dict()\n    selected_query = st.selectbox("Choose a Query", list(queries.keys()))\n    params = ()\n\n    # Handle inputs\n    if selected_query == "4. Contact Info of Providers in a City (input)":\n        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()\n        city = st.selectbox("Select City", cities)\n        if city:\n            params = (city,)\n\n    if selected_query == "10. Claims for a Specific Provider (input)":\n        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()\n        provider = st.selectbox("Select Provider", providers)\n        if provider:\n            params = (provider,)\n\n    # Run\n    df = get_data(queries[selected_query], params)\n    st.write("### Query Result")\n    st.dataframe(df)\n\n\nelif page=="Waste Food Data Visualization":\n    st.title("📊 Waste Food Data Visualization")\n    queries = queries_dict()\n    selected_query = st.selectbox("Choose a Visualization Query", list(queries.keys()))\n    params = ()\n\n    if selected_query == "4. Contact Info of Providers in a City (input)":\n        cities = get_data("SELECT DISTINCT City FROM providers")["City"].tolist()\n        city = st.selectbox("Select City", cities)\n        if city:\n            params = (city,)\n\n    if selected_query == "10. Claims for a Specific Provider (input)":\n        providers = get_data("SELECT DISTINCT Name FROM providers")["Name"].tolist()\n        provider = st.selectbox("Select Provider", providers)\n        if provider:\n            params = (provider,)\n\n    df = get_data(queries[selected_query], params)\n    st.write("### Visualization")\n    visualize_query(selected_query, df)\n    \n# -----------------------------\n# Page 5: Creator Info\n# -----------------------------\nelif page == "Creator Info":\n    st.title("👩\u200d💻 Creator of this Project")\n    st.write(\n        """\n    **Developed by:** Saikiran Devunuri  \n    **Skills:** Python, SQL, Data Analysis, Streamlit, Pandas\n        """\n    )\n    st.image("https://via.placeholder.com/150", caption="Profile Picture", width=150)\n')


# In[ ]:


get_ipython().system('streamlit run app2.py')

