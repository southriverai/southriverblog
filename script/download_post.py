import os
import requests

def download_post(document_id: str, name:str) -> str:
    url = f"https://docs.google.com/document/d/{document_id}/export?format=md"
    response = requests.get(url)
    if not os.path.exists("post_markdown"):
        os.makedirs("post_markdown")
    path_file = os.path.join("post_markdown", f"{name}.md")

    with open(path_file, "w") as f:
        f.write(response.text)

if __name__ == "__main__":
    document_id = "1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo"
    name = "the equality pulse"
    download_post(document_id, name)