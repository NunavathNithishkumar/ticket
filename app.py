# from flask import Flask, request, jsonify, render_template
# import google.generativeai as genai
# import speech_recognition as sr
# import os
# from tempfile import NamedTemporaryFile
# import uuid
# import mysql.connector
# from datetime import datetime

# # -----------------
# # Imported data modules
# # -----------------
# from hsn_data import hsn_data
# from sac_data import sac_data
# from error import error_data
# from predata import pre_fed_data

# # -----------------
# # Configure Generative AI
# # -----------------
# genai.configure(api_key="AIzaSyCy5jnoDRAXpCHqTsm1uT6lN33R2MYfgxw")

# # Create the model configuration
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
# }

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
# )

# # -----------------
# # Conversation History Management
# # -----------------
# conversation_history = {}

# def format_conversation_history(history):
#     """Format conversation history for prompt."""
#     formatted_history = ""
#     for message in history:
#         role = "User" if message["role"] == "user" else "Sensei"
#         formatted_history += f"{role}: {message['content']}\n"
#     return formatted_history

# def classify_query(query):
#     """Classify the user's query into HSN, SAC, or GENERAL."""
#     query_lower = query.lower()
#     hsn_keywords = ["hsn", "gst rate", "product code", "chapter details"]
#     sac_keywords = ["sac", "service code"]
    
#     if any(k in query_lower for k in hsn_keywords):
#         return "HSN"
#     elif any(k in query_lower for k in sac_keywords):
#         return "SAC"
#     return "GENERAL"

# def generate_response(query, session_id):
#     """Generate a chatbot response with reference data based on query classification."""
#     query_type = classify_query(query)
#     if query_type == "HSN":
#         reference_data = hsn_data
#     elif query_type == "SAC":
#         reference_data = sac_data
#     else:
#         reference_data = pre_fed_data
    
#     # Make sure we track conversation
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
#     You are Sensei, an intelligent chatbot here to assist with user queries. Your responses should always be:
#     1. First, analyze the user's message: If the user greets you (e.g., saying 'Hi', 'Hello', 'Hey'), respond warmly and introduce yourself. For example: "Hi, I'm Sensei. How can I assist you today?" follow this only when the user greets. and if user asks any other query other than greeting, then do not say "Hi" or "Hello" or "Hey".
#     2. Based on the following information: {reference_data}
#     3. Clear, concise, and directly answering the user's query without mentioning the paragraph above as your source.
#     4. Adaptable to the ongoing conversation. If the user says things like "Nice" or "Cool," acknowledge and respond appropriately to maintain a conversational flow.
#     5. If you don't understand the query, politely ask the user for clarification (e.g., "Could you please provide more details?").
#     6. For follow-up questions, refer to the conversation history to maintain context.
#     7. Keep the tone friendly, professional, and engaging.
#     8. When asked if something is correct or not, compare with your knowledge and provide a clear yes/no answer with explanation.

#     Previous conversation:
#     {format_conversation_history(conversation_history[session_id])}

#     Now respond to this query: {query}
#     """
#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     # Update conversation
#     conversation_history[session_id].append({"role": "user", "content": query})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     # Limit to last 10 messages
#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# def add_website_link(response_text, query):
#     """Append website links based on certain keywords."""
#     query_lower = query.lower()
#     if any(k in query_lower for k in ["product", "trusty money", "trustee money"]):
#         response_text += "\n\nFor more details, visit: demo.trustymoney.in"
#     elif any(k in query_lower for k in ["payment", "invoice", "transaction"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/invoice"
#     elif any(k in query_lower for k in ["subscriptions", "subscription"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/subscriptions"
#     elif any(k in query_lower for k in ["hsn","sac","gst rate","service code"]):
#         response_text += "\n\nKnow your HSN/SAC code at https://services.gst.gov.in/services/searchhsnsac and Know your GST Rates at https://cbic-gst.gov.in/gst-goods-services-rates.html"
#     return response_text

# # -----------------
# # Enhanced classify_error: Return "YES", "NO", or "MAYBE"
# # -----------------
# def classify_error(error, session_id):
#     """
#     Classify error to see if team intervention is required or not.
#     Now we can return "YES", "NO", or "MAYBE" to be more granular:
#        - "YES" => Team intervention definitely needed
#        - "NO"  => Team intervention definitely not needed
#        - "MAYBE" => "No initial intervention, but if user insists, escalate"
#     """
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
#     You are an assistant trained to classify and resolve errors. Respond to the following query: "{error}". Use the available error data, {error_data}, to find a solution.

#     Follow these instructions:
#     1. Determine if the query requires team intervention ("YES"), does not require it ("NO"), or if it might require it after user retries ("MAYBE").
#     2. If the data explicitly says "No initial intervention, if persists then yes", classify as "MAYBE".
#     3. Return in the format: "CLASSIFICATION: YES|NO|MAYBE\nSOLUTION: <the textual solution from error_data if any>" or "No solution available".
#     4. Provide your response clearly, based on the available information.
#     5. Do not mention you are using data to answer the queries.
#     6. If the error does not require the team intervention then just return the answer provided in the data.
#     7. If the error is not in the data, you can say "TEAM" if it definitely needs escalation or "No solution" if no info found.

#     Example Output:
#     CLASSIFICATION: NO
#     SOLUTION: Please ensure the document meets the required size and file type. Modify the document as needed and upload again.

#     or 

#     CLASSIFICATION: MAYBE
#     SOLUTION: This issue is typically resolved by waiting. If it persists, raise a ticket.
#     """

