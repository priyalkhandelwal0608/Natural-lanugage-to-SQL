import sqlite3
import pandas as pd
from langchain_ollama import OllamaLLM

# ==========================================
# Create SQLite Database
# ==========================================
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [25, 30, 35, 40],
    "Salary": [50000, 60000, 70000, 80000]
}

df = pd.DataFrame(data)

# Create database connection
conn = sqlite3.connect("example.db")

# Store dataframe into SQL table
df.to_sql(
    "employees",
    conn,
    index=False,
    if_exists="replace"
)

print("Database ready!")

# ==========================================
# Load Ollama LLM
# ==========================================
# Make sure Ollama is running:
# ollama run llama3

llm = OllamaLLM(
    model="llama3",
    base_url="http://localhost:11434"
)

# ==========================================
# Function to Handle Questions
# ==========================================
def ask_db(question: str) -> str:

    question_lower = question.lower()

    # --------------------------------------
    # Natural Language → SQL
    # --------------------------------------

    if ("average" in question_lower or "avg" in question_lower) and "salary" in question_lower:

        sql = "SELECT AVG(Salary) AS avg_salary FROM employees"

    elif (
        ("maximum" in question_lower or "highest" in question_lower or "max" in question_lower)
        and "salary" in question_lower
    ):

        sql = "SELECT MAX(Salary) AS highest_salary FROM employees"

    elif (
        ("minimum" in question_lower or "lowest" in question_lower or "min" in question_lower)
        and "salary" in question_lower
    ):

        sql = "SELECT MIN(Salary) AS lowest_salary FROM employees"

    elif "count" in question_lower or "number of employees" in question_lower:

        sql = "SELECT COUNT(*) AS total_employees FROM employees"

    elif "list employees" in question_lower or "show employees" in question_lower:

        sql = "SELECT * FROM employees"

    elif "under" in question_lower and "age" in question_lower:

        age = int(''.join(filter(str.isdigit, question)))

        sql = f"""
        SELECT * FROM employees
        WHERE Age < {age}
        """

    elif (
        ("more than" in question_lower or "greater than" in question_lower)
        and "salary" in question_lower
    ):

        salary = int(''.join(filter(str.isdigit, question)))

        sql = f"""
        SELECT * FROM employees
        WHERE Salary > {salary}
        """

    elif (
        ("less than" in question_lower or "below" in question_lower)
        and "salary" in question_lower
    ):

        salary = int(''.join(filter(str.isdigit, question)))

        sql = f"""
        SELECT * FROM employees
        WHERE Salary < {salary}
        """

    else:

        sql = "SELECT * FROM employees LIMIT 5"

    # --------------------------------------
    # Show Generated SQL
    # --------------------------------------
    print("\nGenerated SQL:")
    print(sql)

    # --------------------------------------
    # Execute SQL
    # --------------------------------------
    try:

        result = pd.read_sql_query(sql, conn)

    except Exception as e:

        return f"SQL Error: {e}"

    # --------------------------------------
    # Convert Result to Text
    # --------------------------------------
    result_str = result.to_string(index=False)

    # --------------------------------------
    # Prompt for Ollama
    # --------------------------------------
    prompt = f"""
    You are an assistant that explains SQL query results.

    SQL Result:
    {result_str}

    Explain the result in simple English.
    """

    # --------------------------------------
    # Ask Ollama
    # --------------------------------------
    try:

        response = llm.invoke(prompt)

        return response

    except Exception as e:

        return f"Ollama Error: {e}"

# ==========================================
# Interactive Chat Loop
# ==========================================
print("\nAsk questions about the employees database")
print("Type 'exit' to quit\n")

while True:

    question = input("Your question: ")

    if question.lower() in ["exit", "quit"]:

        print("Goodbye!")
        break

    answer = ask_db(question)

    print("\nOllama Response:")
    print(answer)
    print()
