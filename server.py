from flask import Flask, request
from linkedin_post_utils import post_to_linkedin

app = Flask(__name__)

@app.route('/approve', methods=['GET'])
def approve_post():
    post_content = request.args.get("content")
    if post_content:
        post_to_linkedin(post_content)
        return "✅ LinkedIn post published!"
    return "❌ Missing content."

if __name__ == "__main__":
    app.run(port=5001, debug=True)