#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     conversation_history[session_id].append({"role": "user", "content": error})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# # -----------------
# # Database / Tickets
# # -----------------
# def setup_database():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tickets (
#             ticket_id VARCHAR(20) PRIMARY KEY,
#             issue_title TEXT NOT NULL,
#             issue_description TEXT NOT NULL,
#             priority ENUM('High', 'Medium', 'Low') NOT NULL,
#             additional_details TEXT,
#             status ENUM('Open', 'In Progress', 'Closed') DEFAULT 'Open',
#             created_at TIMESTAMP,
#             updated_at TIMESTAMP
#         )
#     ''')
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS transactions (
#             transaction_id INT AUTO_INCREMENT PRIMARY KEY,
#             sender VARCHAR(255),
#             receiver VARCHAR(255),
#             amount DECIMAL(10, 2),
#             date TIMESTAMP,
#             status ENUM('Completed', 'Processing', 'Failed') DEFAULT 'Processing'
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def generate_ticket_id():
#     return str(uuid.uuid4())[:8]

# def save_ticket(title, description, priority, additional_details=None):
#     ticket_id = generate_ticket_id()
#     created_at = updated_at = datetime.now()
    
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="Nunavath",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO tickets (ticket_id, issue_title, issue_description, priority, additional_details, status, created_at, updated_at)
#         VALUES (%s, %s, %s, %s, %s, 'Open', %s, %s)
#     ''', (ticket_id, title, description, priority, additional_details, created_at, updated_at))
#     conn.commit()
#     conn.close()
#     return ticket_id

# def get_transaction_details(transaction_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="kumar",
#         password="kumar@58525",
#         database="transaction_db"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return (f"Transaction ID: {result[0]}\n"
#                 f"Sender: {result[1]}\n"
#                 f"Receiver: {result[2]}\n"
#                 f"Amount: {result[3]}\n"
#                 f"Date: {result[4]}\n"
#                 f"Status: {result[5]}")
#     else:
#         return None

# def get_ticket_status(ticket_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT status FROM tickets WHERE ticket_id = %s", (ticket_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return f"Ticket ID: {ticket_id}\nStatus: {result[0]}"
#     else:
#         return None

# # -----------------
# # Flask App
# # -----------------
# app = Flask(__name__)

# @app.route("/")
# def index():
#     # Make sure chat_index.html is in /templates folder
#     return render_template("chat_index.html")

# @app.route("/setup_database", methods=["GET"])
# def route_setup_database():
#     try:
#         setup_database()
#         return jsonify({"message": "Database setup completed successfully."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 1) Get Transaction
# @app.route("/get_transaction", methods=["POST"])
# def route_get_transaction():
#     try:
#         data = request.json
#         txn_id = data.get("transaction_id", "").strip()
#         if not txn_id:
#             return jsonify({"error": "Transaction ID is required."}), 400
#         txn_details = get_transaction_details(txn_id)
#         if txn_details:
#             return jsonify({"transaction_details": txn_details})
#         else:
#             return jsonify({"message": "Transaction not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 2) Classify Error
# @app.route("/classify_error", methods=["POST"])
# def route_classify_error():
#     """
#     Step to check if error requires team intervention or not.
#     Now we return a structured response:
#         {
#           "classification": "YES" / "NO" / "MAYBE",
#           "solution": "<some text from error_data or a fallback>"
#         }
#     """
#     try:
#         data = request.json
#         error_msg = data.get("error", "")
#         session_id = data.get("session_id", "default_error_sess")

#         if not error_msg:
#             return jsonify({"error": "Error message is required."}), 400

#         classify_result = classify_error(error_msg, session_id)

#         # We expect the classification in the format:
#         #   CLASSIFICATION: YES|NO|MAYBE
#         #   SOLUTION: ...
#         classification = "NO"
#         solution = "No solution provided."

#         lines = classify_result.splitlines()
#         for line in lines:
#             if line.upper().startswith("CLASSIFICATION:"):
#                 classification = line.split(":")[1].strip().upper()
#             elif line.upper().startswith("SOLUTION:"):
#                 solution = line.split(":", 1)[1].strip()

#         # Construct our JSON
#         return jsonify({
#             "classification": classification,
#             "solution": solution
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 3) Raise Ticket
# @app.route("/raise_ticket", methods=["POST"])
# def route_raise_ticket():
#     """If classification says 'YES' or user insists, user can fill ticket details."""
#     try:
#         data = request.json
#         title = data.get("issue_title", "No Title")
#         description = data.get("issue_description", "No Description")
#         priority = data.get("priority", "Low").capitalize()
#         additional = data.get("additional_details", "")

#         if priority not in ["High", "Medium", "Low"]:
#             return jsonify({"error": "Invalid priority. Use High, Medium, or Low."}), 400

#         ticket_id = save_ticket(title, description, priority, additional)
#         return jsonify({"message": f"Ticket created successfully. ID: {ticket_id}"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 4) Ticket Status
# @app.route("/ticket_status", methods=["POST"])
# def route_ticket_status():
#     try:
#         data = request.json
#         tid = data.get("ticket_id", "").strip()
#         if not tid:
#             return jsonify({"error": "Ticket ID is required."}), 400
#         status_info = get_ticket_status(tid)
#         if status_info:
#             return jsonify({"ticket_info": status_info})
#         else:
#             return jsonify({"message": "Ticket not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 5) Ask Chatbot
# @app.route("/ask_chatbot", methods=["POST"])
# def route_ask_chatbot():
#     try:
#         data = request.json
#         query = data.get("query", "")
#         session_id = data.get("session_id", "default_chat_sess")
#         if not query:
#             return jsonify({"error": "Query is required."}), 400

