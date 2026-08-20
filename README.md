AI Query Builder and Result Display Application

Natural Language → SQL using an LLM and a relational database.

Project Overview

AI Query Builder is an AI-powered application that allows users to interact with a PostgreSQL database using natural language instead of manually writing SQL queries.

For example, a user can ask:

> "Show the employee who has the 2nd highest salary."

The application uses Google's Gemini API to understand the user's question, generate an SQL query based on the selected database schema, execute the query against PostgreSQL, and return the result.

Project Goal

The goal of this project is to build a practical AI application that connects a Large Language Model (LLM) with a relational database.

The project explores how natural-language interfaces can be used to make structured database systems easier to access while maintaining control over the SQL queries executed against the database.

How It Works

```text
User's Natural Language Question
              
      1.Select Database
              
      2.Retrieve Database Schema
              
      3. Gemini LLM
              
      4. Generate SQL
              
      5.Validate SQL
              
      6.PostgreSQL
              
      7.Query Result


Current Features:
Natural language → SQL query generation
Dynamic database selection
Google Gemini API integration
PostgreSQL database integration
Database schema awareness
Function/tool calling
Execution of generated SQL queries
SELECT-only query restriction
Environment-variable based API key management
Python virtual environment
Command-line user interaction
Basic database error handling

Development Progress:

Completed:
 Python environment setup
 PostgreSQL setup
 Python → PostgreSQL connection
 Gemini API integration
 Natural language user input
 SQL generation
 Database schema integration
 Database selection
 Function/tool calling
 Generated SQL execution
 SELECT-only query restriction
 Environment variable management
 Git/GitHub integration

Planned:
 Improve SQL validation
 Add stronger database permissions
 Add FastAPI backend
 Build a web interface
 Add authentication
 Add query history
 Add automated tests
 Add logging and monitoring
 Dockerize the application
 Deploy the application

 The project is being developed as a practical AI Engineering portfolio project, with the goal of demonstrating how an LLM can be integrated with a real relational database to build a useful and controlled AI application.