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
    document_ids = []
    document_ids.append("1DOQ6at_Ge8-zPbicYCqxx7cS3_bA_8dC_SRulZ-3Qoo")
    document_ids.append("1yiZzJee9BW_HECceGlxDo6JDm0PPdO7CQ30Cak7H1Ro")
    names = []
    names.append("the equality pulse")
    names.append("The insane engineering of paragliding")
    for document_id, name in zip(document_ids, names):
        download_post(document_id, name)