#         bot_res = generate_response(query, session_id)
#         with_link = add_website_link(bot_res, query)
#         return jsonify({"response": with_link})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)


















# ---------------------------------------
# perfectly working app.py
# ---------------------------------------
# from flask import Flask, request, jsonify, render_template
# import google.generativeai as genai
# import speech_recognition as sr
# import os
# from tempfile import NamedTemporaryFile
# import uuid
# import mysql.connector
# from datetime import datetime

# # -----------------
# # Imported data modules
# # -----------------
# from hsn_data import hsn_data
# from sac_data import sac_data
# from error import error_data  # <-- Make sure to import your updated error_data
# from predata import pre_fed_data

# # -----------------
# # Configure Generative AI
# # -----------------
# genai.configure(api_key="AIzaSyCy5jnoDRAXpCHqTsm1uT6lN33R2MYfgxw")  # put your own key

# # Create the model configuration
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
# }

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
# )

# # -----------------
# # Conversation History Management
# # -----------------
# conversation_history = {}

# def format_conversation_history(history):
#     """Format conversation history for prompt."""
#     formatted_history = ""
#     for message in history:
#         role = "User" if message["role"] == "user" else "Sensei"
#         formatted_history += f"{role}: {message['content']}\n"
#     return formatted_history

# def classify_query(query):
#     """Classify the user's query into HSN, SAC, or GENERAL."""
#     query_lower = query.lower()
#     hsn_keywords = ["hsn", "gst rate", "product code", "chapter details"]
#     sac_keywords = ["sac", "service code"]
    
#     if any(k in query_lower for k in hsn_keywords):
#         return "HSN"
#     elif any(k in query_lower for k in sac_keywords):
#         return "SAC"
#     return "GENERAL"

# def generate_response(query, session_id):
#     """Generate a chatbot response with reference data based on query classification."""
#     query_type = classify_query(query)
#     if query_type == "HSN":
#         reference_data = hsn_data
#     elif query_type == "SAC":
#         reference_data = sac_data
#     else:
#         reference_data = pre_fed_data
    
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
#      You are Sensei, an intelligent chatbot here to assist with user queries. Your responses should always be:
#       1. First, analyze the user's message: If the user greets you (e.g., saying 'Hi', 'Hello', 'Hey'), respond warmly and introduce yourself. For example: "Hi, I'm Sensei. How can I assist you today?" follow this only when the user greets. and if user asks any other query other than greeting, then do not say "Hi" or "Hello" or "Hey".
#       2. Based on the following information: {reference_data}
#       3. Clear, concise, and directly answering the user's query without mentioning the paragraph above as your source.
#       4. Adaptable to the ongoing conversation. If the user says things like "Nice" or "Cool," acknowledge and respond appropriately to maintain a conversational flow.
#       5. If you don't understand the query, politely ask the user for clarification (e.g., "Could you please provide more details?").
#       6. For follow-up questions, refer to the conversation history to maintain context.
#       7. Keep the tone friendly, professional, and engaging.
#       8. When asked if something is correct or not, compare with your knowledge and provide a clear yes/no answer with explanation.

#     Previous conversation:
#     {format_conversation_history(conversation_history[session_id])}

#     Now respond to this query: {query}
#     """
#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     # Update conversation
#     conversation_history[session_id].append({"role": "user", "content": query})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     # Limit to last 10 messages
#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# def add_website_link(response_text, query):
#     """Append website links based on certain keywords."""
#     query_lower = query.lower()
#     if any(k in query_lower for k in ["product", "trusty money", "trustee money"]):
#         response_text += "\n\nFor more details, visit: demo.trustymoney.in"
#     elif any(k in query_lower for k in ["payment", "invoice", "transaction"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/invoice"
#     elif any(k in query_lower for k in ["subscriptions", "subscription"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/subscriptions"
#     elif any(k in query_lower for k in ["hsn","sac","gst rate","service code"]):
#         response_text += "\n\nKnow your HSN/SAC code at https://services.gst.gov.in/services/searchhsnsac and Know your GST Rates at https://cbic-gst.gov.in/gst-goods-services-rates.html"
#     return response_text

# # -----------------
# # classify_error function
# # -----------------
# def classify_error(error, session_id):
#     """
#     Classify error into: YES, NO, MAYBE, or UNKNOWN.
#       - YES => Team definitely needed
#       - NO  => The user can solve it themselves
#       - MAYBE => Try first, if persists => escalate
#       - UNKNOWN => Not found in error_data
#     """
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
#     You are an assistant trained to classify and resolve errors. Respond to the following query: "{error}" 
#     using the available error data, {error_data}.

#     1. If the error definitely requires team => CLASSIFICATION: YES
#     2. If it is found and does NOT require team => CLASSIFICATION: NO
#     3. If it is found but "No initial intervention, if persists => team" => CLASSIFICATION: MAYBE
#     4. If the error does not appear in error_data => CLASSIFICATION: UNKNOWN

#     Then provide a short solution or fallback. Format exactly:
#     CLASSIFICATION: <YES|NO|MAYBE|UNKNOWN>
#     SOLUTION: <the textual solution from error_data or fallback message>
#     """

