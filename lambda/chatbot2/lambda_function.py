def lambda_handler(event, context):
    question = event.get("question", "No question provided")

    return {
        "statusCode": 200,
        "body": {
            "message": "Chatbot2 Lambda is working",
            "question": question
        }
    }