#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     conversation_history[session_id].append({"role": "user", "content": error})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# # -----------------
# # Database / Tickets
# # -----------------
# def setup_database():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="Nunavath",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tickets (
#             ticket_id VARCHAR(20) PRIMARY KEY,
#             issue_title TEXT NOT NULL,
#             issue_description TEXT NOT NULL,
#             priority ENUM('High', 'Medium', 'Low') NOT NULL,
#             additional_details TEXT,
#             status ENUM('Open', 'In Progress', 'Closed') DEFAULT 'Open',
#             created_at TIMESTAMP,
#             updated_at TIMESTAMP
#         )
#     ''')
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS transactions (
#             transaction_id INT AUTO_INCREMENT PRIMARY KEY,
#             sender VARCHAR(255),
#             receiver VARCHAR(255),
#             amount DECIMAL(10, 2),
#             date TIMESTAMP,
#             status ENUM('Completed', 'Processing', 'Failed') DEFAULT 'Processing'
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def generate_ticket_id():
#     return str(uuid.uuid4())[:8]

# def save_ticket(title, description, priority, additional_details=None):
#     ticket_id = generate_ticket_id()
#     created_at = updated_at = datetime.now()
    
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="Nunavath",  # or your db username
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO tickets (ticket_id, issue_title, issue_description, priority, additional_details, status, created_at, updated_at)
#         VALUES (%s, %s, %s, %s, %s, 'Open', %s, %s)
#     ''', (ticket_id, title, description, priority, additional_details, created_at, updated_at))
#     conn.commit()
#     conn.close()
#     return ticket_id

# def get_transaction_details(transaction_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="kumar",
#         password="kumar@58525",
#         database="transaction_db"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return (f"Transaction ID: {result[0]}\n"
#                 f"Sender: {result[1]}\n"
#                 f"Receiver: {result[2]}\n"
#                 f"Amount: {result[3]}\n"
#                 f"Date: {result[4]}\n"
#                 f"Status: {result[5]}")
#     else:
#         return None

# def get_ticket_status(ticket_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="Nunavath",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT status FROM tickets WHERE ticket_id = %s", (ticket_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return f"Ticket ID: {ticket_id}\nStatus: {result[0]}"
#     else:
#         return None

# # -----------------
# # Flask App
# # -----------------
# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("chat_index.html")

# @app.route("/setup_database", methods=["GET"])
# def route_setup_database():
#     try:
#         setup_database()
#         return jsonify({"message": "Database setup completed successfully."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 1) Get Transaction
# @app.route("/get_transaction", methods=["POST"])
# def route_get_transaction():
#     try:
#         data = request.json
#         txn_id = data.get("transaction_id", "").strip()
#         if not txn_id:
#             return jsonify({"error": "Transaction ID is required."}), 400
#         txn_details = get_transaction_details(txn_id)
#         if txn_details:
#             return jsonify({"transaction_details": txn_details})
#         else:
#             return jsonify({"message": "Transaction not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 2) Classify Error
# @app.route("/classify_error", methods=["POST"])
# def route_classify_error():
#     """
#     We'll parse the LLM's response and return JSON like:
#       {
#         "classification": "YES" / "NO" / "MAYBE" / "UNKNOWN",
#         "solution": "..."
#       }
#     """
#     try:
#         data = request.json
#         error_msg = data.get("error", "")
#         session_id = data.get("session_id", "default_error_sess")

#         if not error_msg:
#             return jsonify({"error": "Error message is required."}), 400

#         classify_result = classify_error(error_msg, session_id)

#         classification = "UNKNOWN"
#         solution = "No solution found."

#         lines = classify_result.splitlines()
#         for line in lines:
#             if line.upper().startswith("CLASSIFICATION:"):
#                 classification = line.split(":", 1)[1].strip().upper()
#             elif line.upper().startswith("SOLUTION:"):
#                 solution = line.split(":", 1)[1].strip()

#         return jsonify({
#             "classification": classification,
#             "solution": solution
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 3) Raise Ticket
# @app.route("/raise_ticket", methods=["POST"])
# def route_raise_ticket():
#     try:
#         data = request.json
#         title = data.get("issue_title", "No Title")
#         description = data.get("issue_description", "No Description")
#         priority = data.get("priority", "Low").capitalize()
#         additional = data.get("additional_details", "")

#         if priority not in ["High", "Medium", "Low"]:
#             return jsonify({"error": "Invalid priority. Use High, Medium, or Low."}), 400

#         ticket_id = save_ticket(title, description, priority, additional)
#         return jsonify({"message": f"Ticket created successfully. ID: {ticket_id}"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 4) Ticket Status
# @app.route("/ticket_status", methods=["POST"])
# def route_ticket_status():
#     try:
#         data = request.json
#         tid = data.get("ticket_id", "").strip()
#         if not tid:
#             return jsonify({"error": "Ticket ID is required."}), 400
#         status_info = get_ticket_status(tid)
#         if status_info:
#             return jsonify({"ticket_info": status_info})
#         else:
#             return jsonify({"message": "Ticket not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 5) Ask Chatbot
# @app.route("/ask_chatbot", methods=["POST"])
# def route_ask_chatbot():
#     try:
#         data = request.json
#         query = data.get("query", "")
#         session_id = data.get("session_id", "default_chat_sess")
#         if not query:
#             return jsonify({"error": "Query is required."}), 400

#         bot_res = generate_response(query, session_id)
#         with_link = add_website_link(bot_res, query)
#         return jsonify({"response": with_link})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)
















#############################################
# app.py
#############################################
# from flask import Flask, request, jsonify, render_template
# import google.generativeai as genai
# import speech_recognition as sr
# import os
# from tempfile import NamedTemporaryFile
# import uuid
# import mysql.connector
# from datetime import datetime

# # -----------------
# # Imported data modules
# # -----------------
# from hsn_data import hsn_data
# from sac_data import sac_data
# from error import error_data
# from predata import pre_fed_data

# # -----------------
# # Configure Generative AI
# # -----------------
# genai.configure(api_key="AIzaSyCy5jnoDRAXpCHqTsm1uT6lN33R2MYfgxw")

# # Create the model configuration
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
# }

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
# )

# # -----------------
# # Conversation History Management
# # -----------------
# conversation_history = {}

# def format_conversation_history(history):
#     """Format conversation history for prompt."""
#     formatted_history = ""
#     for message in history:
#         role = "User" if message["role"] == "user" else "Sensei"
#         formatted_history += f"{role}: {message['content']}\n"
#     return formatted_history

# def classify_query(query):
#     """Classify the user's query into HSN, SAC, or GENERAL."""
#     query_lower = query.lower()
#     hsn_keywords = ["hsn", "gst rate", "product code", "chapter details"]
#     sac_keywords = ["sac", "service code"]
    
#     if any(k in query_lower for k in hsn_keywords):
#         return "HSN"
#     elif any(k in query_lower for k in sac_keywords):
#         return "SAC"
#     return "GENERAL"

# def generate_response(query, session_id):
#     """Generate a chatbot response with reference data based on query classification."""
#     query_type = classify_query(query)
#     if query_type == "HSN":
#         reference_data = hsn_data
#     elif query_type == "SAC":
#         reference_data = sac_data
#     else:
#         reference_data = pre_fed_data
    
#     # Make sure we track conversation
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
    # You are Sensei, an intelligent chatbot here to assist with user queries. Your responses should always be:
    # 1. First, analyze the user's message: If the user greets you (e.g., saying 'Hi', 'Hello', 'Hey'), respond warmly and introduce yourself. 
    #    For example: "Hi, I'm Sensei. How can I assist you today?" follow this only when the user greets. 
    #    If user asks any other query other than greeting, then do not say "Hi" or "Hello" or "Hey".
    # 2. Based on the following information: {reference_data}
    # 3. Clear, concise, and directly answering the user's query without mentioning the paragraph above as your source.
    # 4. Adaptable to the ongoing conversation. If the user says things like "Nice" or "Cool," acknowledge and respond appropriately.
    # 5. If you don't understand the query, politely ask for clarification (e.g., "Could you please provide more details?").
    # 6. For follow-up questions, refer to the conversation history to maintain context.
    # 7. Keep the tone friendly, professional, and engaging.
    # 8. When asked if something is correct or not, compare with your knowledge and provide a clear yes/no answer with explanation.

#     Previous conversation:
#     {format_conversation_history(conversation_history[session_id])}

#     Now respond to this query: {query}
#     """
#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     # Update conversation
#     conversation_history[session_id].append({"role": "user", "content": query})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     # Limit to last 10 messages
#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# def add_website_link(response_text, query):
#     """Append website links based on certain keywords."""
#     query_lower = query.lower()
#     if any(k in query_lower for k in ["product", "trusty money", "trustee money"]):
#         response_text += "\n\nFor more details, visit: demo.trustymoney.in"
#     elif any(k in query_lower for k in ["payment", "invoice", "transaction"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/invoice"
#     elif any(k in query_lower for k in ["subscriptions", "subscription"]):
#         response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/subscriptions"
#     elif any(k in query_lower for k in ["hsn","sac","gst rate","service code"]):
#         response_text += "\n\nKnow your HSN/SAC code at https://services.gst.gov.in/services/searchhsnsac and Know your GST Rates at https://cbic-gst.gov.in/gst-goods-services-rates.html"
#     return response_text

# def classify_error(error, session_id):
#     """
#     Classify error to see if team intervention is required or not.
#     If 'Yes' => Team intervention needed.
#     Otherwise => Return solution from error_data.
#     """
#     if session_id not in conversation_history:
#         conversation_history[session_id] = []
    
#     system_prompt = f"""
#     You are an assistant trained to classify and resolve errors. Respond to the following query: "{error}". 
#     Use the available error data, {error_data}, to find a solution.

#     Follow these instructions:
#     1. Determine if the query requires team intervention (Yes) or not (No).
#     2. Return in the format:
#        CLASSIFICATION: YES or NO
#        SOLUTION: <the textual solution from error_data or fallback>
#     """

#     chat = model.start_chat(history=[])
#     response = chat.send_message(system_prompt)

#     conversation_history[session_id].append({"role": "user", "content": error})
#     conversation_history[session_id].append({"role": "assistant", "content": response.text})

#     if len(conversation_history[session_id]) > 10:
#         conversation_history[session_id] = conversation_history[session_id][-10:]
    
#     return response.text

# # -----------------
# # Database / Tickets
# # -----------------
# def setup_database():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     # Make sure your tickets table has a LONGBLOB column for screenshots, for example:
#     # screenshot LONGBLOB
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS tickets (
#             ticket_id VARCHAR(20) PRIMARY KEY,
#             issue_title TEXT NOT NULL,
#             issue_description TEXT NOT NULL,
#             priority ENUM('High', 'Medium', 'Low') NOT NULL,
#             additional_details TEXT,
#             screenshot LONGBLOB,  -- for storing the uploaded screenshot as a BLOB
#             status ENUM('Open', 'In Progress', 'Closed') DEFAULT 'Open',
#             created_at TIMESTAMP,
#             updated_at TIMESTAMP
#         )
#     ''')
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS transactions (
#             transaction_id INT AUTO_INCREMENT PRIMARY KEY,
#             sender VARCHAR(255),
#             receiver VARCHAR(255),
#             amount DECIMAL(10, 2),
#             date TIMESTAMP,
#             status ENUM('Completed', 'Processing', 'Failed') DEFAULT 'Processing'
#         )
#     ''')
#     conn.commit()
#     conn.close()

# def generate_ticket_id():
#     return str(uuid.uuid4())[:8]

# def save_ticket(title, description, priority, additional_details=None, screenshot_blob=None):
#     """
#     Now we can accept an optional 'screenshot_blob' (bytes) for the screenshot.
#     We'll store that directly in the 'tickets' table's 'screenshot' column (LONGBLOB).
#     """
#     ticket_id = generate_ticket_id()
#     created_at = updated_at = datetime.now()
    
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="Nunavath",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     sql = '''
#         INSERT INTO tickets (
#             ticket_id, issue_title, issue_description, 
#             priority, additional_details, screenshot, 
#             status, created_at, updated_at
#         )
#         VALUES (%s, %s, %s, %s, %s, %s, 'Open', %s, %s)
#     '''
#     cursor.execute(sql, (
#         ticket_id, title, description, priority, additional_details, screenshot_blob,
#         created_at, updated_at
#     ))
#     conn.commit()
#     conn.close()
#     return ticket_id

# def get_transaction_details(transaction_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="kumar",
#         password="kumar@58525",
#         database="transaction_db"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return (f"Transaction ID: {result[0]}\n"
#                 f"Sender: {result[1]}\n"
#                 f"Receiver: {result[2]}\n"
#                 f"Amount: {result[3]}\n"
#                 f"Date: {result[4]}\n"
#                 f"Status: {result[5]}")
#     else:
#         return None

# def get_ticket_status(ticket_id):
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="Nithish@58525",
#         database="support_system"
#     )
#     cursor = conn.cursor()
#     cursor.execute("SELECT status FROM tickets WHERE ticket_id = %s", (ticket_id,))
#     result = cursor.fetchone()
#     conn.close()
#     if result:
#         return f"Ticket ID: {ticket_id}\nStatus: {result[0]}"
#     else:
#         return None

# # -----------------
# # Flask App
# # -----------------
# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("chat_index.html")

# @app.route("/setup_database", methods=["GET"])
# def route_setup_database():
#     try:
#         setup_database()
#         return jsonify({"message": "Database setup completed successfully."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 1) Get Transaction
# @app.route("/get_transaction", methods=["POST"])
# def route_get_transaction():
#     try:
#         data = request.json
#         txn_id = data.get("transaction_id", "").strip()
#         if not txn_id:
#             return jsonify({"error": "Transaction ID is required."}), 400
#         txn_details = get_transaction_details(txn_id)
#         if txn_details:
#             return jsonify({"transaction_details": txn_details})
#         else:
#             return jsonify({"message": "Transaction not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 2) Classify Error
# @app.route("/classify_error", methods=["POST"])
# def route_classify_error():
#     try:
#         data = request.json
#         error_msg = data.get("error", "")
#         session_id = data.get("session_id", "default_error_sess")

#         if not error_msg:
#             return jsonify({"error": "Error message is required."}), 400

#         classify_result = classify_error(error_msg, session_id)

#         classification = "NO"
#         solution = "No solution found."

#         lines = classify_result.splitlines()
#         for line in lines:
#             if line.upper().startswith("CLASSIFICATION:"):
#                 classification = line.split(":", 1)[1].strip().upper()
#             elif line.upper().startswith("SOLUTION:"):
#                 solution = line.split(":", 1)[1].strip()

#         if classification == "YES":
#             return jsonify({
#                 "requires_intervention": True,
#                 "response": "Team intervention is required for this error."
#             })
#         else:
#             return jsonify({
#                 "requires_intervention": False,
#                 "response": solution
#             })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 3) Raise Ticket
# @app.route("/raise_ticket", methods=["POST"])
# def route_raise_ticket():
#     """
#     Now accepts multipart/form-data so user can optionally upload a screenshot.
#     """
#     try:
#         # Because we might have a file, use request.form + request.files, NOT request.json
#         title = request.form.get("issue_title", "No Title")
#         description = request.form.get("issue_description", "No Description")
#         priority = request.form.get("priority", "Low").capitalize()
#         additional = request.form.get("additional_details", "")

#         if priority not in ["High", "Medium", "Low"]:
#             return jsonify({"error": "Invalid priority. Use High, Medium, or Low."}), 400

#         # Optional screenshot:
#         file_screenshot = request.files.get("screenshot")  # None if not provided
#         screenshot_data = None
#         if file_screenshot:
#             screenshot_data = file_screenshot.read()  # read entire file bytes

#         # save_ticket now can store a BLOB
#         ticket_id = save_ticket(
#             title,
#             description,
#             priority,
#             additional,
#             screenshot_blob=screenshot_data
#         )

#         return jsonify({"message": f"Ticket created successfully. ID: {ticket_id}"})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 4) Ticket Status
# @app.route("/ticket_status", methods=["POST"])
# def route_ticket_status():
#     try:
#         data = request.json
#         tid = data.get("ticket_id", "").strip()
#         if not tid:
#             return jsonify({"error": "Ticket ID is required."}), 400
#         status_info = get_ticket_status(tid)
#         if status_info:
#             return jsonify({"ticket_info": status_info})
#         else:
#             return jsonify({"message": "Ticket not found."})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # 5) Ask Chatbot
# @app.route("/ask_chatbot", methods=["POST"])
# def route_ask_chatbot():
#     try:
#         data = request.json
#         query = data.get("query", "")
#         session_id = data.get("session_id", "default_chat_sess")
#         if not query:
#             return jsonify({"error": "Query is required."}), 400

#         bot_res = generate_response(query, session_id)
#         with_link = add_website_link(bot_res, query)
#         return jsonify({"response": with_link})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)





###################################################
# app.py
###################################################
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import uuid
import mysql.connector
from datetime import datetime

# -----------------------
# 1) Imported data modules
# -----------------------
from hsn_data import hsn_data
from sac_data import sac_data
from error import error_data  # Make sure it marks "Unable to download the invoice" => No
from predata import pre_fed_data

# -----------------------
# 2) Configure Generative AI
# -----------------------
genai.configure(api_key="AIzaSyCy5jnoDRAXpCHqTsm1uT6lN33R2MYfgxw")

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    },
)

# -----------------------
# 3) Conversation History
# -----------------------
conversation_history = {}

def format_conversation_history(history):
    out = ""
    for msg in history:
        role = "User" if msg["role"]=="user" else "Sensei"
        out += f"{role}: {msg['content']}\n"
    return out

def classify_query(query):
    """Classify user query into HSN, SAC, or GENERAL."""
    qlower = query.lower()
    hsn_keywords = ["hsn", "gst rate", "product code", "chapter details"]
    sac_keywords = ["sac", "service code"]
    if any(k in qlower for k in hsn_keywords):
        return "HSN"
    elif any(k in qlower for k in sac_keywords):
        return "SAC"
    else:
        return "GENERAL"

def generate_response(query, session_id):
    """Generate a response from hsn/sac or general data."""
    cat = classify_query(query)
    if cat=="HSN":
        reference_data = hsn_data
    elif cat=="SAC":
        reference_data = sac_data
    else:
        reference_data = pre_fed_data

    if session_id not in conversation_history:
        conversation_history[session_id] = []

    system_prompt = f"""
  You are Sensei, an intelligent chatbot here to assist with user queries. Your responses should always be:
    1. First, analyze the user's message: If the user greets you (e.g., saying 'Hi', 'Hello', 'Hey'), respond warmly and introduce yourself. 
       For example: "Hi, I'm Sensei. How can I assist you today?" follow this only when the user greets. 
       If user asks any other query other than greeting, then do not say "Hi" or "Hello" or "Hey".
    2. Based on the following information: {reference_data}
    3. Clear, concise, and directly answering the user's query without mentioning the paragraph above as your source.
    4. Adaptable to the ongoing conversation. If the user says things like "Nice" or "Cool," acknowledge and respond appropriately.
    5. If you don't understand the query, politely ask for clarification (e.g., "Could you please provide more details?").
    6. For follow-up questions, refer to the conversation history to maintain context.
    7. Keep the tone friendly, professional, and engaging.
    8. When asked if something is correct or not, compare with your knowledge and provide a clear yes/no answer with explanation.


    Previous conversation:
    {format_conversation_history(conversation_history[session_id])}

    User's query: {query}
    """

    chat = model.start_chat(history=[])
    resp = chat.send_message(system_prompt)

    # track conversation
    conversation_history[session_id].append({"role":"user","content":query})
    conversation_history[session_id].append({"role":"assistant","content":resp.text})
    if len(conversation_history[session_id])>10:
        conversation_history[session_id] = conversation_history[session_id][-10:]

    return resp.text

def add_website_link(response_text, query):
    qlower = query.lower()
    if any(k in qlower for k in ["product","trusty money","trustee money"]):
        response_text += "\n\nFor more details, visit: demo.trustymoney.in"
    elif any(k in qlower for k in ["payment","invoice","transaction"]):
        response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/invoice"
    elif any(k in qlower for k in ["subscriptions","subscription"]):
        response_text += "\n\nFor more details, visit: https://demo.trustymoney.in/subscriptions"
    elif any(k in qlower for k in ["hsn","sac","gst rate","service code"]):
        response_text += "\n\nKnow your HSN/SAC code at https://services.gst.gov.in/services/searchhsnsac\n"
        response_text += "and Know your GST Rates at https://cbic-gst.gov.in/gst-goods-services-rates.html"
    return response_text

# -----------------------
# 4) classify_error => YES/NO/MAYBE/UNKNOWN
# -----------------------
def classify_error(error_msg, session_id):
    """
    Use the LLM to parse error_data and decide:
      CLASSIFICATION: YES|NO|MAYBE|UNKNOWN
      SOLUTION: ...
    """
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    system_prompt = f"""
    You are an assistant that classifies errors from this data:
    {error_data}

    For the error: "{error_msg}"
    Return exactly 2 lines:
      CLASSIFICATION: YES|NO|MAYBE|UNKNOWN
      SOLUTION: <the textual solution or fallback>
    Note: "Unable to download the invoice" => classification is NO 
          (since the data states no team intervention needed).
    """

    chat = model.start_chat(history=[])
    resp = chat.send_message(system_prompt)

    conversation_history[session_id].append({"role":"user","content":error_msg})
    conversation_history[session_id].append({"role":"assistant","content":resp.text})
    if len(conversation_history[session_id])>10:
        conversation_history[session_id] = conversation_history[session_id][-10:]

    return resp.text

# -----------------------
# 5) Database Setup & Tickets
# -----------------------
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def setup_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Nithish@58525",
        database="support_system"
    )
    cur = conn.cursor()
    # tickets with screenshot as LONGBLOB
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id VARCHAR(20) PRIMARY KEY,
            issue_title TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            priority ENUM('High','Medium','Low') NOT NULL,
            additional_details TEXT,
            screenshot LONGBLOB,
            status ENUM('Open','In Progress','Closed') DEFAULT 'Open',
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    # transactions
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(255),
            receiver VARCHAR(255),
            amount DECIMAL(10,2),
            date TIMESTAMP,
            status ENUM('Completed','Processing','Failed') DEFAULT 'Processing'
        )
    ''')
    conn.commit()
    conn.close()

def generate_ticket_id():
    return str(uuid.uuid4())[:8]

def save_ticket(title, desc, prio, addl=None, screenshot=None):
    ticket_id = generate_ticket_id()
    created_at = updated_at = datetime.now()

    conn = mysql.connector.connect(
        host="localhost",
        user="Nunavath",
        password="Nithish@58525",
        database="support_system"
    )
    cur = conn.cursor()
    sql = '''
      INSERT INTO tickets (
        ticket_id, issue_title, issue_description,
        priority, additional_details, screenshot,
        status, created_at, updated_at
      )
      VALUES (%s,%s,%s,%s,%s,%s,'Open',%s,%s)
    '''
    cur.execute(sql, (
      ticket_id, title, desc, prio,
      addl, screenshot,
      created_at, updated_at
    ))
    conn.commit()
    conn.close()

    return ticket_id

def get_ticket_status(ticket_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="Nunavath",
        password="Nithish@58525",
        database="support_system"
    )
    cur = conn.cursor()
    cur.execute("SELECT status FROM tickets WHERE ticket_id=%s",(ticket_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return f"Ticket ID: {ticket_id}\nStatus: {row[0]}"
    return None

def get_transaction_details(txn_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="kumar",
        password="kumar@58525",
        database="transaction_db"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions WHERE transaction_id=%s",(txn_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return (f"Transaction ID: {row[0]}\n"
                f"Sender: {row[1]}\n"
                f"Receiver: {row[2]}\n"
                f"Amount: {row[3]}\n"
                f"Date: {row[4]}\n"
                f"Status: {row[5]}")
    return None

# -----------------------
# 6) Flask Routes
# -----------------------
@app.route("/")
def route_index():
    return render_template("chat_index.html")

@app.route("/setup_database", methods=["GET"])
def route_setup():
    try:
        setup_database()
        return jsonify({"message":"DB setup done."})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/get_transaction", methods=["POST"])
def route_get_transaction():
    try:
        data = request.json
        txn_id = data.get("transaction_id","").strip()
        if not txn_id:
            return jsonify({"error":"Transaction ID is required."}),400
        details = get_transaction_details(txn_id)
        if details:
            return jsonify({"transaction_details": details})
        else:
            return jsonify({"message":"Transaction not found."})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/classify_error", methods=["POST"])
def route_classify_error():
    try:
        data = request.json
        err_msg = data.get("error","").strip()
        sess_id = data.get("session_id","default_err_sess")

        if not err_msg:
            return jsonify({"error":"Error message required."}),400

        raw = classify_error(err_msg, sess_id)
        classification = "UNKNOWN"
        solution = "No solution found."

        lines = raw.splitlines()
        for line in lines:
            if line.upper().startswith("CLASSIFICATION:"):
                classification = line.split(":",1)[1].strip().upper()
            elif line.upper().startswith("SOLUTION:"):
                solution = line.split(":",1)[1].strip()

        return jsonify({
            "classification": classification,
            "solution": solution
        })
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/raise_ticket", methods=["POST"])
def route_raise_ticket():
    try:
        title  = request.form.get("issue_title","No Title")
        desc   = request.form.get("issue_description","No Description")
        prio   = request.form.get("priority","Low").capitalize()
        addl   = request.form.get("additional_details","")

        if prio not in ["High","Medium","Low"]:
            return jsonify({"error":"Invalid priority. Use High, Medium, or Low."}),400

        screenshot_data = None
        if "screenshot" in request.files:
            fobj = request.files["screenshot"]
            if fobj:
                screenshot_data = fobj.read()

        tid = save_ticket(title, desc, prio, addl, screenshot_data)
        return jsonify({"message": f"Ticket created successfully. ID: {tid}"})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/ticket_status", methods=["POST"])
def route_ticket_status():
    try:
        data = request.json
        tid = data.get("ticket_id","").strip()
        if not tid:
            return jsonify({"error":"Ticket ID is required."}),400
        info = get_ticket_status(tid)
        if info:
            return jsonify({"ticket_info": info})
        else:
            return jsonify({"message":"Ticket not found."})
    except Exception as e:
        return jsonify({"error":str(e)}),500

@app.route("/ask_chatbot", methods=["POST"])
def route_ask_chatbot():
    try:
        data = request.json
        q = data.get("query","").strip()
        sess = data.get("session_id","default_chat_sess")
        if not q:
            return jsonify({"error":"Query is required."}),400

        answer = generate_response(q, sess)
        final_ans = add_website_link(answer, q)
        return jsonify({"response": final_ans})
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__=="__main__":
    app.run(debug=True)






